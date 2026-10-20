import os
import subprocess
import sys


def main():
    """Точка входа для запуска приложения TenderAI Med."""
    app_path = os.path.join(os.path.dirname(__file__), "ui", "streamlit_app.py")
    print("=" * 60)
    print("🏥 Запуск TenderAI Med (ИИ-аудит тендеров медтехники)...")
    print(f"Файл интерфейса: {app_path}")
    print("Открываем браузер на http://localhost:8501")
    print("=" * 60)
    
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.abspath(__file__))
    env["PYTHONPATH"] = project_root + os.pathpsep + env.get("PYTHONPATH", "")

    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    try:
        subprocess.run(cmd, cwd=project_root, env=env)
    except KeyboardInterrupt:
        print("\nРабота приложения завершена пользователем.")


if __name__ == "__main__":
    main()
