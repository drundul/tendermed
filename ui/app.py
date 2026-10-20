import os
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
        help="Введите ваш ключ OpenAI с доступом к моделям GPT-4o / GPT-4.1",
    )

    # Выбор модели
    available_models = [
        "gpt-4.1",
        "gpt-4o",
        "gpt-4.1-mini",
        "gpt-4o-mini",
        "o3-mini",
        "o4-mini",
    ]
    default_model_index = 0 if "gpt-4.1" in available_models else 1
    selected_model = st.selectbox(
        "Аналитическая модель",
        options=available_models,
        index=default_model_index,
        help="Модели gpt-4.1 и gpt-4o обеспечивают максимальную глубину юридического и технического аудита.",
    )

    # Демо-режим
    demo_mode = st.toggle(
        "🧪 Демо-режим (Mock)",
        value=settings.mock_mode or not bool(api_key_input.strip()),
        help="Включение показа эталонного отчета по закупке УЗИ-аппарата без обращения к внешним API.",
    )

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
    uploaded_file = st.file_uploader(
        "Перетащите архив извещения (.zip) или отдельные файлы (.pdf, .docx, .txt)",
        type=["zip", "pdf", "docx", "txt", "md"],
        help="Поддерживаются архивы ЕИС с закупочной документацией или отдельные файлы ТЗ и контракта.",
    )

with col_demo:
    st.markdown("<br>", unsafe_allow_html=True)
    load_sample_btn = st.button("⚡ Загрузить эталон (УЗИ Resona 7)", use_container_width=True)

# Запуск анализа
pipeline = TenderAnalyzerPipeline(api_key=api_key_input.strip() if api_key_input else None)

if load_sample_btn:
    with st.spinner("Формирование экспертного заключения по эталонному тендеру..."):
        # Загружаем эталонный образец
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "sample_med_tender.md")
        sample_bytes = b""
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                sample_bytes = f.read()
        else:
            sample_bytes = "Техническое задание на поставку УЗИ системы".encode("utf-8")

        result = pipeline.process_file_bytes(
            filename="Эталон_Закупка_УЗИ_44ФЗ.md",
            file_bytes=sample_bytes,
            model_name=selected_model,
            force_mock=True,
        )
        st.session_state.analysis_result = result
        st.success("Эталонный комплект документации успешно проанализирован!")

elif uploaded_file is not None:
    analyze_btn = st.button("🚀 Начать ИИ-экспертизу закупки", type="primary", use_container_width=True)
    if analyze_btn:
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            with st.status("Выполняется многоуровневый анализ документации...", expanded=True) as status:
                st.write("📦 Распаковка и извлечение текстового слоя...")
                file_bytes = uploaded_file.getvalue()
                
                st.write("📑 Классификация документов (ТЗ / Проект контракта / Информационная карта)...")
                st.write("⚖️ Юридический аудит штрафов и неустоек (ПП РФ № 1042)...")
                st.write("🩺 Проверка медицинского комплаенса (РУ Росздравнадзора, ПП РФ № 878, КТРУ)...")
                st.write("🔍 Поиск признаков ограничения конкуренции («заточек» под бренд)...")

                result = pipeline.process_file_bytes(
                    filename=uploaded_file.name,
                    file_bytes=file_bytes,
                    model_name=selected_model,
                    force_mock=demo_mode,
                )
                st.session_state.analysis_result = result
                status.update(label="Анализ успешно завершен!", state="complete", expanded=False)
        st.success(f"Анализ завершен за {result.execution_time_seconds} сек. Обработано {result.total_documents} документов ({result.total_characters} символов).")


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

    # 3. ВКЛАДКИ ДЕТАЛЬНОГО АНАЛИЗА
    tab_risks, tab_med, tab_eq, tab_inquiry, tab_export = st.tabs([
        f"🚨 Матрица рисков ({len(report.risks)})",
        "🩺 Медицинский комплаенс",
        "🔬 Спецификация и заточки",
        f"📝 Запросы разъяснений ({len(report.clarification_requests)})",
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

    # Вкладка 3: Спецификация оборудования
    with tab_eq:
        st.subheader("Анализ позиций оборудования и детекция 'заточек'")
        if not report.equipment:
            st.info("Позиции оборудования не были выделены из загруженного фрагмента.")
        else:
            for eq in report.equipment:
                st.markdown(f"### {eq.name}")
                st.caption(f"Количество: {eq.quantity or '1 шт.'}")
                
                if eq.potential_bias_warning:
                    st.error(f"⚠️ **ВНИМАНИЕ НА ЗАТОЧКУ:** {eq.potential_bias_warning}")
                
                st.markdown("**Ключевые технические требования ТЗ:**")
                for s in eq.key_specs:
                    st.markdown(f"- {s}")
                st.divider()

    # Вкладка 4: Запросы разъяснений
    with tab_inquiry:
        st.subheader("Черновики запросов на разъяснение положений в ЕИС")
        st.caption("Скопируйте подготовленный текст и отправьте заказчику через электронную торговую площадку (ЭТП).")

        if not report.clarification_requests:
            st.info("Поводов для подачи запроса на разъяснение не обнаружено.")
        else:
            for idx, cr in enumerate(report.clarification_requests, 1):
                with st.expander(f"Запрос № {idx}: {cr.subject}", expanded=True):
                    st.markdown(f"**Нормативное обоснование:** {cr.justification}")
                    st.text_area(
                        "Текст запроса к заказчику (готов к отправке):",
                        value=cr.draft_text,
                        height=200,
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
