"use client";

import { useState, useEffect } from "react";
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
  Layers,
  UserCheck,
  FileCheck,
} from "lucide-react";
import { getToken, api } from "@/lib/api";

export default function LandingPage() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    const token = getToken();
    if (token) {
      setIsLoggedIn(true);
      api.auth
        .getMe()
        .then((u) => setUserEmail(u.email))
        .catch(() => {
          setIsLoggedIn(false);
        });
    }
  }, []);

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
            <Link href="/demo" className="text-amber-700 font-semibold hover:text-amber-800 transition-colors flex items-center gap-1">
              <span>Демо-кабинет</span>
              <span className="text-[10px] bg-amber-100 px-1.5 py-0.2 rounded-full border border-amber-200">Free</span>
            </Link>
            <a href="#compliance" className="hover:text-sky-600 transition-colors">
              152-ФЗ Защита
            </a>
            <a href="#faq" className="hover:text-sky-600 transition-colors">
              FAQ
            </a>
          </nav>

          <div className="flex items-center gap-3">
            {isLoggedIn ? (
              <Link
                href="/dashboard"
                className="text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg shadow-sm transition-all flex items-center gap-1.5"
              >
                <UserCheck className="w-4 h-4" />
                <span>Личный кабинет</span>
                {userEmail && <span className="hidden lg:inline text-xs opacity-80">({userEmail})</span>}
              </Link>
            ) : (
              <>
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
              </>
            )}
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
            {isLoggedIn ? (
              <Link
                href="/dashboard"
                className="w-full sm:w-auto px-8 py-3.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl shadow-lg shadow-emerald-200 transition-all flex items-center justify-center gap-2 text-base"
              >
                <UserCheck className="w-5 h-5" />
                Перейти в личный кабинет
              </Link>
            ) : (
              <Link
                href="/register"
                className="w-full sm:w-auto px-8 py-3.5 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl shadow-lg shadow-sky-200 transition-all flex items-center justify-center gap-2 text-base"
              >
                <Sparkles className="w-5 h-5" />
                Попробовать бесплатно (3 аудита)
              </Link>
            )}

            <Link
              href="/demo"
              className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-slate-50 text-slate-700 font-semibold rounded-xl border border-slate-300 shadow-sm transition-all flex items-center justify-center gap-2 text-base"
            >
              <FileText className="w-4 h-4 text-sky-600" />
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
            <div className="bg-slate-100/80 px-4 py-3 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <span className="text-xs font-mono text-slate-500 ml-2">
                  Извещение № 0373100015826000556 (Электрокардиостимуляторы имплантируемые МРТ)
                </span>
              </div>
              <span className="text-xs bg-red-100 text-red-700 font-semibold px-2 py-0.5 rounded">
                Светофор: Стоп-фактор 🔴
              </span>
            </div>

            <div className="p-6 sm:p-8 text-left bg-gradient-to-b from-white to-slate-50">
              <div className="bg-red-500 text-white p-5 rounded-xl shadow-md shadow-red-200 mb-6">
                <div>
                  <h4 className="font-bold text-lg flex items-center gap-2">
                    <span>🔴</span> ВНИМАНИЕ: ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ ИЛИ ВКЛЮЧЕНИЯ В РНП
                  </h4>
                  <p className="text-sm text-red-100 mt-1">
                    Индекс риска: <b>92 / 100</b> • Обнаружены жесткий срок поставки 5 дней,
                    незаконное требование скана РУ в заявке и скрытая заточка под частоты ЭКС.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">НМЦК закупки</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">19 500 000 ₽</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Срок поставки по заявке</div>
                  <div className="text-base font-bold text-red-600 mt-0.5">5 рабочих дней</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Обеспечение контракта</div>
                  <div className="text-base font-bold text-slate-900 mt-0.5">5.0% (975 000 ₽)</div>
                </div>
                <div className="bg-white p-3.5 rounded-lg border border-slate-200">
                  <div className="text-xs text-slate-500 font-medium">Готовые запросы в ЕИС</div>
                  <div className="text-base font-bold text-sky-600 mt-0.5">Word (.docx)</div>
                </div>
              </div>

              <div className="border border-sky-200 bg-sky-50/50 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-sky-600 flex items-center justify-center text-white shrink-0">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-semibold text-sm text-slate-900">
                      Интерактивный демонстрационный аудит
                    </div>
                    <div className="text-xs text-slate-500">
                      Оцените полный отчет, матрицу рисков, проект жалобы в ФАС и скачайте образцы в Word
                    </div>
                  </div>
                </div>
                <Link
                  href="/demo"
                  className="px-5 py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-lg text-xs shadow-sm transition-all flex items-center gap-1.5 shrink-0"
                >
                  <span>Открыть демо-кабинет</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. ВОЗМОЖНОСТИ */}
      <section id="features" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest">
              Специализация на медицинских закупках
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              То, чего не умеют универсальные тендерные сервисы
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200/80 hover:shadow-lg transition-all">
              <div className="w-12 h-12 rounded-xl bg-sky-100 flex items-center justify-center text-sky-600 mb-6">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">
                Детекция брендовых «заточек»
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Выявляет узкие диапазоны частот, веса и запатентованные алгоритмы производителей (Mindray, GE, Philips, Medtronic, Abbott), исключающие поставку эквивалентов.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200/80 hover:shadow-lg transition-all">
              <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600 mb-6">
                <Scale className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">
                Пресечение незаконных штрафов
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Сверяет условия неустоек и штрафов строго с Постановлением Правительства РФ № 1042 и готовит требования о приведении формул в соответствие с 1/300 ключевой ставки.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200/80 hover:shadow-lg transition-all">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-600 mb-6">
                <FileCheck className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-slate-900 mb-2">
                Конструктор жалоб в ФАС и запросов в Word
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                Генерирует готовые юридические документы в формате .docx с шапкой Заказчика, нормами ст. 33, 34 44-ФЗ и ст. 105 для подачи жалобы в УФАС.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. ТАРИФЫ (ЕДИНАЯ СИНХРОНИЗИРОВАННАЯ СЕТКА) */}
      <section id="pricing" className="py-20 bg-slate-50 border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold text-sky-600 uppercase tracking-widest">
              Прозрачные тарифы
            </h2>
            <p className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
              Пакеты проверок без абонентской платы
            </p>
            <p className="mt-4 text-base text-slate-600">
              Купленные проверки не сгорают в конце месяца и действуют бессрочно.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-stretch">
            {/* Тариф 1: Бесплатный тест */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  Для пробы
                </span>
                <h3 className="font-bold text-lg text-slate-900 mt-2">Тестовый</h3>
                <p className="text-xs text-slate-500 mt-1 min-h-[32px]">Оцените точность анализа перед покупкой</p>
                <div className="my-5">
                  <span className="text-3xl font-extrabold text-slate-900">0 ₽</span>
                </div>
                <ul className="space-y-2.5 text-xs text-slate-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span><b>3 полных аудита</b> при регистрации</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Скачивание с ЕИС по ссылке</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Светофор рисков и штрафы ПП 1042</span>
                  </li>
                  <li className="flex items-center gap-2 text-slate-400">
                    <span>— Конструктор жалоб в ФАС</span>
                  </li>
                </ul>
              </div>
              <Link
                href={isLoggedIn ? "/dashboard" : "/register"}
                className="w-full py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold rounded-xl text-center text-xs transition-all"
              >
                {isLoggedIn ? "Перейти в кабинет" : "Попробовать бесплатно"}
              </Link>
            </div>

            {/* Тариф 2: Старт */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                  Базовый
                </span>
                <h3 className="font-bold text-lg text-slate-900 mt-2">Старт</h3>
                <p className="text-xs text-slate-500 mt-1 min-h-[32px]">Для небольших поставщиков медтехники</p>
                <div className="my-5">
                  <span className="text-3xl font-extrabold text-slate-900">1 900 ₽</span>
                  <div className="text-[11px] text-slate-500 mt-0.5">15 проверок • 126 ₽ / аудит</div>
                </div>
                <ul className="space-y-2.5 text-xs text-slate-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span><b>15 проверок</b> без срока действия</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Автономный аудит 44-ФЗ и ИИ</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Выгрузка запросов в Word (.docx)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Анализ РУ и нацрежима ПП 878</span>
                  </li>
                </ul>
              </div>
              <Link
                href={isLoggedIn ? "/dashboard?openBilling=start" : "/register?plan=start"}
                className="w-full py-2.5 bg-sky-50 hover:bg-sky-100 text-sky-700 font-bold rounded-xl text-center text-xs transition-all border border-sky-200"
              >
                Подключить пакет
              </Link>
            </div>

            {/* Тариф 3: Профи (Популярный) */}
            <div className="bg-white rounded-2xl p-6 border-2 border-sky-600 shadow-xl shadow-sky-100 flex flex-col justify-between relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-sky-600 text-white text-[10px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">
                Хит продаж • Рекомендуем
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  Оптимальный
                </span>
                <h3 className="font-bold text-lg text-slate-900 mt-2">Профи / Медтехника</h3>
                <p className="text-xs text-slate-500 mt-1 min-h-[32px]">Для активных участников медицинских торгов</p>
                <div className="my-5">
                  <span className="text-3xl font-extrabold text-slate-900">5 900 ₽</span>
                  <div className="text-[11px] text-slate-500 mt-0.5">50 проверок • 118 ₽ / аудит</div>
                </div>
                <ul className="space-y-2.5 text-xs text-slate-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span><b>50 проверок</b> документации</span>
                  </li>
                  <li className="flex items-center gap-2 font-bold text-slate-900">
                    <Scale className="w-3.5 h-3.5 text-amber-600" />
                    <span>Конструктор жалоб в ФАС (ст. 105)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Глубокий поиск брендовых заточек</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Скачивание готовых жалоб в Word</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                    <span>Аудит кабальных неустоек ПП 1042</span>
                  </li>
                </ul>
              </div>
              <Link
                href={isLoggedIn ? "/dashboard?openBilling=pro" : "/register?plan=pro"}
                className="w-full py-2.5 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl text-center text-xs shadow-md shadow-sky-200 transition-all"
              >
                Подключить тариф
              </Link>
            </div>

            {/* Тариф 4: Корпоративный */}
            <div className="bg-white rounded-2xl p-6 border border-slate-200 flex flex-col justify-between shadow-sm">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                  Максимум выгоды
                </span>
                <h3 className="font-bold text-lg text-slate-900 mt-2">Корпоративный</h3>
                <p className="text-xs text-slate-500 mt-1 min-h-[32px]">Для тендерных отделов и дистрибьюторов</p>
                <div className="my-5">
                  <span className="text-3xl font-extrabold text-slate-900">14 900 ₽</span>
                  <div className="text-[11px] text-slate-500 mt-0.5">150 проверок • 99 ₽ / аудит</div>
                </div>
                <ul className="space-y-2.5 text-xs text-slate-600 mb-6">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span><b>150 проверок</b> (самая выгодная цена)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Жалобы в территориальные УФАС</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Многопользовательский доступ</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                    <span>Загрузка больших архивов ТЗ и Excel</span>
                  </li>
                </ul>
              </div>
              <Link
                href={isLoggedIn ? "/dashboard?openBilling=corp" : "/register?plan=corp"}
                className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl text-center text-xs transition-all"
              >
                Подключить отдел
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 6. БЛОК 152-ФЗ КОМПЛАЕНС */}
      <section id="compliance" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto bg-slate-50 border border-slate-200 rounded-3xl p-8 sm:p-10">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-lg text-slate-900">
                  Строгое соответствие Федеральному закону № 152-ФЗ
                </h3>
                <p className="text-xs text-slate-500">Защита конфиденциальности и персональных данных</p>
              </div>
            </div>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed space-y-2">
              Перед передачей документов в аналитический модуль наша система автоматически маскирует и удаляет персональные телефоны, адреса электронной почты, паспортные данные и СНИЛС должностных лиц заказчика. База данных физически локализована на территории РФ в соответствии с требованиями законодательства.
            </p>

            <div className="mt-6 pt-6 border-t border-slate-200 flex flex-wrap items-center gap-4 text-xs font-semibold">
              <Link href="/privacy" className="text-sky-600 hover:underline">
                Политика обработки персональных данных →
              </Link>
              <Link href="/terms" className="text-sky-600 hover:underline">
                Пользовательское соглашение →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 7. FAQ */}
      <section id="faq" className="py-20 bg-slate-50 border-t border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-slate-900 text-center mb-12">
            Часто задаваемые вопросы
          </h2>

          <div className="space-y-4">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                Законно ли скачивать документы закупок с ЕИС?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Да, абсолютно. В силу ст. 7 Федерального закона № 44-ФЗ и ст. 7–8 закона № 149-ФЗ
                вся документация на `zakupki.gov.ru` является общедоступной публичной информацией.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                Как сервис находит скрытые «заточки» под бренды?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Система анализирует диапазоны характеристик оборудования и выявляет комбинации требований, которые физически соответствуют изделиям только одной конкретной модели (Medtronic, Mindray, GE, Philips).
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
              <h4 className="font-bold text-base text-slate-900 mb-2">
                В каком виде формируются запросы и жалоба в ФАС?
              </h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                Вы получаете готовые файлы Microsoft Word (.docx), оформленные по правилам делопроизводства с шапкой Заказчика, статьями 33, 34 44-ФЗ, ПП 1042 и ст. 105 44-ФЗ. Документы готовы к подаче на ЭТП или в УФАС.
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
            <Link href="/demo" className="hover:text-white transition-colors">
              Демо-кабинет
            </Link>
            <Link href="/privacy" className="hover:text-white transition-colors">
              Политика 152-ФЗ
            </Link>
            <Link href="/terms" className="hover:text-white transition-colors">
              Пользовательское соглашение
            </Link>
            <Link href="/login" className="hover:text-white transition-colors">
              Вход для клиентов
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
