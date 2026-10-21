# Дизайн-документ: SaaS-платформа TenderMed (FastAPI + Next.js)

**Дата:** 21 октября 2026 г.  
**Проект:** TenderMed (ИИ-аудит тендеров сложной медтехники)  
**Репозиторий:** `https://github.com/drundul/tendermed`  

---

## 1. Контекст и цели проекта

TenderMed решает критическую проблему поставщиков медицинского оборудования по 44-ФЗ и 223-ФЗ:
* Исключение штрафов выше нормативов ПП РФ № 1042
* Проверка нацрежима (ПП РФ № 878) и требований к РУ Росздравнадзора
* Выявление скрытых технических «заточек» под бренды
* Автоматическая подготовка юридически грамотных официальных писем-запросов на разъяснение в формате Word (.docx)
* Полный комплаенс с 152-ФЗ («О персональных данных»)

**Цель:** Перевести существующий прототип на архитектуру коммерческого масштабируемого SaaS:
1. **Бэкенд:** FastAPI REST API с базой данных (SQLite/PostgreSQL), аутентификацией (JWT) и лимитами проверок.
2. **Фронтенд:** Next.js 15 + TypeScript + Tailwind CSS (продающий маркетинговый лендинг + авторизованный личный кабинет).

---

## 2. Архитектура монорепозитория

```text
tendermed/
├── backend/
│   ├── app/
│   │   ├── api/                 # Роутеры FastAPI
│   │   │   ├── auth.py          # /api/auth: регистрация, логин, профиль
│   │   │   ├── tenders.py       # /api/tenders: аудит по URL, аудит по файлам, история
│   │   │   └── exports.py       # /api/exports: скачивание DOCX/Markdown
│   │   ├── core/
│   │   │   ├── config.py        # Настройки окружения (Pydantic Settings)
│   │   │   ├── security.py      # Хэширование bcrypt + JWT генерация
│   │   │   └── database.py      # SQLAlchemy сессия
│   │   ├── db/
│   │   │   └── models.py        # User, TenderAudit, AuditCredit
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic DTO (запросы, ответы, FullAnalysisReport)
│   │   ├── services/            # Аналитическое ядро
│   │   │   ├── eis_scraper.py   # Парсинг zakupki.gov.ru
│   │   │   ├── anonymizer.py    # 152-ФЗ микро-анонимизатор
│   │   │   ├── extractor.py     # DOCX, PDF, ZIP парсер
│   │   │   ├── classifier.py    # Классификатор ТЗ / Контракт / Инфокарта
│   │   │   ├── llm_service.py   # OpenAI Structured Outputs
│   │   │   ├── prompts.py       # Медицинские юридические промпты
│   │   │   └── analyzer.py      # Оркестратор анализа
│   │   └── utils/
│   │       └── export.py        # Генераторы DOCX (отчет, запросы) и MD
│   ├── tests/                   # Pytest suite
│   ├── requirements.txt
│   └── main.py                  # Точка входа FastAPI
├── frontend/                    # Next.js 15 App Router
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Главная: продающий лендинг + калькулятор рисков + тарифы
│   │   │   ├── login/page.tsx   # Страница входа
│   │   │   ├── register/page.tsx # Страница регистрации (3 бесплатных аудита)
│   │   │   └── dashboard/       # Личный кабинет тендерного специалиста
│   │   ├── components/          # UI-компоненты (TrafficLight, RiskCard, DocxButton)
│   │   └── lib/                 # API клиент (Fetch c Bearer токеном)
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docker-compose.yml           # Запуск единым контейнером
└── README.md
```

---

## 3. Схема данных (База данных)

### Таблица `users`:
* `id` (Integer / UUID, PK)
* `email` (String, unique, indexed)
* `hashed_password` (String)
* `company_name` (String, nullable)
* `available_credits` (Integer, default=3) — баланс аудитов
* `is_active` (Boolean, default=True)
* `created_at` (DateTime)

### Таблица `tender_audits`:
* `id` (Integer / UUID, PK)
* `user_id` (FK -> users.id)
* `source_url` (String, nullable)
* `notice_number` (String, nullable)
* `purchase_subject` (String)
* `customer_name` (String, nullable)
* `verdict` (String: RED, YELLOW, GREEN)
* `risk_score` (Integer: 0..100)
* `report_json` (JSON / Text) — полный отчет FullAnalysisReport
* `created_at` (DateTime)

---

## 4. Спецификация API (FastAPI)

1. **Аутентификация (`/api/auth`)**:
   * `POST /api/auth/register` $\rightarrow$ `{email, password, company_name}` $\rightarrow$ JWT + 3 бесплатных аудита
   * `POST /api/auth/login` $\rightarrow$ `{email, password}` $\rightarrow$ JWT
   * `GET /api/auth/me` $\rightarrow$ текущий баланс, профиль, лимиты

2. **Анализ закупок (`/api/tenders`)**:
   * `POST /api/tenders/analyze-url` $\rightarrow$ `{url: str, model: Optional[str]}` $\rightarrow$ парсинг ЕИС, списание 1 кредита, возврат `FullAnalysisReport`
   * `POST /api/tenders/analyze-files` $\rightarrow$ `Multipart files` $\rightarrow$ анализ файлов, списание 1 кредита, возврат `FullAnalysisReport`
   * `GET /api/tenders/history` $\rightarrow$ список ранее проверенных закупок пользователя
   * `GET /api/tenders/{id}` $\rightarrow$ детальный результат закупки

3. **Экспорт документов (`/api/exports`)**:
   * `GET /api/exports/tenders/{id}/report.docx` $\rightarrow$ файл аудиторского заключения в Word
   * `GET /api/exports/tenders/{id}/clarifications.docx` $\rightarrow$ файл всех запросов в Word
   * `GET /api/exports/tenders/{id}/clarification/{index}.docx` $\rightarrow$ конкретный запрос в Word

---

## 5. Монетизация и тарифные лимиты
* При регистрации каждый пользователь получает **3 бесплатных аудита** для оценки качества.
* После исчерпания кредитов пользователь видит предложение подключить тариф («Специалист» 14 900 ₽/мес или «Тендерный отдел» 34 900 ₽/мес).
