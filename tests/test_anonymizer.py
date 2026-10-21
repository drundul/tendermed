import pytest
from app.services.anonymizer import DataAnonymizer, AnonymizationStats


def test_anonymize_phones():
    text = (
        "Контактное лицо: Иванов И.И., телефон: +7 (916) 123-45-67, "
        "дополнительный: 8-800-200-00-00 или 89991234567."
    )
    cleaned, stats = DataAnonymizer.anonymize_text(text)
    assert "+7 (916)" not in cleaned
    assert "8-800-200-00-00" not in cleaned
    assert "89991234567" not in cleaned
    assert "[ТЕЛЕФОН_СКРЫТ]" in cleaned
    assert stats.phones_count == 3


def test_anonymize_emails():
    text = "Пишите нам на tender_doc@hospital-samara.ru или personal.doctor@gmail.com"
    cleaned, stats = DataAnonymizer.anonymize_text(text)
    assert "tender_doc@hospital-samara.ru" not in cleaned
    assert "personal.doctor@gmail.com" not in cleaned
    assert cleaned.count("[EMAIL_СКРЫТ]") == 2
    assert stats.emails_count == 2


def test_anonymize_personal_inn_vs_legal_inn():
    # 10 цифр — ИНН организации (сохраняется для реквизитов заказчика!)
    # 12 цифр — ИНН физического лица (маскируется!)
    text = "Заказчик ГБУЗ ИНН: 7701234567, ИП Смирнов ИНН: 771234567890"
    cleaned, stats = DataAnonymizer.anonymize_text(text)
    assert "7701234567" in cleaned  # Юрлицо сохранено
    assert "771234567890" not in cleaned  # Физлицо замаскировано
    assert "[ИНН_ФЛ_СКРЫТ]" in cleaned
    assert stats.personal_inn_count == 1


def test_anonymize_snils_and_passport():
    text = "СНИЛС сотрудника 123-456-789 01, паспорт 45 12 123456 выдан ОВД"
    cleaned, stats = DataAnonymizer.anonymize_text(text)
    assert "123-456-789 01" not in cleaned
    assert "45 12 123456" not in cleaned
    assert "[СНИЛС_СКРЫТ]" in cleaned
    assert "[ПАСПОРТ_СКРЫТ]" in cleaned
    assert stats.snils_count == 1
    assert stats.passports_count == 1


def test_anonymize_clean_technical_text():
    # ГОСТ и технические диапазоны не должны ломаться
    text = "ГОСТ Р 50444-92, датчик 2-5 МГц, погрешность не более 0.05 мм"
    cleaned, stats = DataAnonymizer.anonymize_text(text)
    assert "ГОСТ Р 50444-92" in cleaned
    assert stats.total_masked == 0
