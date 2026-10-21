"""
Data Anonymizer — Микро-анонимизатор персональных данных по 152-ФЗ.

Автоматически очищает извлеченный текст тендерных документов от конфиденциальных
персональных данных физических лиц перед отправкой в нейросеть:
  - Российские номера мобильных и городских телефонов -> [ТЕЛЕФОН_СКРЫТ]
  - Адреса электронной почты -> [EMAIL_СКРЫТ]
  - Паспортные данные граждан РФ (серия и номер) -> [ПАСПОРТ_СКРЫТ]
  - Номера СНИЛС -> [СНИЛС_СКРЫТ]
  - 12-значный ИНН физических лиц -> [ИНН_ФЛ_СКРЫТ] (10-значный ИНН юрлиц сохраняется!)
  - Номера банковских карт -> [НОМЕР_КАРТЫ_СКРЫТ]
"""

import re
from typing import Dict, Tuple
from pydantic import BaseModel, Field


class AnonymizationStats(BaseModel):
    """Статистика маскирования персональных данных."""
    phones_count: int = Field(default=0)
    emails_count: int = Field(default=0)
    passports_count: int = Field(default=0)
    snils_count: int = Field(default=0)
    personal_inn_count: int = Field(default=0)
    bank_cards_count: int = Field(default=0)

    @property
    def total_masked(self) -> int:
        return (
            self.phones_count
            + self.emails_count
            + self.passports_count
            + self.snils_count
            + self.personal_inn_count
            + self.bank_cards_count
        )


class DataAnonymizer:
    """Сервис маскирования персональных данных в соответствии с 152-ФЗ."""

    # 1. Телефоны: +7 (999) 123-45-67, 8-999-123-45-67, 8 (495) 1234567, +79991234567
    # Не трогаем ГОСТы (например, ГОСТ 12345-67) за счет проверки префикса +7 или 8
    PHONE_PATTERN = re.compile(
        r"(?:(?:\+7|8)[\s\-(]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})",
        re.IGNORECASE
    )

    # 2. Email-адреса
    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    # 3. Паспорт РФ: 4 цифры (серия) + 6 цифр (номер), с возможными словами "паспорт", "серия"
    PASSPORT_PATTERN = re.compile(
        r"(?:(?:паспорт|сери[яи])\s*[:\.]?\s*)?(?:\b\d{2}\s*\d{2}\s+\d{6}\b|\b\d{4}\s*№\s*\d{6}\b)",
        re.IGNORECASE
    )

    # 4. СНИЛС: 11 цифр в формате 123-456-789 01 или 123-456-789-01
    SNILS_PATTERN = re.compile(
        r"\b\d{3}[-\s]\d{3}[-\s]\d{3}[-\s]\d{2}\b"
    )

    # 5. ИНН физического лица: ровно 12 цифр подряд (ИНН юрлица 10 цифр — его не трогаем!)
    PERSONAL_INN_PATTERN = re.compile(
        r"(?<!\d)\d{12}(?!\d)"
    )

    # 6. Банковские карты: 16 цифр блоками по 4
    BANK_CARD_PATTERN = re.compile(
        r"\b(?:\d{4}[-\s]){3}\d{4}\b"
    )

    @classmethod
    def anonymize_text(cls, text: str) -> Tuple[str, AnonymizationStats]:
        """
        Маскирует персональные данные в тексте и возвращает (очищенный_текст, статистика).
        """
        if not text:
            return text, AnonymizationStats()

        stats = AnonymizationStats()

        # 1. Email (первыми, чтобы не пересекаться с цифрами)
        emails = cls.EMAIL_PATTERN.findall(text)
        stats.emails_count = len(emails)
        text = cls.EMAIL_PATTERN.sub("[EMAIL_СКРЫТ]", text)

        # 2. СНИЛС
        snils = cls.SNILS_PATTERN.findall(text)
        stats.snils_count = len(snils)
        text = cls.SNILS_PATTERN.sub("[СНИЛС_СКРЫТ]", text)

        # 3. Банковские карты
        cards = cls.BANK_CARD_PATTERN.findall(text)
        stats.bank_cards_count = len(cards)
        text = cls.BANK_CARD_PATTERN.sub("[НОМЕР_КАРТЫ_СКРЫТ]", text)

        # 4. Паспорта РФ
        passports = cls.PASSPORT_PATTERN.findall(text)
        stats.passports_count = len(passports)
        text = cls.PASSPORT_PATTERN.sub("[ПАСПОРТ_СКРЫТ]", text)

        # 5. ИНН физических лиц (12 цифр)
        personal_inns = cls.PERSONAL_INN_PATTERN.findall(text)
        stats.personal_inn_count = len(personal_inns)
        text = cls.PERSONAL_INN_PATTERN.sub("[ИНН_ФЛ_СКРЫТ]", text)

        # 6. Телефоны
        phones = cls.PHONE_PATTERN.findall(text)
        stats.phones_count = len(phones)
        text = cls.PHONE_PATTERN.sub("[ТЕЛЕФОН_СКРЫТ]", text)

        return text, stats
