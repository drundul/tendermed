"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Stethoscope, Lock, Mail, Building, ArrowRight, AlertCircle, Loader2, Sparkles, Eye, EyeOff } from "lucide-react";
import { api, getToken } from "@/lib/api";

function RegisterContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planParam = searchParams.get("plan");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [agree152, setAgree152] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getToken()) {
      if (planParam) {
        router.replace(`/dashboard?openBilling=${planParam}`);
      } else {
        router.replace("/dashboard");
      }
    }
  }, [router, planParam]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agree152) {
      setError("Необходимо дать согласие на обработку персональных данных (152-ФЗ)");
      return;
    }

    setError("");
    setLoading(true);

    try {
      await api.auth.register({
        email,
        password,
        company_name: companyName,
      });
      if (planParam) {
        router.push(`/dashboard?openBilling=${planParam}`);
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sky-600 flex items-center justify-center text-white shadow-md shadow-sky-200">
            <Stethoscope className="w-6 h-6" />
          </div>
          <span className="font-bold text-2xl tracking-tight text-slate-900">
            TenderMed
          </span>
        </Link>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Регистрация аккаунта
        </h2>
        <div className="mt-2 inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full">
          <Sparkles className="w-3.5 h-3.5" />
          <span>3 полных аудита зачисляются сразу после регистрации</span>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl shadow-slate-200/50 sm:rounded-2xl border border-slate-200 sm:px-10">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 flex items-start gap-2.5">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Название компании / ИП (опционально)
              </label>
              <div className="relative">
                <Building className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="ООO «МедТехСнаб»"
                  className="block w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Рабочий Email
              </label>
              <div className="relative">
                <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="tender@medcompany.ru"
                  className="block w-full pl-10 pr-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                />
              </div>
              <p className="mt-1 text-[11px] text-slate-500">
                Корпоративный или персональный email на надёжном сервисе (Яндекс, Mail.ru, Gmail и др.)
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Пароль (не менее 6 символов)
              </label>
              <div className="relative">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-10 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-900 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none p-1"
                  title={showPassword ? "Скрыть пароль" : "Показать пароль"}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4 text-slate-400" />}
                </button>
              </div>
            </div>

            {/* Чекбокс согласия 152-ФЗ */}
            <div className="pt-2 flex items-start gap-2.5 text-xs text-slate-600">
              <input
                id="agree-152"
                type="checkbox"
                required
                checked={agree152}
                onChange={(e) => setAgree152(e.target.checked)}
                className="mt-0.5 w-4 h-4 text-sky-600 rounded border-slate-300 focus:ring-sky-500 cursor-pointer shrink-0"
              />
              <label htmlFor="agree-152" className="leading-snug cursor-pointer select-none">
                Я даю согласие на обработку персональных данных в соответствии с{" "}
                <Link href="/privacy" target="_blank" className="text-sky-600 font-semibold hover:underline">
                  152-ФЗ
                </Link>{" "}
                и принимаю условия{" "}
                <Link href="/terms" target="_blank" className="text-sky-600 font-semibold hover:underline">
                  Пользовательского соглашения
                </Link>
                .
              </label>
            </div>

            <div className="pt-3">
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-sky-600 hover:bg-sky-700 text-white font-semibold rounded-xl shadow-md shadow-sky-200 transition-all flex items-center justify-center gap-2 text-sm disabled:opacity-50 cursor-pointer"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Создание кабинета...
                  </>
                ) : (
                  <>
                    Получить 3 аудита и войти
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-600">
              Уже есть аккаунт?{" "}
              <Link href="/login" className="font-semibold text-sky-600 hover:text-sky-500">
                Войти в кабинет
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-50 flex items-center justify-center text-sm text-slate-500">Загрузка формы регистрации...</div>}>
      <RegisterContent />
    </Suspense>
  );
}
