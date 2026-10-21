"use client";

import Link from "next/link";
import {
  ShieldCheck,
  AlertTriangle,
  FileText,
  Download,
  CheckCircle2,
  ArrowRight,
  Stethoscope,
  Scale,
  Sparkles,
  Lock,
  ChevronRight,
  ExternalLink,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-sky-100 selection:text-sky-900">
      {/* 1. ВЕРХНЯЯ ПАНЕЛЬ НАВИГАЦИИ */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-sky-600 flex items-center justify-center text-white shadow-sm shadow-sky-200">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg tracking-tight text-slate-900 flex items-center gap-1.5">
                TenderMed
                <span className="text-[10px] font-semibold bg-sky-100 text-sky-800 px-1.5 py-0.5 rounded uppercase tracking-wider">
                  AI MedTech
                </span>
              </span>
              <span className="text-[11px] text-slate-500 -mt-1 font-medium">
                Аудит закупок медтехники 44-ФЗ
              </span>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-sky-600 transition-colors">
              Возможности
            </a>
            <a href="#risks" className="hover:text-sky-600 transition-colors">
              Стоп-факторы
            </a>
            <a href="#pricing" className="hover:text-sky-600 transition-colors">
              Тарифы
            </a>
            <a href="#compliance" className="hover:text-sky-600 transition-colors">
              152-ФЗ Защита
            </a>
            <a href="#faq" className="hover:text-sky-600 transition-colors">
              FAQ
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-slate-700 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors"
            >
              Войти
            </Link>
            <Link
              href="/register"
              className="text-sm font-semibold bg-sky-600 hover:bg-sky-700 text-white px-4 py-2 rounded-lg shadow-sm shadow-sky-200 transition-all flex items-center gap-1.5"
            >
              3 проверки бесплатно
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* 2. HERO СЕКЦИЯ */}
      <section className="relative pt-16 pb-20 md:pt-24 md:pb-28 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-sky-50 border border-sky-200/80 rounded-full px-4 py-1.5 text-xs font-semibold text-sky-800 mb-8 shadow-sm">
            <ShieldCheck className="w-4 h-4 text-sky-600" />
            <span>152-ФЗ Комплаенс • 44-ФЗ и 223-ФЗ • Защита от РНП и штрафов</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.15]">
            Экспертный ИИ-аудит тендеров медтехники{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-indigo-600">
              за 60 секунд
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto font-normal leading-relaxed">
            Автоматический поиск скрытых «заточек» под бренды, пресечение незаконных
            штрафов по ПП РФ № 1042 и нацрежима ПП 878. Генерация официальных запросов
            в Word (.docx) в 1 клик.
          </p>

          {/* CTA Кнопки */}
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto px-8 py-3.5 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl shadow-lg shadow-sky-200 transition-all flex items-center justify-center gap-2 text-base"
            >
              <Sparkles className="w-5 h-5" />
              Попробовать бесплатно (3 аудита)
            </Link>
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-xl border border-slate-300 shadow-sm transition-all flex items-center justify-center gap-2 text-base"
            >
              Демо-кабинет аудита
              <ChevronRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>

          {/* Преимущества в одну строку */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-y-2 gap-x-8 text-xs sm:text-sm font-medium text-slate-500">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Скачивание с ЕИС по прямой ссылке</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Официальные бланки в Word (.docx)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Без передачи перс. данных (152-ФЗ)</span>
            </div>
          </div>
        </div>

        {/* 3. ИНТЕРАКТИВНОЕ ПРЕВЬЮ РЕЗУЛЬТАТА АУДИТА */}
        <div className="max-w-5xl mx-auto px-4 mt-14">
          <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-200 overflow-hidden">
            {/* Имитация окна браузера */}
            <div className="bg-slate-100/80 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="text-xs font-mono text-slate-500 ml-2">
                  Извещение № 0859200001126012552 (Кардиостимуляторы имплантируемые)
                </span>
              </div>
              <span className="text-xs bg-red-100 text-red-700 font-semibold px-2 py-0.5 rounded">
                Светофор: Стоп-фактор 🔴
              </span>
            </div>

            {/* Содержимое превью карточки */}
            <div className="p-6 sm:p-8 text-left bg-gradient-to-b from-white to-slate-50">
              <div className="bg-red-500 text-white p-5 rounded-xl shadow-md shadow-red-200 mb-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-lg flex items-center gap-2">
                      <span>🔴</span> ВНИМАНИЕ: ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ ИЛИ ВКЛЮЧЕНИЯ В РНП
                    </h4>
                    <p className="text-sm text-red-100 mt-1">
                      Индекс риска: <b>85 / 100</b> • Обнаружены штрафы 10% вместо 5% по ПП 1042,
                      срок поставки 5 дней и скрытая заточка под электрокардиостимуляторы Medtronic.
                    </p>
                  </div>
                </div>
              </div>

              {/* Метрики контракта */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">НМЦК закупки</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">8 321 000 ₽</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Срок поставки</div>
                  <div className="text-base font-bold text-red-600 mt-0.5">5 календарных дней</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Штраф за факт</div>
                  <div className="text-base font-bold text-red-600 mt-0.5">10% (незаконно)</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Готовые запросы в ЕИС</div>
                  <div className="text-base font-bold text-sky-600 mt-0.5">3 письма в Word</div>
                </div>
              </div>

              {/* Образец запроса в Word */}
              <div className="border border-sky-200 bg-sky-50/50 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-sky-600 flex items-center justify-center text-white shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-semibold text-sm text-slate-900">
                      Официальный запрос на разъяснение № 1 (ПП 1042)
                    </div>
                    <div className="text-xs text-slate-500">
                      С шапкой Заказчика, статьями 33, 34 44-ФЗ и требованием снижения штрафа
                    </div>
                  </div>
                </div>
                <Link
                  href="/register"
                  className="w-full sm:w-auto shrink-0 bg-white hover:bg-slate-100 text-sky-700 font-semibold px-4 py-2 rounded-lg text-xs border border-sky-300 flex items-center justify-center gap-1.5 shadow-sm"
                >
                  <Download className="w-3.5 h-3.5" />
                  Скачать образец в Word (.docx)
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. СЕКЦИЯ: 4 ГЛАВНЫХ РИСКА В МЕДТЕХНИКЕ */}
      <section id="risks" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 tracking-wider uppercase">
              С какими ловушками борется TenderMed
            </h2>
            <p className="mt-2 text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Ошибки в тендерах медтехники стоят десятков миллионов
            </p>
            <p className="mt-4 text-base text-slate-600">
              Госзаказчики часто составляют документацию под «своего» поставщика или
              перестраховываются кабальными пунктами, которые ведут прямо в РНП.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-sky-300 transition-all">
              <div className="w-10 h-10 rounded-xl bg-red-100 text-red-600 flex items-center justify-center mb-4">
                <Scale className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">Незаконные штрафы</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Заказчик прописывает штраф 10% вместо положенных 5% по ПП РФ № 1042 при цене
                от 3 до 50 млн ₽. ИИ выявляет расхождение и готовит запрос на изменение.
              </p>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-sky-300 transition-all">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-600 flex items-center justify-center mb-4">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">Скрытые заточки</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Диапазон веса до грамма, габариты в миллиметрах или запатентованные алгоритмы
                зонного сканирования (Mindray/GE), исключающие аналоги.
              </p>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-sky-300 transition-all">
              <div className="w-10 h-10 rounded-xl bg-sky-100 text-sky-600 flex items-center justify-center mb-4">
                <Stethoscope className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">Нацрежим и РУ</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Ограничения по ПП РФ № 878 (радиоэлектроника), правило «третий лишний» и скрытые
                требования к комплектации по РУ Росздравнадзора.
              </p>
            </div>

            <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 hover:border-sky-300 transition-all">
              <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-4">
                <Lock className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">Кабальные сроки</h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Поставка сложного КТ/МРТ за 5 дней по разовой заявке. Поставщик физически не успевает
                привезти технику и попадает на расторжение и РНП.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. СЕКЦИЯ: 152-ФЗ БЕЗОПАСНОСТЬ */}
      <section id="compliance" className="py-20 bg-slate-100 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-3xl p-8 sm:p-12 border border-slate-200 shadow-sm flex flex-col lg:flex-row items-center gap-10">
            <div className="lg:w-1/2">
              <div className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold px-3 py-1 rounded-full mb-4">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                Юридическая чистота и конфиденциальность
              </div>
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-4">
                Полное соответствие закону о персональных данных (152-ФЗ)
              </h2>
              <p className="text-slate-600 text-sm sm:text-base leading-relaxed mb-6">
                Документация на ЕИС открыта в силу ст. 7 44-ФЗ. При этом TenderMed оборудован
                встроенным <b>микро-анонимизатором</b>: перед отправкой в нейросеть телефоны,
                e-mail, СНИЛС и паспорта физических лиц автоматически маскируются.
              </p>
              <div className="space-y-3 text-sm text-slate-700">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Работа в оперативной памяти (in-memory) без сохранения на диск</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Сохранение ИНН юрлиц Заказчика для официальных бланков</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Поддержка российских SSL-сертификатов Национального УЦ (Минцифры)</span>
                </div>
              </div>
            </div>

            <div className="lg:w-1/2 bg-slate-50 p-6 rounded-2xl border border-slate-200 w-full">
              <div className="text-xs font-mono text-slate-500 mb-2">Лог микро-анонимизатора 152-ФЗ:</div>
              <div className="bg-slate-900 text-emerald-400 p-4 rounded-xl font-mono text-xs leading-relaxed overflow-x-auto shadow-inner">
                <div className="text-slate-500">// Входящий фрагмент контракта:</div>
                <div className="line-through text-red-400 opacity-70">
                  Контактное лицо: Иванов И.И., +7 (916) 123-45-67, email: doc@samara.ru
                </div>
                <div className="text-slate-500 mt-2">// После фильтрации TenderMed:</div>
                <div className="text-emerald-300 font-semibold">
                  Контактное лицо: Иванов И.И., [ТЕЛЕФОН_СКРЫТ], email: [EMAIL_СКРЫТ]
                </div>
                <div className="text-sky-400 mt-2">✓ 0 персональных данных передано внешним API</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 6. СЕКЦИЯ: ТАРИФЫ И МОНЕТИЗАЦИЯ */}
      <section id="pricing" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 tracking-wider uppercase">Тарифные планы</h2>
            <p className="mt-2 text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              Инвестируйте в безопасность ваших тендеров
            </p>
            <p className="mt-4 text-base text-slate-600">
              Один предотвращенный штраф окупает подписку на 5 лет вперед.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
            {/* Тариф 1: Старт */}
            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-900">Тестовый старт</h3>
                <p className="text-sm text-slate-500 mt-1">Оцените точность ИИ на ваших закупках</p>
                <div className="mt-6 mb-6">
                  <span className="text-4xl font-extrabold text-slate-900">0 ₽</span>
                  <span className="text-sm text-slate-500 ml-2">навсегда</span>
                </div>
                <ul className="space-y-3 text-sm text-slate-600 mb-8">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span><b>3 полных аудита</b> при регистрации</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Скачивание с zakupki.gov.ru по URL</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Светофор рисков и проверка штрафов</span>
                  </li>
                  <li className="flex items-center gap-2 text-slate-400">
                    <span>— Выгрузка официальных Word-писем</span>
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="w-full py-3 bg-white hover:bg-slate-100 text-slate-800 font-semibold rounded-xl border border-slate-300 text-center text-sm shadow-sm transition-all"
              >
                Попробовать бесплатно
              </Link>
            </div>

            {/* Тариф 2: Специалист (Популярный) */}
            <div className="bg-white rounded-2xl p-8 border-2 border-sky-600 shadow-xl shadow-sky-100 flex flex-col justify-between relative">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-sky-600 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                Выбор поставщиков
              </div>
              <div>
                <h3 className="font-bold text-lg text-slate-900">Специалист</h3>
                <p className="text-sm text-slate-500 mt-1">Для тендерных специалистов и юристов</p>
                <div className="mt-6 mb-6">
                  <span className="text-4xl font-extrabold text-slate-900">14 900 ₽</span>
                  <span className="text-sm text-slate-500 ml-2">/ месяц</span>
                </div>
                <ul className="space-y-3 text-sm text-slate-600 mb-8">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-600" />
                    <span><b>30 полных аудитов</b> в месяц</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-600" />
                    <span><b>Скачивание запросов в Word (.docx)</b></span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-600" />
                    <span>Детекция брендовых заточек (Mindray/GE)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-600" />
                    <span>Проверка РУ и ограничений ПП 878</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-sky-600" />
                    <span>Флагманская модель <b>GPT-5.4</b></span>
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="w-full py-3 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl text-center text-sm shadow-md shadow-sky-200 transition-all"
              >
                Подключить тариф
              </Link>
            </div>

            {/* Тариф 3: Тендерный отдел */}
            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200 flex flex-col justify-between">
              <div>
                <h3 className="font-bold text-lg text-slate-900">Тендерный отдел</h3>
                <p className="text-sm text-slate-500 mt-1">Для дистрибьюторов и производителей</p>
                <div className="mt-6 mb-6">
                  <span className="text-4xl font-extrabold text-slate-900">34 900 ₽</span>
                  <span className="text-sm text-slate-500 ml-2">/ месяц</span>
                </div>
                <ul className="space-y-3 text-sm text-slate-600 mb-8">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span><b>150 аудитов</b> в месяц (до 5 рабочих мест)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Генерация <b>Формы 2 (конкретные показатели)</b></span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Проекты жалоб в УФАС</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Выгрузка всех отчетов в DOCX и Markdown</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    <span>Персональный аккаунт-менеджер и SLA</span>
                  </li>
                </ul>
              </div>
              <Link
                href="/register"
                className="w-full py-3 bg-white hover:bg-slate-100 text-slate-800 font-semibold rounded-xl border border-slate-300 text-center text-sm shadow-sm transition-all"
              >
                Подключить для отдела
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 7. СЕКЦИЯ FAQ */}
      <section id="faq" className="py-20 bg-slate-50 border-t border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-xs font-bold text-sky-600 tracking-wider uppercase">Вопросы и ответы</h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 tracking-tight">
              Часто задаваемые вопросы
            </p>
          </div>

          <div className="space-y-4">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                Законно ли скачивать документы закупок с ЕИС?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Да, абсолютно. В силу ст. 7 Федерального закона № 44-ФЗ и ст. 7–8 закона № 149-ФЗ
                вся документация на `zakupki.gov.ru` является общедоступной публичной информацией.
                Кроме того, перед обработкой наш микро-анонимизатор удаляет все телефоны и персональные данные по 152-ФЗ.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                Как сервис находит скрытые «заточки» под бренды?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                ИИ обучен на реестрах медицинских изделий Росздравнадзора и паспортах оборудования.
                Он сопоставляет параметры ТЗ с базой характеристик (Mindray, GE Healthcare, Philips,
                Medtronic, Abbott, Siemens) и выявляет комбинации требований, которые физически
                совпадают только с одной конкретной моделью.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                В каком виде формируются запросы к Заказчику?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Вы получаете файл Microsoft Word (.docx), оформленный по всем правилам делопроизводства:
                с шапкой учреждения, ФИО руководителя, исходящим номером, мотивировочной частью (ссылки на ст. 33,
                34 44-ФЗ, ПП 1042) и четкой просительной частью. Письмо готово к прикреплению на ЭТП.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 8. ПОДВАЛ */}
      <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800 text-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5 text-white">
            <div className="w-7 h-7 rounded-lg bg-sky-600 flex items-center justify-center text-white">
              <Stethoscope className="w-4 h-4" />
            </div>
            <span className="font-bold text-base">TenderMed</span>
            <span className="text-xs text-slate-500">© 2026. Все права защищены.</span>
          </div>

          <div className="flex flex-wrap items-center gap-6 text-xs text-slate-400">
            <a href="#compliance" className="hover:text-white transition-colors">
              Политика 152-ФЗ
            </a>
            <a href="#risks" className="hover:text-white transition-colors">
              Нормативная база (44-ФЗ, ПП 1042)
            </a>
            <Link href="/login" className="hover:text-white transition-colors">
              Вход для клиентов
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
