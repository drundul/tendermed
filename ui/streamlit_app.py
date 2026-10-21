import os
import sys

# Гарантируем корректный импорт модулей app независимо от того, как запущен Streamlit
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

# Настройка страницы
st.set_page_config(
    page_title="TenderAI Med — Аудит тендеров медтехники",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.config import settings
from app.models.schemas import TrafficLightVerdict, RiskSeverity, RiskCategory
from app.services.analyzer import TenderAnalyzerPipeline
from app.services.eis_scraper import EISScraper
from app.utils.export import ReportExporter


# Стилизация интерфейса
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #e9ecef;
        margin-bottom: 12px;
    }
    .verdict-banner-red {
        background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(255, 77, 79, 0.25);
    }
    .verdict-banner-yellow {
        background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(250, 173, 20, 0.25);
    }
    .verdict-banner-green {
        background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(82, 196, 26, 0.25);
    }
    .risk-card-high {
        border-left: 5px solid #ff4d4f;
        background-color: #fff1f0;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 14px;
    }
    .risk-card-medium {
        border-left: 5px solid #faad14;
        background-color: #fffbe6;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 14px;
    }
    .risk-card-low {
        border-left: 5px solid #52c41a;
        background-color: #f6ffed;
        padding: 16px;
        border-radius: 6px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = 0


init_session_state()

# ----------------- БОКОВАЯ ПАНЕЛЬ -----------------
with st.sidebar:
    st.title("🏥 TenderAI Med")
    st.caption("ИИ-аудит тендеров медицинского оборудования (44-ФЗ / 223-ФЗ)")
    st.divider()

    st.subheader("⚙️ Настройки ИИ")
    
    # Ключ OpenAI
    env_key = settings.openai_api_key or ""
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=env_key if env_key != "your_openai_api_key_here" else "",
        type="password",
        help="Введите ваш ключ OpenAI (начинается с sk-...)",
    )
    if api_key_input.strip():
        st.caption("🟢 API-ключ указан")
    else:
        st.caption("⚪ Ключ не указан (доступен Демо-режим)")

    # Базовый URL (прокси / зеркало)
    env_url = settings.openai_base_url or ""
    base_url_input = st.text_input(
        "Base URL (опционально для прокси)",
        value=env_url,
        placeholder="https://api.openai.com/v1",
        help="Укажите, если используете прокси или зеркало (напр. https://api.proxyapi.ru/openai/v1 или https://openrouter.ai/api/v1)",
    )

    # Выбор модели
    available_models = [
        "gpt-5.4-mini",
        "gpt-5.4",
        "gpt-5.2",
        "gpt-5-mini",
        "gpt-4.1-mini",
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini",
        "o3-mini",
        "o4-mini",
        "Ввести модель вручную...",
    ]
    model_choice = st.selectbox(
        "Аналитическая модель",
        options=available_models,
        index=0,
        help="gpt-5.4-mini — идеальна по умолчанию (быстрая, точная, квота 2.5 млн токенов/день). gpt-5.4 и gpt-5.2 — флагманский глубокий анализ.",
    )
    if model_choice == "Ввести модель вручную...":
        selected_model = st.text_input("Название модели", value="gpt-5.4-mini")
    else:
        selected_model = model_choice

    # Демо-режим
    demo_mode = st.toggle(
        "🧪 Демо-режим (Mock)",
        value=not bool(api_key_input.strip()),
        help="Включение показа эталонного отчета по закупке УЗИ-аппарата без обращения к внешним API.",
    )

    if demo_mode:
        st.info("ℹ️ **Режим:** ДЕМО (работает на эталонных данных, токены не расходуются)")
    else:
        if api_key_input.strip():
            st.success(f"🤖 **Режим:** ЖИВОЙ ИИ (модель: `{selected_model}`)")
        else:
            st.warning("⚠️ Для отключения демо-режима введите OpenAI API Key выше!")

    st.divider()
    st.subheader("📚 Нормативная база")
    st.markdown("""
    - **44-ФЗ ст. 33:** Правила описания объекта закупки
    - **ПП РФ № 1042:** Предельные размеры штрафов и пеней
    - **ПП РФ № 878:** Ограничения допуска иностранной радиоэлектроники
    - **135-ФЗ ст. 17:** Запрет ограничения конкуренции заказчиками
    """)
    st.caption("v1.0.0 MVP • Ниша: Медоборудование")


