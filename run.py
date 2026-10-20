import os
import subprocess
import sys


def main():
    """Точка входа для запуска приложения TenderAI Med."""
    app_path = os.path.join(os.path.dirname(__file__), "ui", "app.py")
    print("=" * 60)
    print("🏥 Запуск TenderAI Med (ИИ-аудит тендеров медтехники)...")
    print(f"Файл интерфейса: {app_path}")
    print("Открываем браузер на http://localhost:8501")
    print("=" * 60)
    
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nРабота приложения завершена пользователем.")


if __name__ == "__main__":
    main()
