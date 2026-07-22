# Revopoint Converter 6to5

Преобразователь проектов из формата Revopoint 6 в формат Revopoint 5.

## Описание

**Revopoint Converter 6to5** — это утилита для конвертации проектов из программного обеспечения Revopoint (RevoCap) версии 6 в совместимый формат версии 5. Приложение позволяет легко и быстро преобразовать проекты без потери данных.

## Особенности

- Преобразование `.revox` файлов Revopoint 6 в `.revo` файлы Revopoint 5
- Автоматическое создание структуры проекта с правильной иерархией файлов
- Генерация `property.rvproj` с корректными GUID
- Графический интерфейс на базе tkinter
- Открытый исходный код (GPL v3)

## Версия

Текущая версия: **1.0.0**

## Требования

- Python 3.6+
- tkinter (включён в стандартную поставку Python)

## Установка

### Python версия

1. Клонируйте репозиторий:
```bash
git clone https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5.git
cd Revopoint-Project-Converter-6-to-5
```

2. Запустите приложение:
```bash
python converter.py
```

### EXE версия (Windows)

1. Скачайте `Revopoint-Converter-6to5.exe` из релизов
2. Запустите файл — приложение работает автономно без установки

## Сборка EXE

```bash
# Установите pyinstaller
pip install pyinstaller

# Соберите exe
pyinstaller --name "Revopoint-Converter-6to5" --onefile --windowed converter.py
```

Или используйте скрипт:
```bash
python build.py
```

## Использование

1. Запустите `converter.py` или `Revopoint-Converter-6to5.exe`
2. Нажмите **"Выбрать"** для исходной папки (содержит проект Revopoint 6)
3. Нажмите **"Выбрать"** для папки результата
4. Нажмите **"Конвертировать"**
5. Готово! Конвертированный проект будет сохранён в указанной папке

## Структура проекта

```
Revopoint-Project-Converter-6-to-5/
├── build.py            # Скрипт сборки exe
├── converter.py        # Основной модуль приложения
├── LICENSE             # Лицензия GPL v3
├── README.md           # Документация
├── pyproject.toml      # Metadata пакета
├── requirements.txt    # Зависимости
└── .gitignore          # Git игнор файлы
```

## Лицензия

Этот проект лицензирован по GNU General Public License v3 (GPLv3).
Вы можете распространять и изменять этот файл в соответствии с условиями лицензии.

## Author

Author: Cline (AI Assistant) / Revopoint-Project-Converter

## GitHub

Смотрите проект на [GitHub](https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5)