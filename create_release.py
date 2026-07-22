"""
Скрипт для создания GitHub Release с EXS файлом
"""

import json
import os
import requests

GITHUB_TOKEN = "YOUR_TOKEN_HERE"
GITHUB_REPO = "1Biba1Boba/Revopoint-Project-Converter-6-to-5"
RELEASE_TAG = "v1.1.0"
RELEASE_NAME = "Revopoint Converter 6to5 v1.1.0"

RELEASE_BODY = """\
## 🎉 Revopoint Converter 6to5 v1.1.0 - Обновление с мультиязычным интерфейсом!

Второй релиз инструмента для конвертации проектов Revopoint с улучшенным UI и мультиязычной поддержкой.

### ✨ Что нового в v1.1.0
- **Мультиязычный интерфейс**: поддержка 3 языков (русский 🇷🇺, английский 🇺🇸, китайский 🇨🇳)
- **Динамическое переключение языков**: кнопки RU/EN/ZH для мгновенной смены языка
- **Диалог контактов автора**: кликабельные ссылки на Email, Telegram, GitHub
- **Диалог инструкций**: пошаговое руководство по использованию на 3 языках
- **Обновлённый дизайн**: стильный UI с улучшенной цветовой палитрой (#F5F5F5 фон, #1976D8 синий, #4CAF50 зелёный)
- **Фиксы**: исправлено отображение заголовка, перевод ошибок, указание версии в интерфейсе
### 🔧 Что исправлено
- Исправлена ошибка "tk" вместо названия приложения при запуске
- Исправлены сообщения об ошибках на выбранном языке
- Добавлена строка "Сделано с помощью ИИ" в контакты автора
- Добавлена метка версии в нижнюю часть окна

### 📋 Как использовать
1. Запустите `Revopoint-Converter-6to5.exe`
2. Нажмите **"Выбрать"** для исходной папки (содержит проект Revopoint 6)
3. Нажмите **"Выбрать"** для папки результата
4. Нажмите **"Конвертировать"**
5. Готово! Конвертированный проект будет сохранён в указанной папке

### 💻 Системные требования
- Windows 10+
- Python 3.6+ (если собираете из источника)

### 🔧 Сборка из источника
```bash
pip install pyinstaller
pyinstaller --name Revopoint-Converter-6to5 --onefile --windowed converter.py
```

Или используйте скрипт:
```bash
python build.py
```

### 📄 License
GNU General Public License v3 (GPLv3)

### 🔗 Ссылки
- **GitHub**: https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5
"""

def create_release():
    """Создает GitHub Release через API"""
    
    # Шаг 1: Проверяем, существует ли уже release
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
    get_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Проверяем существующий release
    print(f"Проверяем существующий Release {RELEASE_TAG}...")
    check_response = requests.get(get_url, headers=headers)
    
    if check_response.status_code == 200:
        print(f"Release уже существует!")
        release_data = check_response.json()
    elif check_response.status_code == 404:
        print(f"Создаем новый Release {RELEASE_TAG}...")
        # Создаем новый release
        data = {
            "tag_name": RELEASE_TAG,
            "target_commitish": "main",
            "name": RELEASE_NAME,
            "body": RELEASE_BODY,
            "draft": False,
            "prerelease": False
        }
        
        headers_with_json = headers.copy()
        headers_with_json["Content-Type"] = "application/json"
        response = requests.post(api_url, headers=headers_with_json, json=data)
        
        if response.status_code != 201:
            print(f"Ошибка создания release:\n{response.status_code}\n{response.text}")
            return False
        
        release_data = response.json()
    else:
        print(f"Ошибка проверки release: {check_response.status_code}\n{check_response.text}")
        return False
    
    print(f"Release доступен: https://github.com/{GITHUB_REPO}/releases/tag/{RELEASE_TAG}")
    
    # Шаг 2: Загружаем EXE файл
    print("\nЗагружаем Revopoint-Converter-6to5.exe...")
    
    exe_path = os.path.join("dist", "Revopoint-Converter-6to5.exe")
    upload_url = release_data.get("upload_url", "")
    
    if not upload_url:
        print("Нет upload URL")
        return False
    
    # GitHub upload URL format: https://uploads.github.com/repos/.../releases/{id}/assets{?name,label}
    # Need to construct proper upload URL with filename
    import re
    
    with open(exe_path, 'rb') as f:
        exe_content = f.read()
    
    print(f"Файл размером: {len(exe_content)} байт ({len(exe_content)/1024/1024:.2f} MB)")
    
    # Extract release ID and construct proper upload URL
    # Pattern: https://uploads.github.com/repos/owner/repo/releases/12345/assets{?name,label}
    upload_url_pattern = r'(https://uploads\.github\.com/repos/[^/]+/[^/]+/releases/(\d+)/assets)\{[^}]+\}'
    match = re.search(upload_url_pattern, upload_url)
    
    if not match:
        print(f"Не удалось парсить upload URL: {upload_url}")
        return False
    
    release_id = match.group(2)
    
    # Construct the proper upload URL
    proper_upload_url = f"https://uploads.github.com/repos/{GITHUB_REPO}/releases/{release_id}/assets?name=Revopoint-Converter-6to5.exe"
    
    print(f"Proper Upload URL: {proper_upload_url}")
    
    from io import BytesIO
    from mimetypes import guess_type
    
    file_like = BytesIO(exe_content)
    file_like.seek(0)
    
    content_type, _ = guess_type('Revopoint-Converter-6to5.exe')
    content_type = content_type or 'application/octet-stream'
    
    files = {
        'file': (
            'Revopoint-Converter-6to5.exe',
            file_like,
            content_type
        )
    }
    
    upload_headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
    }
    
    print(f"Загрузка файла (11.46 MB)...")
    upload_response = requests.post(
        proper_upload_url,
        headers=upload_headers,
        files=files
    )
    
    print(f"Upload status: {upload_response.status_code}")
    
    if upload_response.status_code not in (200, 201, 202, 204):
        print(f"Ошибка загрузки файла: {upload_response.status_code}")
        print(f"Response: {upload_response.text}")
        return False
    
    print("✅ EXE файл загружен на GitHub!")
    print(f"✅ Release готов: https://github.com/{GITHUB_REPO}/releases/tag/{RELEASE_TAG}")
    print(f"📥 Ссылка для скачивания: https://github.com/{GITHUB_REPO}/releases/download/v1.1.0/Revopoint-Converter-6to5.exe")
    return True

if __name__ == "__main__":
    # Проверим есть ли requests
    try:
        import requests
    except ImportError:
        print("Устанавливаю requests...")
        import subprocess
        subprocess.run(["pip", "install", "requests"])
        import requests
    
    success = create_release()
    
    if success:
        print("\n" + "="*50)
        print(f"GitHub Release v1.1.0 создан успешно!")
        print(f"Ссылка: https://github.com/{GITHUB_REPO}/releases/tag/v1.1.0")
        print("="*50)
