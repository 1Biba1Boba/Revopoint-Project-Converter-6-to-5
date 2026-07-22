"""
Скрипт для сборки Revopoint Converter 6to5 v1.1.0 в standalone exe
"""

import subprocess
import os

APP_NAME = "Revopoint-Converter-6to5"
ICON_PATH = None  # Если есть иконка, укажите путь

def build_exe():
    """Собирает проект в один exe файл через PyInstaller"""
    
    # Проверяем, установлен ли pyinstaller
    try:
        import pyinstaller
    except ImportError:
        print("Устанавливаю pyinstaller...")
        subprocess.run(["pip", "install", "pyinstaller"])
    
    # Упрощённая команда pyinstaller без version-file
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed",
        "--icon", "None",
        "converter.py"
    ]
    
    print(f"Сборка {APP_NAME}.exe...")
    print(f"Команда: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("\nУспешно собрано!")
        print(f" exe находится в: dist/{APP_NAME}.exe")
    else:
        print(f"Ошибка сборки:\n{result.stderr}")
    
    return result.returncode == 0

def create_dist_folder():
    """Копилирует exe в отдельную папку dist/"""
    import shutil
    
    dist_folder = "dist"
    os.makedirs(dist_folder, exist_ok=True)
    
    exe_source = f"dist/{APP_NAME}.exe"
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, os.path.join(dist_folder, f"{APP_NAME}.exe"))
        print(f" exe скопирован в: {dist_folder}/{APP_NAME}.exe")

if __name__ == "__main__":
    success = build_exe()
    
    if success:
        print("\n" + "="*50)
        print(f"Релиз версия 1.1.0 готова!")
        print(f" Файл: dist/{APP_NAME}.exe")
        print("="*50)
