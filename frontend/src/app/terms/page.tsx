"use client";

import Link from "next/link";
import { Stethoscope, Scale, ArrowLeft } from "lucide-react";

export default function TermsPage() {
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
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center border border-sky-100">
            <Scale className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Пользовательское соглашение (Публичная оферта)
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Условия использования аналитической системы TenderMed • Редакция от 2026 г.
            </p>
          </div>
        </div>

        <div className="prose prose-slate max-w-none text-sm leading-relaxed space-y-6 text-slate-700">
          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">1. Термины и предмет соглашения</h2>
            <p>
              1.1. Настоящее Соглашение является публичной офертой в соответствии со ст. 437 Гражданского кодекса РФ. Регистрация в Сервисе или оплата любого тарифного пакета означает полное и безоговорочное принятие (акцепт) условий настоящего документа.
            </p>
            <p>
              1.2. Сервис TenderMed предоставляет Пользователю программный доступ к автоматизированным инструментам правового и технического анализа документации государственных закупок (44-ФЗ, 223-ФЗ), выявлению юридических рисков и генерации проектов процессуальных документов (запросов на разъяснение положений и жалоб в ФАС России).
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">2. Порядок регистрации и баланс проверок</h2>
            <p>
              2.1. При первичной регистрации каждому новому Пользователю безвозмездно начисляется стартовый пакет из 3 (трёх) проверок для ознакомления с функционалом Сервиса.
            </p>
            <p>
              2.2. Каждая проверка списывает с баланса Пользователя ровно 1 кредит при успешном завершении аудита по ссылке ЕИС или загруженному комплекту документов.
            </p>
            <p>
              2.3. Дополнительные пакеты проверок (тарифы «Старт», «Профи», «Корпоративный») приобретаются Пользователем в Личном кабинете. Приобретенные проверки не сгорают по истечении календарного месяца и остаются на балансе Пользователя до полного исчерпания.
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">3. Права и обязанности сторон</h2>
            <p>
              3.1. <b>Сервис обязуется:</b> обеспечивать круглосуточную доступность платформы, конфиденциальность информации и удаление персональных данных третьих лиц из документов до их семантической обработки в соответствии со 152-ФЗ.
            </p>
            <p>
              3.2. <b>Пользователь обязуется:</b> не передавать учетные данные третьим лицам и использовать аналитические отчеты исключительно в законных целях участия в государственных и коммерческих закупках.
            </p>
            <p>
              3.3. Результаты аудитов, сгенерированные запросы на разъяснение и проекты жалоб в ФАС носят экспертно-рекомендательный характер. Окончательное решение о подаче процессуальных документов принимает уполномоченный представитель участника закупки.
            </p>
          </section>

          <section>
            <h2 className="text-base font-bold text-slate-900 mb-2">4. Интеллектуальная собственность</h2>
            <p>
              Алгоритмы детекции медицинских заточек ТЗ, классификатор документов, эвристические базы правил 44-ФЗ и шаблоны генерации документов являются объектами интеллектуальной собственности разработчиков сервиса TenderMed и защищены законодательством РФ.
            </p>
          </section>
        </div>

        <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
          <span>TenderMed • Регулируется законодательством РФ</span>
          <Link href="/privacy" className="text-sky-600 hover:underline">
            Политика 152-ФЗ
          </Link>
        </div>
      </div>
    </div>
  );
}