# ----------------- ГЛАВНЫЙ ЭКРАН -----------------
st.title("Экспертный ИИ-анализ тендерной документации")
st.markdown(
    "Загрузите документацию закупки на поставку сложной медтехники (УЗИ, МРТ, КТ, ИВЛ). "
    "ИИ за 60 секунд выявит скрытые ловушки контракта, проверит требования к РУ и нацрежиму (ПП 878) "
    "и подготовит черновик запроса на разъяснение."
)

col_upload, col_demo = st.columns([3, 1])

with col_upload:
    uploaded_files = st.file_uploader(
        "Перетащите файлы закупки (.zip архив или сразу несколько файлов .docx / .pdf)",
        type=["zip", "pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Вы можете выбрать сразу несколько файлов с сайта (ТЗ, проект контракта, инфокарту) или один ZIP-архив.",
    )
    if uploaded_files:
        st.caption(f"📁 Выбрано файлов: {len(uploaded_files)} ({', '.join(f.name for f in uploaded_files[:3])}{'...' if len(uploaded_files) > 3 else ''})")

with col_demo:
    st.markdown("<br>", unsafe_allow_html=True)
    load_sample_btn = st.button("⚡ Загрузить эталон (УЗИ Resona 7)", use_container_width=True)

# --- БЛОК: Автоскачивание по ссылке ЕИС ---
st.markdown("---")
st.markdown("#### 🌐 Или вставьте ссылку на закупку с zakupki.gov.ru")
st.caption(
    "Система автоматически найдёт страницу «Документы», скачает прикреплённые файлы "
    "(Обоснование НМЦК, Проект контракта, ТЗ, Инфокарту) и запустит ИИ-анализ."
)
col_url, col_fetch = st.columns([4, 1])
with col_url:
    eis_url_input = st.text_input(
        "Ссылка на закупку ЕИС",
        placeholder="https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=...",
        label_visibility="collapsed",
    )
with col_fetch:
    fetch_btn = st.button("📥 Скачать и анализировать", use_container_width=True, type="primary")

st.markdown("---")

# Инициализация пайплайна с переданными ключами
clean_key = api_key_input.strip() if api_key_input else None
clean_url = base_url_input.strip() if base_url_input else None
pipeline = TenderAnalyzerPipeline(api_key=clean_key, base_url=clean_url)

if load_sample_btn:
    sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_med_tender.md")
    sample_bytes = b""
    if os.path.exists(sample_path):
        with open(sample_path, "rb") as f:
            sample_bytes = f.read()
    else:
        sample_bytes = "Техническое задание на поставку УЗИ системы".encode("utf-8")

    action_label = "Демонстрационный разбор эталона..." if demo_mode else f"Живой анализ эталона через OpenAI ({selected_model})..."
    with st.spinner(action_label):
        try:
            result = pipeline.process_file_bytes(
                filename="Эталон_Закупка_УЗИ_44ФЗ.md",
                file_bytes=sample_bytes,
                model_name=selected_model,
                force_mock=demo_mode,
            )
            st.session_state.analysis_result = result
            if demo_mode:
                st.success("Эталонный комплект документации успешно загружен в Демо-режиме!")
            else:
                st.success(f"Живой анализ успешно выполнен моделью {selected_model} за {result.execution_time_seconds} с!")
        except Exception as err:
            st.error(f"❌ Не удалось выполнить живой запрос к OpenAI: {str(err)}")
            st.info("💡 Рекомендация: Проверьте валидность API-ключа, наличие VPN/прокси (если запрос блокируется по региону) или выберите другую модель.")

elif fetch_btn and eis_url_input.strip():
    # --- Автоматическое скачивание документов по ссылке ЕИС ---
    url_to_fetch = eis_url_input.strip()
    with st.status("🌐 Скачиваем документы с портала ЕИС zakupki.gov.ru...", expanded=True) as fetch_status:
        try:
            st.write("🔗 Анализируем ссылку и определяем тип закупки...")
            eis_files, reg_number = EISScraper.fetch_documents(url_to_fetch)

            if not eis_files:
                fetch_status.update(label="❌ Файлы не найдены", state="error")
                st.error(
                    f"На портале ЕИС не найдены прикреплённые файлы для закупки №{reg_number}. "
                    "Возможно, закупка ещё не размещена или документы опубликованы в нестандартном формате."
                )
                st.info("💡 Попробуйте скачать файлы вручную и загрузить через кнопку выше.")
            else:
                file_names = ", ".join(name for name, _ in eis_files[:4])
                st.write(f"📂 Найдено файлов: **{len(eis_files)}** → {file_names}{'...' if len(eis_files) > 4 else ''}")
                st.write("📑 Классификация документов (ТЗ / Проект контракта / Информационная карта)...")
                st.write("⚖️ Юридический аудит штрафов и неустоек (ПП РФ № 1042)...")
                st.write("🩺 Проверка медицинского комплаенса (РУ Росздравнадзора, ПП РФ № 878, КТРУ)...")
                st.write("🔍 Поиск признаков ограничения конкуренции («заточек» под бренд)...")

                result = pipeline.process_files(
                    files=eis_files,
                    model_name=selected_model,
                    force_mock=demo_mode,
                )
                st.session_state.analysis_result = result
                fetch_status.update(
                    label=f"✅ Анализ закупки №{reg_number} завершён!",
                    state="complete",
                    expanded=False,
                )
                st.success(
                    f"Анализ завершён за **{result.execution_time_seconds} сек**. "
                    f"Обработано **{result.total_documents}** документов ({result.total_characters} символов)."
                )
        except ValueError as ve:
            fetch_status.update(label="❌ Ошибка URL", state="error")
            st.error(f"❌ Некорректная ссылка: {str(ve)}")
        except RuntimeError as re_err:
            fetch_status.update(label="❌ Документы не найдены", state="error")
            st.error(f"❌ {str(re_err)}")
            st.info("💡 Попробуйте скопировать ссылку прямо на вкладку «Документы» закупки.")
        except Exception as err:
            fetch_status.update(label="❌ Ошибка", state="error")
            st.error(f"❌ Неожиданная ошибка при скачивании: {str(err)}")

elif uploaded_files:
    analyze_btn = st.button("🚀 Начать ИИ-экспертизу закупки", type="primary", use_container_width=True)
    if analyze_btn:
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            with st.status("Выполняется многоуровневый анализ документации...", expanded=True) as status:
                st.write(f"📦 Чтение и распаковка {len(uploaded_files)} файлов...")
                files_payload = [(f.name, f.getvalue()) for f in uploaded_files]

                st.write("📑 Классификация документов (ТЗ / Проект контракта / Информационная карта)...")
                st.write("⚖️ Юридический аудит штрафов и неустоек (ПП РФ № 1042)...")
                st.write("🩺 Проверка медицинского комплаенса (РУ Росздравнадзора, ПП РФ № 878, КТРУ)...")
                st.write("🔍 Поиск признаков ограничения конкуренции («заточек» под бренд)...")

                try:
                    result = pipeline.process_files(
                        files=files_payload,
                        model_name=selected_model,
                        force_mock=demo_mode,
                    )
                    st.session_state.analysis_result = result
                    status.update(label="Анализ успешно завершен!", state="complete", expanded=False)
                    st.success(f"Анализ завершен за {result.execution_time_seconds} сек. Обработано {result.total_documents} документов ({result.total_characters} символов).")
                except Exception as err:
                    status.update(label="Ошибка анализа!", state="error", expanded=True)
                    st.error(f"❌ Ошибка вызова OpenAI API: {str(err)}")
                    st.info("💡 Подсказка: Проверьте правильность API-ключа или включите 'Демо-режим' в боковой панели слева.")


# ----------------- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ -----------------
res = st.session_state.analysis_result

if res:
    report = res.report

    st.markdown("---")

    # 1. ГЛАВНЫЙ СВЕТОФОР (БАННЕР ВЕРДИКТА)
    if report.verdict == TrafficLightVerdict.RED:
        banner_class = "verdict-banner-red"
        icon = "🔴"
        title = "СТОП-ФАКТОРЫ: ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ ИЛИ ВКЛЮЧЕНИЯ В РНП"
    elif report.verdict == TrafficLightVerdict.YELLOW:
        banner_class = "verdict-banner-yellow"
        icon = "🟡"
        title = "ВНИМАНИЕ: ТРЕБУЕТСЯ ЗАПРОС РАЗЪЯСНЕНИЙ ИЛИ ОСТОРОЖНОСТЬ"
    else:
        banner_class = "verdict-banner-green"
        icon = "🟢"
        title = "РЕКОМЕНДОВАНО К УЧАСТИЮ (РИСКИ В ПРЕДЕЛАХ НОРМЫ)"

    st.markdown(f"""
    <div class="{banner_class}">
        <h2 style="margin: 0 0 8px 0; color: white;">{icon} {title}</h2>
        <p style="font-size: 16px; margin: 0; line-height: 1.5; color: white;"><b>Индекс риска:</b> {report.risk_score} / 100</p>
        <p style="font-size: 16px; margin: 8px 0 0 0; line-height: 1.5; color: white;"><b>Резюме для руководителя:</b> {report.verdict_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    if getattr(report, "is_mock", False) or "демо" in (report.model_used or "").lower():
        st.info("🧪 **Источник анализа:** ДЕМО-ОБРАЗЕЦ (без списания токенов OpenAI)")
    else:
        st.success(f"🤖 **Источник анализа:** ЖИВОЙ ИИ-АНАЛИЗ • Модель: `{report.model_used}` • Время: `{res.execution_time_seconds} сек`")

    # 2. ПАРАМЕТРЫ КОНТРАКТА (МЕТРИКИ)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        nmck_str = f"{report.summary.nmck_rubles:,.0f} ₽".replace(",", " ") if report.summary.nmck_rubles else "Не указана"
        st.metric("НМЦК закупки", nmck_str)
    with m2:
        st.metric("Срок поставки", report.summary.delivery_deadline or "По графику")
    with m3:
        adv_str = f"{report.summary.advance_percent}%" if report.summary.advance_percent else "Без аванса"
        st.metric("Авансирование", adv_str)
    with m4:
        guar_str = f"{report.summary.contract_guarantee_percent}%" if report.summary.contract_guarantee_percent else "Не установлено"
        st.metric("Обеспечение контракта", guar_str)

    # 2.1. ЮРИДИЧЕСКИЕ РЕКВИЗИТЫ ЗАКАЗЧИКА И ПРОЦЕДУРЫ
    with st.expander("🏛️ Юридические реквизиты Заказчика и процедуры", expanded=True):
        c_r1, c_r2 = st.columns(2)
        with c_r1:
            st.markdown(f"**Заказчик:** {report.summary.customer_name or 'Уточняется в контракте'}")
            if report.summary.customer_signer:
                st.markdown(f"**В лице:** {report.summary.customer_signer}")
            if report.summary.customer_inn:
                st.markdown(f"**ИНН / КПП:** `{report.summary.customer_inn}` / `{report.summary.customer_kpp or 'Н/Д'}`")
            st.markdown(f"**Адрес / Место поставки:** {report.summary.customer_address or report.summary.delivery_place or 'Не указан'}")
        with c_r2:
            st.markdown(f"**Номер извещения:** `{report.summary.notice_number or 'По документации'}`")
            if report.summary.ikz:
                st.markdown(f"**ИКЗ:** `{report.summary.ikz}`")
            if report.summary.etp_name:
                st.markdown(f"**Электронная площадка (ЭТП):** {report.summary.etp_name}")
            st.markdown(f"**Законодательство:** {report.summary.law_type}")

    # 3. ВКЛАДКИ ДЕТАЛЬНОГО АНАЛИЗА
    tab_risks, tab_med, tab_eq, tab_inquiry, tab_export = st.tabs([
        f"🚨 Матрица рисков ({len(report.risks)})",
        "🩺 Медицинский комплаенс",
        f"🔬 Спецификация и заточки ({len(report.equipment)})",
        f"📝 Официальные запросы в ЕИС ({len(report.clarification_requests)})",
        "💾 Экспорт отчета",
    ])

    # Вкладка 1: Матрица рисков
    with tab_risks:
        st.subheader("Выявленные угрозы и несоответствия")
        
        severity_filter = st.radio(
            "Фильтр по критичности:",
            options=["Все риски", "Только критические 🔴", "Умеренные 🟡"],
            horizontal=True,
        )

        filtered_risks = report.risks
        if severity_filter == "Только критические 🔴":
            filtered_risks = [r for r in report.risks if r.severity == RiskSeverity.HIGH]
        elif severity_filter == "Умеренные 🟡":
            filtered_risks = [r for r in report.risks if r.severity == RiskSeverity.MEDIUM]

        if not filtered_risks:
            st.info("В выбранной категории рисков не обнаружено.")
        else:
            for idx, risk in enumerate(filtered_risks, 1):
                card_class = (
                    "risk-card-high" if risk.severity == RiskSeverity.HIGH
                    else "risk-card-medium" if risk.severity == RiskSeverity.MEDIUM
                    else "risk-card-low"
                )
                sev_badge = "🔴 Высокий риск" if risk.severity == RiskSeverity.HIGH else "🟡 Внимание"
                
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <h4 style="margin: 0; color: #262626;">{idx}. {risk.title}</h4>
                        <span style="font-weight: bold; font-size: 13px;">{sev_badge} • {risk.category.value}</span>
                    </div>
                    <p style="margin: 4px 0 8px 0; color: #595959;">{risk.description}</p>
                </div>
                """, unsafe_allow_html=True)

                if risk.quote:
                    st.caption(f"📌 **Цитата из документа:** *«{risk.quote}»*")
                if risk.law_reference:
                    st.caption(f"⚖️ **Нарушение норм:** `{risk.law_reference}`")
                
                st.success(f"💡 **Рекомендация поставщику:** {risk.recommendation}")
                st.markdown("<br>", unsafe_allow_html=True)

    # Вкладка 2: Медицинский комплаенс
    with tab_med:
        st.subheader("Проверка специфических медицинских и нормативных требований")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 📋 Регистрационное удостоверение (РУ)")
            if report.med_compliance.ru_required:
                st.warning("⚠️ **Требуется РУ Росздравнадзора.**")
            else:
                st.info("ℹ️ РУ прямо не затребовано.")
            st.write(report.med_compliance.ru_notes)

            st.markdown("#### 🇷🇺 Национальный режим (ПП РФ № 878 / ст. 14)")
            if report.med_compliance.national_regime_applies:
                st.error("🚨 **Применяется Постановление Правительства РФ № 878.** Действует правило 'третий лишний'!")
            else:
                st.success("✅ Ограничения по ПП РФ № 878 не установлены.")
            st.write(report.med_compliance.national_regime_details)

        with col_c2:
            st.markdown("#### 🏷️ Каталог товаров, работ, услуг (КТРУ)")
            if report.med_compliance.ktru_used:
                st.success(f"✅ Использована позиция КТРУ: `{report.med_compliance.ktru_code or 'Да'}`")
            else:
                st.warning("⚠️ КТРУ не использован (описание в свободной форме заказчика).")

            st.markdown("#### 🛠️ Сервисные обязательства и персонал")
            st.write(f"- **Монтаж, пусконаладка и инструктаж:** {'Да' if report.med_compliance.installation_and_training else 'Нет'}")
            st.write(f"- **Гарантийный срок:** {report.med_compliance.warranty_period_months or 'Не указан'} мес.")

    # Вкладка 3: Спецификация оборудования и заточки
    with tab_eq:
        st.subheader("Анализ позиций оборудования и детекция скрытых заточек")
        st.caption("ИИ выявляет узкие диапазоны веса (до грамма), габариты (в мм) и запатентованные алгоритмы, исключающие аналоги.")
        
        if not report.equipment:
            st.info("Позиции оборудования не были выделены из загруженного фрагмента.")
        else:
            for idx, eq in enumerate(report.equipment, 1):
                ktru_label = f" • КТРУ: `{eq.ktru_code}`" if eq.ktru_code else ""
                with st.expander(f"📦 Позиция {idx}: {eq.name} ({eq.quantity or '1 шт.'}){ktru_label}", expanded=True):
                    
                    if eq.potential_bias_warning:
                        st.error(f"⚠️ **ИНДИКАТОР ЗАТОЧКИ:** {eq.potential_bias_warning}")
                    
                    if eq.detected_brand_bias:
                        st.markdown(f"🔬 **ДЕТАЛЬНЫЙ РАЗБОР ЗАТОЧКИ ПОД ПРОИЗВОДИТЕЛЯ:**")
                        st.warning(eq.detected_brand_bias)

                    if eq.suggested_neutral_specs:
                        st.markdown(f"💡 **КАК ОСПАРИВАТЬ (РЕКОМЕНДАЦИЯ ПОСТАВЩИКУ):**")
                        st.info(eq.suggested_neutral_specs)

                    st.markdown("**Ключевые технические требования ТЗ:**")
                    for s in eq.key_specs:
                        st.markdown(f"- {s}")

    # Вкладка 4: Запросы разъяснений
    with tab_inquiry:
        st.subheader("Официальные юридические запросы на разъяснение в ЕИС")
        st.caption("Сформированы по канонам претензионной практики 44-ФЗ со всеми реквизитами Заказчика. Готовы к копированию и отправке на ЭТП.")

        if not report.clarification_requests:
            st.info("Поводов для подачи запроса на разъяснение не обнаружено.")
        else:
            for idx, cr in enumerate(report.clarification_requests, 1):
                with st.expander(f"📄 Запрос № {idx}: {cr.subject}", expanded=True):
                    if cr.recipient_header:
                        st.markdown(f"**Официальная шапка:**\n```text\n{cr.recipient_header}\n```")
                    st.markdown(f"⚖️ **Нормативное обоснование:** `{cr.justification}`")
                    st.text_area(
                        "Полный официальный текст запроса (готов к отправке):",
                        value=cr.draft_text,
                        height=280,
                        key=f"draft_{idx}",
                    )

    # Вкладка 5: Экспорт отчета
    with tab_export:
        st.subheader("Выгрузка аналитического заключения")
        markdown_report = ReportExporter.to_markdown(report)
        
        st.download_button(
            label="📥 Скачать отчет в формате Markdown (.md)",
            data=markdown_report,
            file_name=f"Tender_Audit_{report.summary.law_type}.md",
            mime="text/markdown",
            use_container_width=True,
        )

        with st.expander("Предпросмотр текстового отчета"):
            st.markdown(markdown_report)

else:
    # Приветственный экран, если еще ничего не загружено
    st.info("👆 Загрузите ZIP-архив с закупкой или нажмите кнопку 'Загрузить эталон', чтобы увидеть работу ИИ.")
    
    st.markdown("### Что умеет сервис:")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        **⚖️ Юридический анти-краш**
        - Пресечение незаконных штрафов 0.5% в день
        - Сверка с нормами ПП РФ № 1042
        - Аудит кабальных условий приемки
        """)
    with c2:
        st.markdown("""
        **🩺 Медицинский комплаенс**
        - Проверка требований к РУ Росздравнадзора
        - Контроль нацрежима (ПП 878 радиоэлектроника)
        - Сверка с кодами КТРУ Минфина
        """)
    with c3:
        st.markdown("""
        **📝 Запросы в ЕИС за 1 клик**
        - Выявление «заточек» под бренды
        - Автогенерация юридических запросов
        - Ссылки на статьи 44-ФЗ и 135-ФЗ
        """)
