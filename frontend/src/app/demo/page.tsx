"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Stethoscope,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Download,
  CheckCircle2,
  ArrowRight,
  Scale,
  Sparkles,
  ExternalLink,
  Layers,
  Building,
  Calendar,
  DollarSign,
  AlertCircle,
  FileCheck,
  Info,
  ChevronRight,
  Printer,
  Copy,
} from "lucide-react";
import { api } from "@/lib/api";

export default function DemoPage() {
  const [demoData, setDemoData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"risks" | "med" | "eq" | "inquiry" | "fas" | "export">("risks");
  const [riskFilter, setRiskFilter] = useState<"all" | "high" | "medium">("all");
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.tenders
      .getPublicDemoAudit()
      .then((data) => setDemoData(data))
      .catch((err) => console.error("Error loading demo audit:", err))
      .finally(() => setLoading(false));
  }, []);

  const report = demoData?.report;

  const handleDownloadDemoDocx = async () => {
    setDownloading(true);
    try {
      await api.exports.downloadDemoReportDocx();
    } catch {
      alert("Не удалось скачать демонстрационный файл");
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyText = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const filteredRisks = (report?.risks || []).filter((r: any) => {
    if (riskFilter === "high") return r.severity === "HIGH";
    if (riskFilter === "medium") return r.severity === "MEDIUM";
    return true;
  });

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-sky-100 selection:text-sky-900 pb-20">
      {/* 1. ШАПКА ДЕМО-РЕЖИМА */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
              <Stethoscope className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-slate-900">
                TenderMed
              </span>
              <span className="text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                Демо-кабинет
              </span>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-xs sm:text-sm font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg hover:bg-slate-100 transition-colors"
            >
              Войти
            </Link>
            <Link
              href="/register"
              className="text-xs sm:text-sm font-semibold bg-sky-600 hover:bg-sky-700 text-white px-3.5 py-1.5 rounded-lg shadow-sm shadow-sky-200 transition-all flex items-center gap-1.5"
            >
              <span>3 проверки бесплатно</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* 2. ДЕМО ПЛАШКА-БАННЕР */}
      <div className="bg-gradient-to-r from-amber-500 via-amber-600 to-orange-500 text-white py-2.5 px-4 text-center text-xs sm:text-sm font-medium shadow-inner flex items-center justify-center gap-2">
        <Sparkles className="w-4 h-4 shrink-0 text-amber-200" />
        <span>
          Вы просматриваете интерактивный аудит реальной закупки <b>№ 0373100015826000556</b> (НМИЦ Кардиологии им. Чазова, 19.5 млн ₽). Все функции доступны для ознакомления.
        </span>
      </div>

      {/* 3. ОСНОВНОЙ КОНТЕНТ */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full space-y-6">
        {loading ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-500 space-y-3">
            <div className="w-8 h-8 border-2 border-sky-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-sm font-medium">Загрузка демонстрационного заключения...</p>
          </div>
        ) : !report ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-red-600 text-sm">
            Демонстрационный отчет временно формируется. Пожалуйста, обновите страницу.
          </div>
        ) : (
          <>
            {/* ВЕРДИКТ "СВЕТОФОР" */}
            <div
              className={`rounded-2xl p-6 sm:p-8 border shadow-sm transition-all ${
                report.verdict === "RED"
                  ? "bg-red-500/10 border-red-200 text-red-950"
                  : report.verdict === "YELLOW"
                  ? "bg-amber-500/10 border-amber-200 text-amber-950"
                  : "bg-emerald-500/10 border-emerald-200 text-emerald-950"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-black/5 pb-5">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${
                      report.verdict === "RED"
                        ? "bg-red-600 text-white"
                        : report.verdict === "YELLOW"
                        ? "bg-amber-500 text-white"
                        : "bg-emerald-600 text-white"
                    }`}
                  >
                    {report.verdict === "RED" ? (
                      <AlertTriangle className="w-7 h-7" />
                    ) : (
                      <ShieldCheck className="w-7 h-7" />
                    )}
                  </div>
                  <div>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                      Итоговый вердикт по закупке
                    </span>
                    <h2 className="text-lg sm:text-xl font-extrabold tracking-tight">
                      {report.verdict === "RED"
                        ? "🔴 СТОП-ФАКТОРЫ: ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ ИЛИ ВКЛЮЧЕНИЯ В РНП"
                        : report.verdict === "YELLOW"
                        ? "🟡 ВНИМАНИЕ: ТРЕБУЮТСЯ ЗАПРОСЫ РАЗЪЯСНЕНИЙ"
                        : "🟢 РЕКОМЕНДОВАНО К УЧАСТИЮ"}
                    </h2>
                  </div>
                </div>

                <div className="flex items-center gap-4 shrink-0 bg-white/80 rounded-xl px-4 py-2 border border-slate-200/80">
                  <div className="text-right">
                    <div className="text-[10px] uppercase font-bold text-slate-500">Индекс риска</div>
                    <div className="text-xl font-black text-slate-900">{report.risk_score} / 100</div>
                  </div>
                  <div className="w-10 h-10 rounded-full border-4 border-red-500 flex items-center justify-center font-bold text-xs text-red-700 bg-red-50">
                    {report.risk_score}
                  </div>
                </div>
              </div>

              <div className="mt-4 text-xs sm:text-sm leading-relaxed text-slate-700">
                <b className="text-slate-900">Резюме для генерального директора:</b>{" "}
                {report.verdict_summary}
              </div>
            </div>

            {/* КАРТОЧКА РЕКВИЗИТОВ И ПАРАМЕТРОВ ЗАКУПКИ */}
            <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Info className="w-4 h-4 text-sky-600" />
                <span>Официальные параметры извещения ЕИС</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <span className="text-[11px] font-medium text-slate-500">НМЦК закупки</span>
                  <div className="text-lg font-bold text-slate-900 mt-1">
                    {report.summary.nmck_rubles
                      ? `${report.summary.nmck_rubles.toLocaleString("ru-RU")} ₽`
                      : "19 500 000 ₽"}
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <span className="text-[11px] font-medium text-slate-500">Срок поставки</span>
                  <div className="text-xs font-bold text-red-600 mt-1 line-clamp-2" title={report.summary.delivery_deadline}>
                    {report.summary.delivery_deadline || "По заявке (до 5 рабочих дней)"}
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <span className="text-[11px] font-medium text-slate-500">Обеспечение контракта</span>
                  <div className="text-lg font-bold text-slate-900 mt-1">
                    {report.summary.contract_guarantee_percent ?? 5.0}% (975 000 ₽)
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                  <span className="text-[11px] font-medium text-slate-500">Обеспечение заявки</span>
                  <div className="text-lg font-bold text-slate-900 mt-1">
                    {report.summary.application_guarantee_percent ?? 1.0}% (195 000 ₽)
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-600">
                <div>
                  <span className="text-slate-400">Заказчик:</span>{" "}
                  <b className="text-slate-800">{report.summary.customer_name}</b>
                </div>
                <div>
                  <span className="text-slate-400">Объект закупки:</span>{" "}
                  <b className="text-slate-800">{report.summary.purchase_subject}</b>
                </div>
                <div>
                  <span className="text-slate-400">ИНН / КПП:</span>{" "}
                  <b className="text-slate-800">{report.summary.customer_inn} / {report.summary.customer_kpp}</b>
                </div>
                <div>
                  <span className="text-slate-400">Номер извещения:</span>{" "}
                  <a
                    href={`https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=${report.summary.notice_number}`}
                    target="_blank"
                    className="text-sky-600 font-bold hover:underline inline-flex items-center gap-1"
                  >
                    <span>{report.summary.notice_number}</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>

            {/* 4. ИНТЕРАКТИВНЫЕ ВКЛАДКИ АУДИТА */}
            <div>
              <div className="flex items-center gap-2 border-b border-slate-200 overflow-x-auto pb-px">
                <button
                  onClick={() => setActiveTab("risks")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "risks"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <AlertTriangle className="w-4 h-4" />
                  <span>Матрица рисков ({report.risks?.length || 0})</span>
                </button>

                <button
                  onClick={() => setActiveTab("med")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "med"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <Stethoscope className="w-4 h-4" />
                  <span>Мед. комплаенс</span>
                </button>

                <button
                  onClick={() => setActiveTab("eq")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "eq"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <Layers className="w-4 h-4" />
                  <span>Заточки ТЗ ({report.equipment?.length || 0})</span>
                </button>

                <button
                  onClick={() => setActiveTab("inquiry")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "inquiry"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Запросы в Word ({report.clarification_requests?.length || 0})</span>
                </button>

                <button
                  onClick={() => setActiveTab("fas")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "fas"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <Scale className="w-4 h-4 text-amber-600" />
                  <span>Жалоба в ФАС (ст. 105)</span>
                </button>

                <button
                  onClick={() => setActiveTab("export")}
                  className={`px-4 py-3 text-xs sm:text-sm font-bold border-b-2 transition-all flex items-center gap-2 shrink-0 cursor-pointer ${
                    activeTab === "export"
                      ? "border-sky-600 text-sky-600 bg-sky-50/50"
                      : "border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300"
                  }`}
                >
                  <Download className="w-4 h-4" />
                  <span>Экспорт отчета</span>
                </button>
              </div>

              {/* ТЕЛО ВКЛАДКИ 1: МАТРИЦА РИСКОВ */}
              {activeTab === "risks" && (
                <div className="pt-6 space-y-4">
                  <div className="flex items-center gap-2 pb-2">
                    <span className="text-xs text-slate-500 font-semibold">Фильтр:</span>
                    <button
                      onClick={() => setRiskFilter("all")}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                        riskFilter === "all" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                    >
                      Все ({report.risks?.length || 0})
                    </button>
                    <button
                      onClick={() => setRiskFilter("high")}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                        riskFilter === "high" ? "bg-red-600 text-white" : "bg-red-50 text-red-700 hover:bg-red-100"
                      }`}
                    >
                      Только критические 🔴
                    </button>
                    <button
                      onClick={() => setRiskFilter("medium")}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition-all cursor-pointer ${
                        riskFilter === "medium" ? "bg-amber-500 text-white" : "bg-amber-50 text-amber-700 hover:bg-amber-100"
                      }`}
                    >
                      Умеренные 🟡
                    </button>
                  </div>

                  <div className="space-y-3">
                    {filteredRisks.map((risk: any, idx: number) => (
                      <div
                        key={idx}
                        className={`bg-white rounded-2xl p-5 border shadow-sm transition-all ${
                          risk.severity === "HIGH"
                            ? "border-red-200 border-l-4 border-l-red-600"
                            : "border-amber-200 border-l-4 border-l-amber-500"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span
                                className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                                  risk.severity === "HIGH"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-amber-100 text-amber-800"
                                }`}
                              >
                                {risk.severity} • {risk.category}
                              </span>
                            </div>
                            <h4 className="font-bold text-base text-slate-900">{risk.title}</h4>
                            <p className="text-xs sm:text-sm text-slate-600 mt-1 leading-relaxed">
                              {risk.description}
                            </p>
                          </div>
                        </div>

                        {risk.recommendation && (
                          <div className="mt-3 pt-3 border-t border-slate-100 text-xs bg-slate-50/60 -mx-5 -mb-5 p-4 rounded-b-2xl">
                            <span className="font-bold text-slate-700">💡 Рекомендация эксперта:</span>{" "}
                            <span className="text-slate-600">{risk.recommendation}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ТЕЛО ВКЛАДКИ 2: МЕДИЦИНСКИЙ КОМПЛАЕНС */}
              {activeTab === "med" && (
                <div className="pt-6 space-y-4">
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-sm">
                    <h3 className="text-base font-bold text-slate-900">Регуляторный комплаенс медизделия</h3>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-xs text-slate-500 font-semibold">Регистрационное удостоверение (РУ)</span>
                        <div className="text-sm font-bold text-emerald-700 mt-1 flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Обязательно действующее РУ Росздравнадзора</span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1">{report.med_compliance?.ru_notes}</p>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-xs text-slate-500 font-semibold">Национальный режим (ПП РФ № 878 / ПП 102)</span>
                        <div className="text-sm font-bold text-amber-700 mt-1 flex items-center gap-1.5">
                          <AlertTriangle className="w-4 h-4" />
                          <span>Применяется правило «Третий лишний»</span>
                        </div>
                        <p className="text-xs text-slate-600 mt-1">{report.med_compliance?.national_regime_details}</p>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-xs text-slate-500 font-semibold">Каталог товаров, работ, услуг (КТРУ)</span>
                        <div className="text-sm font-bold text-slate-900 mt-1">
                          Код: {report.med_compliance?.ktru_code || "26.60.14.110-00000048"}
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Использован каталог ЕИС с дополнительными характеристиками</p>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
                        <span className="text-xs text-slate-500 font-semibold">Пусконаладка и обучение</span>
                        <div className="text-sm font-bold text-slate-700 mt-1">
                          {report.med_compliance?.installation_and_training ? "Требуется" : "Не требуется (расходное изделие)"}
                        </div>
                        <p className="text-xs text-slate-500 mt-1">Имплантируемое изделие стерильной поставки</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ТЕЛО ВКЛАДКИ 3: ЗАТОЧКИ ОБОРУДОВАНИЯ */}
              {activeTab === "eq" && (
                <div className="pt-6 space-y-4">
                  {(report.equipment || []).map((eq: any, idx: number) => (
                    <div key={idx} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
                        <h4 className="font-bold text-base text-slate-900">{eq.name}</h4>
                        <span className="text-xs bg-slate-100 text-slate-700 px-3 py-1 rounded-full font-semibold">
                          КТРУ: {eq.ktru_code || "26.60.14.110-00000048"}
                        </span>
                      </div>

                      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                        <div className="font-bold text-xs text-amber-900 flex items-center gap-1.5 mb-1">
                          <AlertTriangle className="w-4 h-4 text-amber-600" />
                          <span>Обнаруженные признаки брендовой заточки ТЗ:</span>
                        </div>
                        <p className="text-xs text-amber-950 leading-relaxed">
                          {eq.detected_brand_bias}
                        </p>
                      </div>

                      {eq.suggested_neutral_specs && (
                        <div className="bg-sky-50 border border-sky-200 rounded-xl p-4">
                          <div className="font-bold text-xs text-sky-900 mb-1">
                            💡 Как заказчик обязан расширить параметры для допуска эквивалентов:
                          </div>
                          <p className="text-xs text-sky-950 leading-relaxed">
                            {eq.suggested_neutral_specs}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* ТЕЛО ВКЛАДКИ 4: ЗАПРОСЫ В WORD */}
              {activeTab === "inquiry" && (
                <div className="pt-6 space-y-4">
                  <div className="flex items-center justify-between bg-sky-50 border border-sky-200 rounded-2xl p-4">
                    <div className="text-xs text-sky-900">
                      <b>Готовые запросы на разъяснение положений документации:</b> Сформированы по ГОСТ и нормам 44-ФЗ с официальной шапкой Заказчика, мотивировочной и просительной частью.
                    </div>
                    <button
                      onClick={handleDownloadDemoDocx}
                      className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all shrink-0 ml-4 flex items-center gap-1.5 cursor-pointer"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Скачать все в Word (.docx)</span>
                    </button>
                  </div>

                  {(report.clarification_requests || []).map((req: any, idx: number) => (
                    <div key={idx} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-3">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                        <span className="font-bold text-sm text-slate-900">Запрос № {idx + 1}: {req.topic}</span>
                        <button
                          onClick={() => handleCopyText(req.draft_text, idx)}
                          className="text-xs font-semibold text-sky-600 hover:text-sky-700 flex items-center gap-1 cursor-pointer"
                        >
                          <Copy className="w-3.5 h-3.5" />
                          <span>{copiedIndex === idx ? "Скопировано!" : "Копировать текст"}</span>
                        </button>
                      </div>

                      <div className="bg-slate-50 p-3 rounded-lg text-xs text-slate-500 font-mono">
                        {req.recipient_header || `Кому: ${report.summary.customer_name}`}
                      </div>

                      <pre className="text-xs text-slate-700 whitespace-pre-wrap font-sans bg-slate-50/50 p-4 rounded-xl border border-slate-100 leading-relaxed max-h-60 overflow-y-auto">
                        {req.draft_text}
                      </pre>
                    </div>
                  ))}
                </div>
              )}

              {/* ТЕЛО ВКЛАДКИ 5: ЖАЛОБА В ФАС */}
              {activeTab === "fas" && (
                <div className="pt-6 space-y-4">
                  <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-4 shadow-sm">
                    <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                      <div>
                        <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
                          <Scale className="w-5 h-5 text-amber-600" />
                          <span>Официальная жалоба в ФАС России (ст. 105 44-ФЗ)</span>
                        </h4>
                        <p className="text-xs text-slate-500 mt-0.5">
                          Готовый процессуальный документ для обжалования положений документации в территориальный УФАС
                        </p>
                      </div>

                      <button
                        onClick={handleDownloadDemoDocx}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center gap-1.5 cursor-pointer shrink-0"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Скачать проект в Word (.docx)</span>
                      </button>
                    </div>

                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 font-mono text-xs text-slate-700 space-y-2 max-h-96 overflow-y-auto whitespace-pre-wrap">
                      <b>В УПРАВЛЕНИЕ ФЕДЕРАЛЬНОЙ АНТИМОНОПОЛЬНОЙ СЛУЖБЫ ПО Г. МОСКВЕ</b>
                      <div>Заявитель: [Участник закупки • Вставьте реквизиты компании]</div>
                      <div>Заказчик: {report.summary.customer_name}</div>
                      <div>Номер извещения: {report.summary.notice_number} (НМЦК: 19 500 000,00 ₽)</div>
                      <div className="pt-2 border-t border-slate-200 font-bold text-slate-900 font-sans">
                        ЖАЛОБА на положения извещения об осуществлении закупки
                      </div>
                      <div className="font-sans text-xs text-slate-600 leading-relaxed pt-2">
                        Заказчиком утверждено описание объекта закупки с грубыми нарушениями п. 1 ч. 1 ст. 33 Федерального закона № 44-ФЗ и ст. 17 Закона о защите конкуренции № 135-ФЗ: совокупность параметров базовой частоты, МРТ-режима и функции 'Ответ на проведенную фибрилляцию предсердий' физически соответствует изделиям единственного производителя...
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ТЕЛО ВКЛАДКИ 6: ЭКСПОРТ */}
              {activeTab === "export" && (
                <div className="pt-6 space-y-4">
                  <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-4 shadow-sm">
                    <div className="w-16 h-16 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mx-auto border border-sky-100">
                      <Download className="w-8 h-8" />
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-slate-900">
                        Скачать полное экспертное заключение в Word
                      </h4>
                      <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                        Профессиональный отчёт со всеми таблицами реквизитов, матрицей рисков, медицинским комплаенсом и запросами в ЕИС.
                      </p>
                    </div>

                    <button
                      onClick={handleDownloadDemoDocx}
                      disabled={downloading}
                      className="px-6 py-3 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl text-sm shadow-md shadow-sky-200 transition-all inline-flex items-center gap-2 cursor-pointer disabled:opacity-50"
                    >
                      <FileCheck className="w-4 h-4" />
                      <span>{downloading ? "Генерация файла..." : "Скачать экспертный отчет (.docx)"}</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* 5. ФИКСИРОВАННЫЙ НИЖНИЙ CTA-БАР ДЛЯ ГОСТЕЙ */}
      <div className="fixed bottom-0 inset-x-0 bg-white/95 backdrop-blur-md border-t border-slate-200 py-3.5 px-4 shadow-lg z-50">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs sm:text-sm font-bold text-slate-900">
                Хотите проверить вашу закупку прямо сейчас?
              </div>
              <div className="text-[11px] text-slate-500">
                Зарегистрируйтесь за 30 секунд и получите 3 полных экспертных аудита бесплатно
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <Link
              href="/register"
              className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white text-xs sm:text-sm font-bold rounded-xl shadow-md shadow-sky-200 transition-all flex items-center gap-1.5"
            >
              <span>Попробовать бесплатно</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
