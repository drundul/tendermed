import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TenderMed — ИИ-аудит тендеров медтехники (44-ФЗ и 223-ФЗ)",
  description:
    "Экспертный ИИ-аудит документации на поставку сложного медицинского оборудования (УЗИ, МРТ, КТ, ИВЛ). Детекция скрытых «заточек» под бренды, пресечение незаконных штрафов по ПП 1042 и нацрежима ПП 878. Генерация официальных запросов в Word за 60 секунд.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru" className="h-full bg-slate-50 antialiased">
      <body className="min-h-full flex flex-col font-sans text-slate-900 bg-slate-50">
        {children}
      </body>
    </html>
  );
}
