"""
TenderMed SaaS Local Launcher
Запускает одновременно FastAPI Backend (порт 8000) и Next.js Frontend (порт 3000)
"""

import os
import sys
import subprocess
import time
import webbrowser

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")

    print("=" * 65)
    print("🚀 ЗАПУСК TENDERMED SAAS (FASTAPI + NEXT.JS)")
    print("=" * 65)
    print("🔹 Backend API:  http://localhost:8000 (Swagger: http://localhost:8000/docs)")
    print("🔹 Frontend Web: http://localhost:3000")
    print("=" * 65)

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    # 1. Запуск FastAPI
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=project_root, env=env)

    # 2. Запуск Next.js dev сервера
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_cmd, "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=(sys.platform == "win32"))

    # Открываем браузер через 3 секунды
    time.sleep(3)
    webbrowser.open("http://localhost:3000")

    print("\n✅ Платформа успешно запущена! Нажмите Ctrl+C для остановки.\n")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nОстанавливаем сервисы...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Работа завершена.")


if __name__ == "__main__":
    main()
