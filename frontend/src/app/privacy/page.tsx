"use client";

import Link from "next/link";
import { Stethoscope, ShieldCheck, ArrowLeft, Lock } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-sm border border-slate-200 p-8 sm:p-12">
        <div className="flex items-center justify-between border-b border-slate-100 pb-6 mb-8">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-sky-600 flex items-center justify-center text-white shadow-sm shadow-sky-200">
              <Stethoscope className="w-5 h-5" />
            </div>
            <span className="font-bold text-xl tracking-tight text-slate-900">
              TenderMed
            </span>
          </Link>

          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-sky-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            На главную
          </Link>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Политика в отношении обработки персональных данных
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              В соответствии с Федеральным законом РФ от 27.07.2006 № 152-ФЗ «О персональных данных» • Редакция от 2026 г.
            </p>
          </div>
        </div>

        <div className="prose prose-slate max-w-none text-sm leading-relaxed space-y-6 text-slate-700">
          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">1. Общие положения</h2>
            <p>
              1.1. Настоящая Политика определяет порядок обработки и защиты персональных данных пользователей сервиса TenderMed (далее — Оператор), доступного в сети Интернет по адресу домена сервиса.
            </p>
            <p>
              1.2. Соблюдение прав и свобод человека и гражданина при обработке его персональных данных, включая защиту прав на неприкосновенность частной жизни, личную и семейную тайну — важнейшее условие деятельности Оператора.
            </p>
            <p>
              1.3. Обработка персональных данных осуществляется исключительно на законной и справедливой основе в строгом соответствии с нормами 152-ФЗ, 149-ФЗ и 44-ФЗ.
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">2. Состав собираемых персональных данных</h2>
            <p>Оператор обрабатывает следующие категории данных Пользователя:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Адрес электронной почты (email), используемый для идентификации и доступа в Личный кабинет;</li>
              <li>Название организации или данные индивидуального предпринимателя (по желанию пользователя);</li>
              <li>Технические метаданные (IP-адрес, файлы cookies, сведения о типе браузера и операционной системы);</li>
              <li>История проверок государственных закупок и транзакции пополнения баланса.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">3. Цели обработки персональных данных</h2>
            <ul className="list-disc pl-5 space-y-1">
              <li>Предоставление доступа к функционалу экспертного ИИ-аудита документации закупок медтехники;</li>
              <li>Идентификация Пользователя в рамках заключенного соглашения об оказании услуг;</li>
              <li>Направление сервисных уведомлений, информации о готовности аудитов и чеков об оплате;</li>
              <li>Обеспечение технической поддержки и предотвращение несанкционированного доступа.</li>
            </ul>
          </section>

          <section className="bg-sky-50 border border-sky-100 rounded-xl p-4">
            <h2 className="text-base font-bold text-sky-900 mb-1 flex items-center gap-2">
              <Lock className="w-4 h-4 text-sky-600" />
              4. Микро-анонимизация документов закупок (Privacy-by-Design)
            </h2>
            <p className="text-xs text-sky-800 leading-normal">
              Все файлы тендерной документации, загружаемые для анализа, проходят этап автоматической маскировки и деперсонализации. 
              Система автоматически удаляет телефонные номера, персональные email-адреса, паспортные данные, СНИЛС и ИНН физических лиц перед отправкой в модуль семантического анализа.
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">5. Локализация и безопасность хранения данных</h2>
            <p>
              5.1. В соответствии со ст. 18 ч. 5 Федерального закона № 152-ФЗ и № 242-ФЗ база данных пользователей TenderMed размещается на серверах, физически расположенных на территории Российской Федерации.
            </p>
            <p>
              5.2. Пароли пользователей шифруются с использованием криптографических алгоритмов хэширования (bcrypt / PBKDF2) и никогда не хранятся в открытом виде.
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">6. Права субъекта персональных данных</h2>
            <p>
              Пользователь имеет право в любой момент запросить сведения об обработке его данных, потребовать их уточнения, блокирования или уничтожения, направив запрос по электронной почте Оператора через службу поддержки сервиса.
            </p>
          </section>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>TenderMed • Соответствие нормам 152-ФЗ РФ</span>
          <Link href="/terms" className="text-sky-600 hover:underline">
            Пользовательское соглашение
          </Link>
        </div>
      </div>
    </div>
  );
}
