"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Stethoscope,
  ShieldCheck,
  AlertTriangle,
  FileText,
  Download,
  Building,
  Scale,
  Sparkles,
  LogOut,
  RefreshCw,
  Search,
  Upload,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  ChevronDown,
  Layers,
  History,
  KeyRound,
} from "lucide-react";
import { api, getToken, getOpenAIKey, setOpenAIKey } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();

  // Состояние пользователя
  const [user, setUser] = useState<{
    id: number;
    email: string;
    company_name?: string;
    available_credits: number;
  } | null>(null);

  // Ввод данных
  const [inputTab, setInputTab] = useState<"url" | "files">("url");
  const [eisUrl, setEisUrl] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedModel, setSelectedModel] = useState("gpt-5.4-mini");
  const [engineMode, setEngineMode] = useState<"heuristic" | "ai">("heuristic");
  const [demoMode, setDemoMode] = useState(false);
  const [customApiKey, setCustomApiKey] = useState("");
  const [showKeyInput, setShowKeyInput] = useState(false);

  // Статус анализа
  const [loading, setLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("");
  const [error, setError] = useState("");

  // Текущий отчет
  const [auditResult, setAuditResult] = useState<any | null>(null);

  // История
  const [history, setHistory] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"risks" | "med" | "eq" | "inquiry" | "export">("risks");
  const [riskFilter, setRiskFilter] = useState<"all" | "high" | "medium">("all");

  // Загрузка пользователя и истории при входе
  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const savedKey = getOpenAIKey();
    setCustomApiKey(savedKey);
    if (savedKey && savedKey.trim().length > 0) {
      setEngineMode("ai");
      setShowKeyInput(true);
    }

    api.auth
      .getMe()
      .then((data) => setUser(data))
      .catch(() => {
        api.auth.logout();
        router.push("/login");
      });

    loadHistory();
  }, [router]);

  const loadHistory = async () => {
    try {
      const data = await api.tenders.getHistory();
      setHistory(data);
    } catch {
      // Игнорируем ошибку истории
    }
  };

  const handleAnalyzeUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!eisUrl.trim()) return;

    setError("");
    setLoading(true);
    setLoadingStatus("🌐 Скачиваем документы с портала ЕИС (zakupki.gov.ru)...");

    try {
      const isHeuristic = engineMode === "heuristic";
      const keyToSend = isHeuristic ? "" : customApiKey;
      const res = await api.tenders.analyzeUrl(eisUrl.trim(), selectedModel, isHeuristic, keyToSend);
      setAuditResult(res);
      if (user) {
        setUser({ ...user, available_credits: res.remaining_credits });
      }
      loadHistory();
    } catch (err: any) {
      setError(err.message || "Ошибка при анализе закупки");
    } finally {
      setLoading(false);
      setLoadingStatus("");
    }
  };

  const handleAnalyzeFiles = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFiles.length === 0) return;

    setError("");
    setLoading(true);
    setLoadingStatus("📑 Обработка и 152-ФЗ анонимизация файлов...");

    try {
      const isHeuristic = engineMode === "heuristic";
      const keyToSend = isHeuristic ? "" : customApiKey;
      const res = await api.tenders.analyzeFiles(selectedFiles, selectedModel, isHeuristic, keyToSend);
      setAuditResult(res);
      if (user) {
        setUser({ ...user, available_credits: res.remaining_credits });
      }
      loadHistory();
    } catch (err: any) {
      setError(err.message || "Ошибка при анализе файлов");
    } finally {
      setLoading(false);
      setLoadingStatus("");
    }
  };

  const handleLoadDetail = async (id: number) => {
    setLoading(true);
    setLoadingStatus("Загрузка сохраненного отчета...");
    setError("");
    try {
      const detail = await api.tenders.getDetail(id);
      setAuditResult({
        audit_id: detail.id,
        report: detail.report,
        execution_time_seconds: 0,
        anonymization_stats: null,
      });
    } catch (err: any) {
      setError(err.message || "Не удалось загрузить отчет");
    } finally {
      setLoading(false);
      setLoadingStatus("");
    }
  };

  const report = auditResult?.report;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      {/* 1. ШАПКА КАБИНЕТА */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
              <Stethoscope className="w-4 h-4" />
            </div>
            <span className="font-bold text-lg tracking-tight text-slate-900">
              TenderMed
            </span>
          </Link>

          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-xs font-semibold text-slate-900">
                    {user.company_name || user.email}
                  </span>
                  <span className="text-[11px] text-slate-500">
                    {user.email}
                  </span>
                </div>

                <div className="inline-flex items-center gap-1.5 bg-sky-50 border border-sky-200 text-sky-800 px-3 py-1 rounded-full text-xs font-bold">
                  <Sparkles className="w-3.5 h-3.5 text-sky-600" />
                  <span>Проверок: {user.available_credits}</span>
                </div>

                <button
                  onClick={() => {
                    api.auth.logout();
                    router.push("/login");
                  }}
                  title="Выйти"
                  className="p-2 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 2. ОСНОВНОЙ КОНТЕЙНЕР */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {/* БЛОК ВВОДА ЗАКУПКИ */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                <span>⚡ Экспертная экспертиза закупки</span>
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Вставьте прямую ссылку на закупку с ЕИС или загрузите комплект файлов ТЗ и контракта.
              </p>
            </div>
          </div>

          {/* ВЫБОР ДВИЖКА АНАЛИЗА: Автономный 44-ФЗ или Нейросеть */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-5 mb-5 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-2">
                  <span>Режим работы системы</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                    engineMode === "heuristic" 
                      ? "bg-sky-100 text-sky-800 border border-sky-200" 
                      : "bg-violet-100 text-violet-800 border border-violet-200"
                  }`}>
                    {engineMode === "heuristic" ? "⚡ Автономный эксперт 44-ФЗ" : "🤖 Нейросеть GPT"}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed max-w-2xl">
                  {engineMode === "heuristic" ? (
                    <>
                      <b>Автономный режим без ИИ:</b> Мгновенный экспертный анализ норм права РФ, сроков поставки, РУ Росздравнадзора, нацрежима (ПП РФ № 878) и обеспечения по <i>встроенной юридической базе правил 44-ФЗ</i>. Токены не тратятся, внешние серверы не опрашиваются.
                    </>
                  ) : (
                    <>
                      <b>Нейросетевой режим (OpenAI):</b> Глубокий семантический ИИ-аудит спецификации на скрытые «заточки» оборудования и генерация персонализированных запросов на разъяснение на базе GPT-4o / GPT-5.4.
                    </>
                  )}
                </p>
              </div>

              {/* Крупный переключатель режима */}
              <div className="flex items-center bg-white p-1 rounded-xl border border-slate-300 shadow-sm shrink-0">
                <button
                  type="button"
                  onClick={() => {
                    setEngineMode("heuristic");
                    setDemoMode(true);
                  }}
                  className={`px-3.5 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                    engineMode === "heuristic"
                      ? "bg-sky-600 text-white shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Scale className="w-4 h-4" />
                  <span>⚡ Автономно (без ИИ)</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setEngineMode("ai");
                    setDemoMode(false);
                    setShowKeyInput(true);
                  }}
                  className={`px-3.5 py-2 text-xs font-semibold rounded-lg transition-all flex items-center gap-1.5 ${
                    engineMode === "ai"
                      ? "bg-violet-600 text-white shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  <Sparkles className="w-4 h-4" />
                  <span>🤖 С нейросетью (OpenAI)</span>
                </button>
              </div>
            </div>

            {/* Настройки при выборе режима с нейросетью */}
            {engineMode === "ai" && (
              <div className="mt-4 pt-4 border-t border-slate-200/80 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <div className="flex-1 flex items-center gap-2">
                  <KeyRound className="w-4 h-4 text-violet-600 shrink-0" />
                  <input
                    type="password"
                    value={customApiKey}
                    onChange={(e) => {
                      setCustomApiKey(e.target.value);
                      setOpenAIKey(e.target.value);
                    }}
                    placeholder="Вставьте ваш API-ключ (OpenAI sk-... или ключ ProxyAPI)"
                    className="w-full px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                  {customApiKey && (
                    <button
                      type="button"
                      onClick={() => {
                        setCustomApiKey("");
                        setOpenAIKey("");
                      }}
                      className="text-[11px] text-red-500 hover:underline shrink-0 font-medium px-1"
                    >
                      Очистить
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-xs text-slate-500 font-medium">Модель:</span>
                  <select
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="text-xs font-semibold bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500"
                  >
                    <option value="gpt-5.4-mini">gpt-5.4-mini (Быстрая • Рекомендуется)</option>
                    <option value="gpt-5.4">gpt-5.4 (Глубокий аудит)</option>
                    <option value="gpt-5.2">gpt-5.2 (Флагманская)</option>
                    <option value="gpt-4o">gpt-4o</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Быстрые ссылки для тестирования */}
          <div className="mb-5 flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Быстрый пример:</span>
            <button
              type="button"
              onClick={() => {
                setInputTab("url");
                setEisUrl("https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0306500000326000965");
              }}
              className="px-2.5 py-1 bg-sky-50 hover:bg-sky-100 text-sky-800 font-semibold rounded-md border border-sky-200 transition-colors"
            >
              🩺 Кардиостимуляторы 0306500000326000965 (35.9 млн ₽)
            </button>
            <button
              type="button"
              onClick={() => {
                setInputTab("url");
                setEisUrl("https://zakupki.gov.ru/epz/order/notice/zk20/view/common-info.html?regNumber=0372200005426000768");
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-md transition-colors"
            >
              Котировка 0372200005426000768 (.doc)
            </button>
            <button
              type="button"
              onClick={() => {
                setInputTab("url");
                setEisUrl("https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0142200001326018834");
              }}
              className="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-md transition-colors"
            >
              Аукцион 0142200001326018834 (ea20)
            </button>
          </div>

          {/* Переключатель вкладок ввода */}
          <div className="flex border-b border-slate-200 mb-6">
            <button
              onClick={() => setInputTab("url")}
              className={`pb-3 px-4 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
                inputTab === "url"
                  ? "border-sky-600 text-sky-600"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              <Search className="w-4 h-4" />
              <span>По ссылке с ЕИС (zakupki.gov.ru)</span>
            </button>
            <button
              onClick={() => setInputTab("files")}
              className={`pb-3 px-4 text-sm font-semibold flex items-center gap-2 border-b-2 transition-all ${
                inputTab === "files"
                  ? "border-sky-600 text-sky-600"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              <Upload className="w-4 h-4" />
              <span>Загрузить файлы (.docx / .pdf / .doc / .zip)</span>
            </button>
          </div>

          {/* Форма 1: По ссылке */}
          {inputTab === "url" && (
            <form onSubmit={handleAnalyzeUrl} className="flex flex-col sm:flex-row gap-3">
              <input
                type="url"
                required
                value={eisUrl}
                onChange={(e) => setEisUrl(e.target.value)}
                placeholder="https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0142200001326018834"
                className="flex-1 px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 transition-all"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-3 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl text-sm shadow-md shadow-sky-200 transition-all flex items-center justify-center gap-2 shrink-0 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Анализируем...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Скачать и проверить
                  </>
                )}
              </button>
            </form>
          )}

          {/* Форма 2: Файлы */}
          {inputTab === "files" && (
            <form onSubmit={handleAnalyzeFiles} className="space-y-4">
              <input
                type="file"
                multiple
                accept=".docx,.pdf,.doc,.zip,.txt,.md"
                onChange={(e) => {
                  if (e.target.files) {
                    setSelectedFiles(Array.from(e.target.files));
                  }
                }}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer"
              />
              <button
                type="submit"
                disabled={loading || selectedFiles.length === 0}
                className="px-6 py-3 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl text-sm shadow-md shadow-sky-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Анализируем файлы...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    Запустить аудит файлов
                  </>
                )}
              </button>
            </form>
          )}

          {/* Индикатор статуса загрузки с шагами */}
          {loading && (
            <div className="mt-5 p-5 rounded-2xl bg-sky-50 border border-sky-200 text-sky-950 space-y-3 shadow-inner">
              <div className="flex items-center gap-2.5 font-bold text-sm">
                <RefreshCw className="w-4 h-4 animate-spin text-sky-600 shrink-0" />
                <span>{loadingStatus}</span>
              </div>
              <div className="w-full bg-sky-200/60 rounded-full h-2 overflow-hidden">
                <div className="bg-sky-600 h-2 rounded-full animate-pulse w-4/5 transition-all"></div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-semibold text-slate-600 pt-1">
                <div className="flex items-center gap-1.5 text-sky-800">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" /> 1. Поиск в ЕИС
                </div>
                <div className="flex items-center gap-1.5 text-sky-800">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" /> 2. Скачивание файлов
                </div>
                <div className="flex items-center gap-1.5 text-sky-800">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" /> 3. 152-ФЗ защита
                </div>
                <div className="flex items-center gap-1.5 text-sky-800">
                  <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" /> 4. ИИ-экспертиза
                </div>
              </div>
            </div>
          )}

          {/* Ошибка */}
          {error && (
            <div className="mt-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <div>
                <div className="font-bold">Ошибка обработки</div>
                <div className="mt-0.5 text-xs text-red-600 leading-relaxed">{error}</div>
              </div>
            </div>
          )}
        </div>

        {/* 3. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ АУДИТА */}
        {report && (
          <div className="space-y-6">
            {/* ИНФО-БАННЕР РЕЖИМА АУДИТА */}
            {report.is_mock ? (
              <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 shadow-sm">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="text-xs text-amber-900 leading-relaxed">
                  <div className="font-bold text-sm text-amber-950 flex items-center gap-2">
                    <span>Экспертный аудит по правилам 44-ФЗ (Без внешнего OpenAI API)</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-amber-200 text-amber-900 font-semibold">
                      Реальные данные ЕИС
                    </span>
                  </div>
                  <div className="mt-1">
                    Все параметры контракта (НМЦК: <b>{report.summary.nmck_rubles ? `${report.summary.nmck_rubles.toLocaleString("ru-RU")} ₽` : "Н/Д"}</b>, Заказчик: <b>{report.summary.customer_name}</b>, объект: <b>«{report.summary.purchase_subject}»</b>) и риски извлечены напрямую из официальных документов ЕИС.
                    Чтобы запустить глубокий нейросетевой аудит через OpenAI (GPT-4o / GPT-5), укажите ваш API-ключ в настройках выше.
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4 sm:p-5 flex items-start gap-3.5 shadow-sm">
                <Sparkles className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div className="text-xs text-emerald-900 leading-relaxed">
                  <div className="font-bold text-sm text-emerald-950 flex items-center gap-2">
                    <span>Живой ИИ-аудит ({report.model_used || "OpenAI"})</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-200 text-emerald-900 font-semibold">
                      GPT Модель
                    </span>
                  </div>
                  <div className="mt-1">
                    Отчет сформирован нейросетью с глубоким семантическим риск-аудитом по всей документации закупки.
                  </div>
                </div>
              </div>
            )}

            {/* ГЛАВНЫЙ БАННЕР ВЕРДИКТА */}
            <div
              className={`p-6 sm:p-8 rounded-2xl text-white shadow-lg ${
                report.verdict === "RED"
                  ? "bg-gradient-to-r from-red-600 to-rose-700 shadow-red-200"
                  : report.verdict === "YELLOW"
                  ? "bg-gradient-to-r from-amber-500 to-yellow-600 shadow-amber-200"
                  : "bg-gradient-to-r from-emerald-600 to-teal-700 shadow-emerald-200"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="text-xs uppercase font-bold tracking-wider opacity-90 mb-1">
                    Итоговый вердикт участия
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-extrabold flex items-center gap-2">
                    <span>
                      {report.verdict === "RED"
                        ? "🔴 СТОП-ФАКТОРЫ: ВЫСОКИЙ РИСК"
                        : report.verdict === "YELLOW"
                        ? "🟡 ВНИМАНИЕ: ТРЕБУЕТСЯ ЗАПРОС"
                        : "🟢 РЕКОМЕНДОВАНО К УЧАСТИЮ"}
                    </span>
                  </h2>
                </div>
                <div className="bg-white/10 backdrop-blur-md px-5 py-3 rounded-xl text-center shrink-0 border border-white/20">
                  <div className="text-xs uppercase tracking-wider font-semibold opacity-80">
                    Индекс риска
                  </div>
                  <div className="text-3xl font-black">{report.risk_score} / 100</div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-white/20 text-sm leading-relaxed opacity-95">
                <b>Резюме для руководителя:</b> {report.verdict_summary}
              </div>
            </div>

            {/* БЕЙДЖ 152-ФЗ АНОНИМИЗАЦИИ */}
            {auditResult.anonymization_stats && auditResult.anonymization_stats.total_masked > 0 && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium px-4 py-3 rounded-xl flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  <b>152-ФЗ Комплаенс:</b> В тексте документов замаскировано{" "}
                  {auditResult.anonymization_stats.total_masked} персональных данных (телефоны:{" "}
                  {auditResult.anonymization_stats.phones_count}, email:{" "}
                  {auditResult.anonymization_stats.emails_count}). Никакие перс. данные не покинули защищенный периметр.
                </span>
              </div>
            )}

            {/* МЕТРИКИ КОНТРАКТА */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-xs text-slate-500 font-medium">НМЦК закупки</div>
                <div className="text-lg font-bold text-slate-900 mt-1">
                  {report.summary.nmck_rubles
                    ? `${report.summary.nmck_rubles.toLocaleString("ru-RU")} ₽`
                    : "Не указана"}
                </div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-xs text-slate-500 font-medium">Срок поставки</div>
                <div className="text-lg font-bold text-slate-900 mt-1">
                  {report.summary.delivery_deadline || "По графику"}
                </div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-xs text-slate-500 font-medium">Авансирование</div>
                <div className="text-lg font-bold text-slate-900 mt-1">
                  {report.summary.advance_percent ? `${report.summary.advance_percent}%` : "Без аванса"}
                </div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-xs text-slate-500 font-medium">Обеспечение контракта</div>
                <div className="text-lg font-bold text-slate-900 mt-1">
                  {report.summary.contract_guarantee_percent
                    ? `${report.summary.contract_guarantee_percent}%`
                    : "Не установлено"}
                </div>
              </div>
            </div>

            {/* РЕКВИЗИТЫ ЗАКАЗЧИКА */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h3 className="font-bold text-sm text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Building className="w-4 h-4 text-sky-600" />
                Юридические реквизиты Заказчика
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-slate-500 text-xs">Заказчик / В лице:</div>
                  <div className="font-semibold text-slate-900">
                    {report.summary.customer_name || "Не указан"}{" "}
                    {report.summary.customer_signer && `(${report.summary.customer_signer})`}
                  </div>
                  <div className="text-slate-500 text-xs mt-2">ИНН / КПП:</div>
                  <div className="font-mono text-slate-800">
                    {report.summary.customer_inn || "Н/Д"} / {report.summary.customer_kpp || "Н/Д"}
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-xs">Номер извещения / ЭТП:</div>
                  <div className="font-mono text-slate-800">
                    {report.summary.notice_number || "Не указан"} • {report.summary.etp_name || "ЕЭТП"}
                  </div>
                  <div className="text-slate-500 text-xs mt-2">Адрес / Место поставки:</div>
                  <div className="text-slate-800">
                    {report.summary.customer_address || report.summary.delivery_place || "По документации"}
                  </div>
                </div>
              </div>
            </div>

            {/* ВКЛАДКИ ДЕТАЛЬНОГО АУДИТА */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="flex border-b border-slate-200 bg-slate-50/50 overflow-x-auto">
                <button
                  onClick={() => setActiveTab("risks")}
                  className={`py-3.5 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-all ${
                    activeTab === "risks"
                      ? "border-sky-600 text-sky-600 bg-white"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  🚨 Матрица рисков ({report.risks?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab("med")}
                  className={`py-3.5 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-all ${
                    activeTab === "med"
                      ? "border-sky-600 text-sky-600 bg-white"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  🩺 Мед. комплаенс
                </button>
                <button
                  onClick={() => setActiveTab("eq")}
                  className={`py-3.5 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-all ${
                    activeTab === "eq"
                      ? "border-sky-600 text-sky-600 bg-white"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  🔬 Заточки и оборудование ({report.equipment?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab("inquiry")}
                  className={`py-3.5 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-all ${
                    activeTab === "inquiry"
                      ? "border-sky-600 text-sky-600 bg-white"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  📝 Официальные запросы в Word ({report.clarification_requests?.length || 0})
                </button>
                <button
                  onClick={() => setActiveTab("export")}
                  className={`py-3.5 px-5 text-sm font-semibold border-b-2 whitespace-nowrap transition-all ${
                    activeTab === "export"
                      ? "border-sky-600 text-sky-600 bg-white"
                      : "border-transparent text-slate-600 hover:text-slate-900"
                  }`}
                >
                  💾 Экспорт отчета
                </button>
              </div>

              <div className="p-6">
                {/* 1. ВКЛАДКА: МАТРИЦА РИСКОВ */}
                {activeTab === "risks" && (
                  <div className="space-y-4">
                    <div className="flex gap-2 mb-4">
                      <button
                        onClick={() => setRiskFilter("all")}
                        className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                          riskFilter === "all"
                            ? "bg-slate-900 text-white"
                            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                        }`}
                      >
                        Все риски ({report.risks?.length || 0})
                      </button>
                      <button
                        onClick={() => setRiskFilter("high")}
                        className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                          riskFilter === "high"
                            ? "bg-red-600 text-white"
                            : "bg-red-50 text-red-700 hover:bg-red-100"
                        }`}
                      >
                        Только критические 🔴
                      </button>
                      <button
                        onClick={() => setRiskFilter("medium")}
                        className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                          riskFilter === "medium"
                            ? "bg-amber-600 text-white"
                            : "bg-amber-50 text-amber-700 hover:bg-amber-100"
                        }`}
                      >
                        Умеренные 🟡
                      </button>
                    </div>

                    {report.risks
                      ?.filter((r: any) => {
                        if (riskFilter === "high") return r.severity === "HIGH";
                        if (riskFilter === "medium") return r.severity === "MEDIUM";
                        return true;
                      })
                      .map((risk: any, idx: number) => (
                        <div
                          key={idx}
                          className={`p-4 rounded-xl border-l-4 ${
                            risk.severity === "HIGH"
                              ? "border-l-red-500 bg-red-50/40 border border-slate-200"
                              : "border-l-amber-500 bg-amber-50/40 border border-slate-200"
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <h4 className="font-bold text-sm text-slate-900">
                              {idx + 1}. {risk.title}
                            </h4>
                            <span
                              className={`text-[11px] font-bold px-2 py-0.5 rounded uppercase ${
                                risk.severity === "HIGH"
                                  ? "bg-red-100 text-red-700"
                                  : "bg-amber-100 text-amber-700"
                              }`}
                            >
                              {risk.severity} • {risk.category}
                            </span>
                          </div>
                          <p className="text-xs text-slate-600 mb-2 leading-relaxed">
                            {risk.description}
                          </p>
                          {risk.quote && (
                            <div className="text-xs text-slate-500 italic bg-white/70 p-2 rounded mb-2 border border-slate-100">
                              📌 Цитата: «{risk.quote}»
                            </div>
                          )}
                          {risk.law_reference && (
                            <div className="text-xs font-semibold text-slate-700 mb-1">
                              ⚖️ Норма права: {risk.law_reference}
                            </div>
                          )}
                          <div className="text-xs font-semibold text-emerald-700 bg-emerald-50 p-2 rounded border border-emerald-100">
                            💡 Рекомендация: {risk.recommendation}
                          </div>
                        </div>
                      ))}
                  </div>
                )}

                {/* 2. ВКЛАДКА: МЕДКОМПЛАЕНС */}
                {activeTab === "med" && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-4">
                      <div>
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Регистрационное удостоверение (РУ)
                        </div>
                        <div className="font-bold text-base text-slate-900 mt-1">
                          {report.med_compliance.ru_required ? "⚠️ Требуется действующее РУ" : "Не затребовано"}
                        </div>
                        <p className="text-xs text-slate-600 mt-1">
                          {report.med_compliance.ru_notes}
                        </p>
                      </div>

                      <div className="pt-3 border-t border-slate-200">
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Национальный режим (ПП РФ № 878 / ст. 14)
                        </div>
                        <div className="font-bold text-base text-slate-900 mt-1">
                          {report.med_compliance.national_regime_applies
                            ? "🚨 Применяется (Ограничение допуска)"
                            : "✅ Ограничений не установлено"}
                        </div>
                        <p className="text-xs text-slate-600 mt-1">
                          {report.med_compliance.national_regime_details}
                        </p>
                      </div>
                    </div>

                    <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 space-y-4">
                      <div>
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Каталог КТРУ
                        </div>
                        <div className="font-bold text-base text-slate-900 mt-1">
                          {report.med_compliance.ktru_used
                            ? `Использована позиция: ${report.med_compliance.ktru_code || "Да"}`
                            : "Свободная форма описания Заказчика"}
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-200">
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                          Сервис, пусконаладка и гарантия
                        </div>
                        <div className="text-sm text-slate-800 mt-1">
                          • Монтаж и инструктаж:{" "}
                          <b>{report.med_compliance.installation_and_training ? "Да" : "Нет"}</b>
                        </div>
                        <div className="text-sm text-slate-800">
                          • Гарантийный срок:{" "}
                          <b>{report.med_compliance.warranty_period_months || "Не указан"} мес.</b>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 3. ВКЛАДКА: ЗАТОЧКИ И СПЕЦИФИКАЦИЯ */}
                {activeTab === "eq" && (
                  <div className="space-y-4">
                    {report.equipment?.map((eq: any, idx: number) => (
                      <div key={idx} className="bg-slate-50 p-5 rounded-xl border border-slate-200">
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <h4 className="font-bold text-sm text-slate-900">
                            {idx + 1}. {eq.name} ({eq.quantity || "1 шт."})
                          </h4>
                          {eq.ktru_code && (
                            <span className="text-xs font-mono bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-600">
                              КТРУ: {eq.ktru_code}
                            </span>
                          )}
                        </div>

                        {eq.detected_brand_bias && (
                          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-800 mb-2">
                            <b>🔬 Анализ заточки под производителя:</b> {eq.detected_brand_bias}
                          </div>
                        )}

                        {eq.suggested_neutral_specs && (
                          <div className="p-3 bg-sky-50 border border-sky-200 rounded-lg text-xs text-sky-800 mb-2">
                            <b>💡 Как оспаривать:</b> {eq.suggested_neutral_specs}
                          </div>
                        )}

                        <div className="text-xs text-slate-600">
                          <span className="font-semibold text-slate-700">Ключевые требования:</span>
                          <ul className="list-disc list-inside mt-1 space-y-0.5">
                            {eq.key_specs?.map((s: string, sIdx: number) => (
                              <li key={sIdx}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* 4. ВКЛАДКА: ОФИЦИАЛЬНЫЕ ЗАПРОСЫ В WORD */}
                {activeTab === "inquiry" && (
                  <div className="space-y-6">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-sky-50 border border-sky-200 rounded-xl">
                      <div>
                        <div className="font-bold text-sm text-sky-950">
                          Готовые официальные письма для отправки на ЭТП
                        </div>
                        <div className="text-xs text-sky-800 mt-0.5">
                          Сформированы по ст. 33, 34, 42 44-ФЗ с шапкой Заказчика и местом для подписи.
                        </div>
                      </div>
                      <button
                        onClick={() =>
                          api.exports.downloadClarificationsDocx(
                            auditResult.audit_id,
                            report.summary.notice_number
                          )
                        }
                        className="px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-lg text-xs flex items-center gap-1.5 shadow-sm shrink-0"
                      >
                        <Download className="w-4 h-4" />
                        Скачать ВСЕ запросы в Word (.docx)
                      </button>
                    </div>

                    {report.clarification_requests?.map((cr: any, idx: number) => (
                      <div key={idx} className="bg-slate-50 p-5 rounded-xl border border-slate-200">
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <h4 className="font-bold text-sm text-slate-900">
                            Запрос № {idx + 1}: {cr.subject}
                          </h4>
                          <button
                            onClick={() =>
                              api.exports.downloadSingleClarificationDocx(
                                auditResult.audit_id,
                                idx + 1,
                                report.summary.notice_number
                              )
                            }
                            className="text-xs bg-white hover:bg-slate-100 text-sky-700 font-semibold px-3 py-1 rounded border border-slate-300 flex items-center gap-1 shadow-sm"
                          >
                            <Download className="w-3.5 h-3.5" />
                            Скачать этот запрос (.docx)
                          </button>
                        </div>

                        {cr.recipient_header && (
                          <div className="text-xs font-mono bg-white p-2.5 rounded border border-slate-200 text-slate-600 mb-2 whitespace-pre-wrap">
                            {cr.recipient_header}
                          </div>
                        )}

                        <div className="text-xs text-sky-700 font-semibold mb-2">
                          ⚖️ Правовое основание: {cr.justification}
                        </div>

                        <textarea
                          readOnly
                          rows={6}
                          value={cr.draft_text}
                          className="w-full text-xs font-sans p-3 bg-white border border-slate-200 rounded-lg text-slate-800 focus:outline-none"
                        />
                      </div>
                    ))}
                  </div>
                )}

                {/* 5. ВКЛАДКА: ЭКСПОРТ ОТЧЕТА */}
                {activeTab === "export" && (
                  <div className="space-y-4">
                    <p className="text-sm text-slate-600">
                      Выгрузите полный аналитический отчёт со светофором и таблицами для согласования с руководством:
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <button
                        onClick={() =>
                          api.exports.downloadReportDocx(
                            auditResult.audit_id,
                            report.summary.notice_number
                          )
                        }
                        className="p-5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl shadow-md shadow-sky-200 text-left transition-all flex items-center justify-between"
                      >
                        <div>
                          <div className="font-bold text-base flex items-center gap-2">
                            <Download className="w-5 h-5" />
                            Полный отчет в Word (.docx)
                          </div>
                          <div className="text-xs text-sky-100 mt-1">
                            Оформленный документ с таблицами, метриками и блоками вердиктов
                          </div>
                        </div>
                      </button>

                      <button
                        onClick={() =>
                          api.exports.downloadReportMd(
                            auditResult.audit_id,
                            report.summary.notice_number
                          )
                        }
                        className="p-5 bg-white hover:bg-slate-50 text-slate-800 rounded-xl border border-slate-300 text-left transition-all flex items-center justify-between"
                      >
                        <div>
                          <div className="font-bold text-base flex items-center gap-2">
                            <FileText className="w-5 h-5 text-slate-500" />
                            Отчёт в формате Markdown (.md)
                          </div>
                          <div className="text-xs text-slate-500 mt-1">
                            Для корпоративных баз знаний, Notion и Obsidian
                          </div>
                        </div>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 4. ИСТОРИЯ ПРОВЕРОК */}
        {history.length > 0 && (
          <div className="mt-12 bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
            <h3 className="font-bold text-base text-slate-900 mb-4 flex items-center gap-2">
              <History className="w-4 h-4 text-slate-500" />
              История ваших проверок ({history.length})
            </h3>
            <div className="divide-y divide-slate-100">
              {history.map((h: any) => (
                <div
                  key={h.id}
                  onClick={() => handleLoadDetail(h.id)}
                  className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:bg-slate-50 p-2 rounded-lg cursor-pointer transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span
                      className={`w-3 h-3 rounded-full shrink-0 ${
                        h.verdict === "RED"
                          ? "bg-red-500"
                          : h.verdict === "YELLOW"
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                    />
                    <div>
                      <div className="font-semibold text-sm text-slate-900">
                        {h.purchase_subject}
                      </div>
                      <div className="text-xs text-slate-500">
                        № {h.notice_number || "Б/Н"} • {h.customer_name || "Заказчик"}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-500 shrink-0">
                    <span className="font-bold text-slate-700">Индекс риска: {h.risk_score}/100</span>
                    <button className="text-sky-600 font-semibold hover:underline">
                      Открыть →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
