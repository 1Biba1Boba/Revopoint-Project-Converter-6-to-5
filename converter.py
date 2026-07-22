__version__ = "1.1.0"

APP_NAME = "Revopoint Converter 6to5"
APP_VERSION = "1.1.0"

import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class RevopointConverter:
    """Конвертер проектов Revopoint 6 -> Revopoint 5"""

    def __init__(self):
        self.project_name = ""
        self.project_name_without_prefix = ""

    def extract_project_name(self, revox_filename):
        """Извлекаем название проекта из имени файла .revox (убираем расширение)"""
        return os.path.splitext(revox_filename)[0]

    def create_template_revo(self, project_name):
        """Создаём шаблон .revo файла для версии 5"""
        template = {
            "edit_time": "",
            "guid": "",
            "model_mesh_count": 1,
            "model_pointcloud_count": 0,
            "name": project_name,
            "nodes": [
                {
                    "childs": [],
                    "guid": self.project_name_without_prefix,
                    "name": self.project_name_without_prefix,
                    "type": 2
                }
            ],
            "scan_scene": {},
            "size": "",
            "version": "2.0"
        }
        return template

    def create_template_property(self, project_name_without_prefix):
        """Создаём шаблон property.rvproj файла"""
        template = {
            "can_fuse_optimize": True,
            "clip_marker_ratio": 0,
            "edit_time": "",
            "face_count": 0,
            "fuse_file": "fuse.ply",
            "fuse_type": 2,
            "guid": project_name_without_prefix,
            "mesh_file": "fuse_mesh_rgb.ply",
            "mesh_level_max": 7,
            "mesh_level_min": 1,
            "param_index": 1,
            "point_count": 0,
            "point_pitch": 1.5,
            "point_pitch_max": 2,
            "point_pitch_min": 0.1000000014901161,
            "project_mode": 0,
            "rotate_state": True,
            "scan_algo_param": {
                "algo_type": 1,
                "algo_ver": "1.0.0"
            },
            "scan_device": "RANGE",
            "scan_param": {
                "accuracy_type": 1,
                "color_height": 0,
                "color_type": 1,
                "color_width": 0,
                "depth_height": 400,
                "depth_scale": 0.1000000014901161,
                "depth_width": 640,
                "ir_height": 400,
                "ir_width": 640,
                "scan_mode": 1,
                "scan_object": 0,
                "scanner_sn": ""
            },
            "scan_step": 4,
            "source_type": 1,
            "texture_file": "fuse_mesh_tex.ply",
            "version": "2.0",
            "vertex_count": 0,
            "vf_count": 360
        }
        return template

    def find_revox_file(self, source_folder):
        """Находим .revox файл в исходной папке"""
        for root, dirs, files in os.walk(source_folder):
            for f in files:
                if f.endswith('.revox'):
                    return os.path.join(root, f)
        # Also check top level
        for f in os.listdir(source_folder):
            if f.endswith('.revox'):
                return os.path.join(source_folder, f)
        return None

    def copy_files_except(self, src, dst, exclude=None):
        """Копируем все файлы кроме исключённых"""
        if exclude is None:
            exclude = []

        for item in os.listdir(src):
            if item in exclude:
                continue
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    def convert(self, source_folder, output_path, progress_callback=None):
        """Основная логика конвертации"""
        # Step 0: Find .revox file and extract project name
        revox_file = self.find_revox_file(source_folder)
        if revox_file is None:
            raise ValueError(f"Не найден .revox файл в папке: {source_folder}")

        revox_filename = os.path.basename(revox_file)
        self.project_name_without_prefix = self.extract_project_name(revox_filename)
        self.project_name = f"project{self.project_name_without_prefix}"

        # Step 1: Create output project folder
        os.makedirs(output_path, exist_ok=True)

        # Step 2: Create .revo template file
        revo_template = self.create_template_revo(self.project_name)
        revo_path = os.path.join(output_path, f"{self.project_name}.revo")
        with open(revo_path, 'w', encoding='utf-8') as f:
            json.dump(revo_template, f, indent=4, ensure_ascii=False)

        # Step 3: Create data folder
        data_path = os.path.join(output_path, "data")
        os.makedirs(data_path, exist_ok=True)

        # Step 4: Create project-named subfolder inside data
        data_project_path = os.path.join(data_path, self.project_name_without_prefix)
        os.makedirs(data_project_path, exist_ok=True)

        # Step 5: Copy all source files to data/project_folder
        exclude_files = []  # We don't need to exclude anything special
        self.copy_files_except(source_folder, data_project_path, exclude_files)

        # Step 6 & 7: Create property.rvproj with correct guid
        prop_template = self.create_template_property(self.project_name_without_prefix)
        prop_path = os.path.join(data_project_path, "property.rvproj")
        with open(prop_path, 'w', encoding='utf-8') as f:
            json.dump(prop_template, f, indent=4, ensure_ascii=False)

        # Step 8 & 9: Update .revo file with correct guid and name in nodes section
        # (Already done in create_template_revo, but let's make sure)
        with open(revo_path, 'r', encoding='utf-8') as f:
            revo_data = json.load(f)

        # Update top-level fields
        revo_data['name'] = self.project_name  # Step 7: name with "project" prefix

        # Update nodes section (Step 8 & 9: guid and name only inside nodes)
        for node in revo_data.get('nodes', []):
            node['guid'] = self.project_name_without_prefix   # Step 8: guid in nodes section
            node['name'] = self.project_name_without_prefix    # Step 9: name in nodes section

        with open(revo_path, 'w', encoding='utf-8') as f:
            json.dump(revo_data, f, indent=4, ensure_ascii=False)

        return output_path


class ConverterApp:
    """GUI приложение для конвертера"""

    def __init__(self, root):
        self.root = root
        self.lang = "ru"  # Default language is Russian
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.progress_text = tk.StringVar(value=self._t("ready"))

        # Fix 1: Set title immediately after setting default language
        self.root.title(self._t("title"))

        # Store button references for later update
        self.ru_btn = None
        self.en_btn = None
        self.zh_btn = None
        self.contact_btn = None
        self.instructions_btn = None

        self.converter = RevopointConverter()
        self.create_widgets()
        self.center_window()

    def _t(self, key):
        """Translate UI strings based on current language"""
        translations = {
            "title": {
                "ru": "Revopoint 6 -> Revopoint 5 Конвертер",
                "en": "Revopoint 6 -> Revopoint 5 Converter",
                "zh": "Revopoint 6 \u2013> Revopoint 5 \u8f6c\u63db\u5668"
            },
            "ready": {
                "ru": "\u0413\u043e\u0442\u043e\u0432 \u043a \u043a\u043e\u043d\u0432\u0435\u0440\u0442\u0430\u0446\u0438\u0438",
                "en": "Ready to convert",
                "zh": "\u9ecf\u6e90\u8f2c\u63db"
            },
            "contact": {
                "ru": "\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u044b \u0430\u0432\u0442\u043e\u0440\u0430",
                "en": "Author Contacts",
                "zh": "\u4f5c\u8005\u8054\u7cfb\u65b9\u5f0f"
            },
            "instructions": {
                "ru": "\u0418\u043d\u0441\u0442\u0440\u0443\u043a\u0446\u0438\u044f",
                "en": "Instructions",
                "zh": "\u4f7f\u7528\u8bf4\u660e"
            },
            "source_folder": {
                "ru": "\u0418\u0441\u0445\u043e\u0434\u043d\u0430\u044f \u043f\u0430\u043f\u043a\u0430 (Revopoint 6):",
                "en": "Source folder (Revopoint 6):",
                "zh": "\u6e90\u6587\u4ef6\u5939\uff08Revopoint 6\uff1a"
            },
            "output_folder": {
                "ru": "\u041f\u0430\u043f\u043a\u0430 \u0434\u043b\u044f \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u0430 (Revopoint 5):",
                "en": "Output folder (Revopoint 5):",
                "zh": "\u8f3a\u51fa\u6587\u4ef6\u5939\uff08Revopoint 5\uff1a"
            },
            "browse": {
                "ru": "\u0412\u044b\u0431\u0440\u0430\u0442\u044c",
                "en": "Browse",
                "zh": "\u9075"
            },
            "convert": {
                "ru": "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c",
                "en": "Convert",
                "zh": "\u8f6c\u63db"
            },
            "converting": {
                "ru": "\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0430\u0446\u0438\u044f...",
                "en": "Converting...",
                "zh": "\u8f6c\u63db\u4e2d..."
            },
            "success_title": {
                "ru": "\u0423\u0441\u043f\u0435\u0445",
                "en": "Success",
                "zh": "\u6210\u529f"
            },
            "success_message": {
                "ru": "\u041f\u0440\u043e\u0435\u043a\u0442 \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u043a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u043d!",
                "en": "Project successfully converted!",
                "zh": "\u9810\u675f\u8f6c\u63db\u6210\u529f\uff01"
            },
            "error_title": {
                "ru": "\u041e\u0448\u0438\u0431\u043a\u0430",
                "en": "Error",
                "zh": "\u9324\u8aa4"
            },
            "error_both_folders": {
                "ru": "\u0423\u043a\u0430\u0436\u0438\u0442\u0435 \u043e\u0431\u0435 \u043f\u0430\u043f\u043a\u0438!",
                "en": "Specify both folders!",
                "zh": "\u6307\u5b9a\u6587\u4ef6\u5939\uff01"
            },
            "contact_info": {
                "ru": "Email: vanyagubarev@yandex.ru\nTelegram: https://t.me/qwerty918\nGitHub: https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5",
                "en": "Email: vanyagubarev@yandex.ru\nTelegram: https://t.me/qwerty918\nGitHub: https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5",
                "zh": "\u00a9\u00e4\u00b7\u00e4\u00b7\u00e4\u00b7: vanyagubarev@yandex.ru\nTelegram: https://t.me/qwerty918\nGitHub: https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5"
            },
            "instructions_text": {
                "ru": "\u041a\u0430\u043a \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c\u0441\u044f:\n\n1. \u041d\u0430\u0436\u043c\u0435\u0442\u0435 '\u0412\u044b\u0431\u0440\u0430\u0442\u044c' \u0443 \u043f\u043e\u043b\u044f '\u0418\u0441\u0445\u043e\u0434\u043d\u0430\u044f \u043f\u0430\u043f\u043a\u0430 (Revopoint 6)' \u0438 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0441 \u043f\u0440\u043e\u0435\u043a\u0442\u043e\u043c \u0432\u0435\u0440\u0441\u0438\u0438 6\n\n2. \u041d\u0430\u0436\u043c\u0435\u0442\u0435 '\u0412\u044b\u0431\u0440\u0430\u0442\u044c' \u0443 \u043f\u043e\u043b\u044f 'Папка для результата (Revopoint 5)' \u0438 \u0432\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043c\u0435\u0441\u0442\u043e \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f\n\n3. \u041d\u0430\u0436\u043c\u0435\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 '\u041a\u043e\u043d\u0432\u0435\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c'\n\n4. \u0414\u043e\u0436\u0434\u0438\u0442\u0435\u0441\u044c \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0438\u044f \u2014 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442 \u043f\u043e\u044f\u0432\u0438\u0442\u0441\u044f \u0432 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u0439 \u043f\u0430\u043f\u043a\u0435",
                "en": "How to use:\n\n1. Click 'Browse' next to 'Source folder (Revopoint 6)' and select a version 6 project folder.\n\n2. Click 'Browse' next to 'Output folder (Revopoint 5)' and choose where to save the result.\n\n3. Click the 'Convert' button.\n\n4. Wait for completion - the converted result will appear in the selected folder.",
                "zh": "\u601e\u7528\uff1a\n\n1. \u9ede\u64ca\u201c\u6e90\u6587\u4ef6\u5939\uff08Revopoint 6\uff1a\u201d\u65c1\u7684\u201c\u9075\u201d\u6309\u94e5\uff0c\u9075\u64c0\u7248\u672c 6 \u7684\u9810\u675f\u6587\u4ef6\u5939\u3002\n\n2. \u9ede\u64ca\u201c\u8f3a\u51fa\u6587\u4ef6\u5939\uff08Revopoint 5\uff1a\u201d\u65c1\u7684\u201c\u9075\u201d\u6309\u94e5\uff0c\u9075\u64c0\u4fdd\u5b58\u4f4d\u7f6e\u3002\n\n3. \u9ede\u64ca\u201c\u8f6c\u63db\u201d\u6309\u94e5\u3002\n\n4. \u7b49\u5f85\u5b8c\u6210\uff0d\u8f6c\u63db\u7d50\u679c\u5c07\u51fa\u73fe\u5728\u6240\u9075\u7684\u6587\u4ef6\u5939\u4e2d\u3002"
            },
            "made_with": {
                "ru": "Сделано с помощью LLM Qwen3.6 35B A3B UD, среды VS Code и расширения Cline. Спасибо ИИ!",
                "en": "Made with LLM Qwen3.6 35B A3B UD, VS Code environment and Cline extension. Thanks AI!",
                "zh": "\u4f7f\u7528 Qwen3.6 35B A3B UD LLM\u3001VS Code\u73af\u5883\u548c Cline\u6269\u5c55\u5236\u6210\u3002\u8c22\u8c22\u4eba\u5de5\u667a\u80fd\uff01"
            }
        }
        if key in translations and self.lang in translations[key]:
            return translations[key][self.lang]
        return key

    def set_language(self, lang_code):
        """Change UI language"""
        self.lang = lang_code
        self.root.title(self._t("title"))
        self.progress_text.set(self._t("ready"))
        self.update_lang_buttons()
        # Update all text labels
        self._update_texts()

    def _update_texts(self):
        """Update all text elements without recreating widgets"""
        if hasattr(self, 'title_label') and self.title_label:
            self.title_label.config(text=self._t("title"))
        if hasattr(self, 'source_label') and self.source_label:
            self.source_label.config(text=self._t("source_folder"))
        if hasattr(self, 'output_label') and self.output_label:
            self.output_label.config(text=self._t("output_folder"))
        if hasattr(self, 'browse_btn_source') and self.browse_btn_source:
            self.browse_btn_source.config(text=self._t("browse"))
        if hasattr(self, 'browse_btn_output') and self.browse_btn_output:
            self.browse_btn_output.config(text=self._t("browse"))
        if hasattr(self, 'convert_btn') and self.convert_btn:
            self.convert_btn.config(text=self._t("convert"))
        if hasattr(self, 'contact_btn') and self.contact_btn:
            self.contact_btn.config(text=self._t("contact"))
        if hasattr(self, 'instructions_btn') and self.instructions_btn:
            self.instructions_btn.config(text=self._t("instructions"))

    def update_lang_buttons(self):
        """Update language button appearance"""
        if not hasattr(self, '_lang_buttons'):
            return
        for btn in self._lang_buttons:
            btn.config(bg="#FFFFFF", fg="#333333")
        if self.lang == "ru":
            self.ru_btn.config(bg="#4CAF50", fg="white")
        elif self.lang == "en":
            self.en_btn.config(bg="#4CAF50", fg="white")
        elif self.lang == "zh":
            self.zh_btn.config(bg="#4CAF50", fg="white")

    def open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)

    def show_contact(self):
        """Show author contacts dialog with clickable links"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self._t("contact"))
        dialog.geometry("500x380")
        dialog.resizable(False, False)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg="#F5F5F5", pady=10, padx=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Email link
        email_label = tk.Label(main_frame, text="Email:", font=("Arial", 10, "bold"), bg="#F5F5F5", fg="#424242", anchor=tk.W)
        email_label.pack(fill=tk.X, pady=(0, 5))
        email_link = tk.Label(main_frame, text="mailto:vanyagubarev@yandex.ru", font=("Arial", 11), bg="#E3F2FD", fg="#1563C0", cursor="hand2", anchor=tk.W)
        email_link.pack(fill=tk.X, pady=(0, 10))
        email_link.bind("<Button-1>", lambda e: self.open_url("mailto:vanyagubarev@yandex.ru"))

        # Telegram link
        telegram_label = tk.Label(main_frame, text="Telegram:", font=("Arial", 10, "bold"), bg="#F5F5F5", fg="#424242", anchor=tk.W)
        telegram_label.pack(fill=tk.X, pady=(0, 5))
        telegram_link = tk.Label(main_frame, text="https://t.me/qwerty918", font=("Arial", 11), bg="#E3F2FD", fg="#1563C0", cursor="hand2", anchor=tk.W)
        telegram_link.pack(fill=tk.X, pady=(0, 10))
        telegram_link.bind("<Button-1>", lambda e: self.open_url("https://t.me/qwerty918"))

        # GitHub link
        github_label = tk.Label(main_frame, text="GitHub:", font=("Arial", 10, "bold"), bg="#F5F5F5", fg="#424242", anchor=tk.W)
        github_label.pack(fill=tk.X, pady=(0, 5))
        github_link = tk.Label(main_frame, text="https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5", font=("Arial", 11), bg="#E3F2FD", fg="#1563C0", cursor="hand2", anchor=tk.W)
        github_link.pack(fill=tk.X, pady=(0, 10))
        github_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/1Biba1Boba/Revopoint-Project-Converter-6-to-5"))

        # Fix 3: "Made with LLM" attribution line
        made_with_label = tk.Label(main_frame, text=self._t("made_with"), font=("Arial", 9), bg="#F5F5F5", fg="#888888", anchor=tk.W, wraplength=460)
        made_with_label.pack(fill=tk.X, pady=(10, 5))

        # Close button
        close_btn = tk.Button(main_frame, text="OK", command=dialog.destroy, bg="#4CAF50", fg="white", bd=2, relief=tk.RAISED, font=("Arial", 10, "bold"), cursor="hand2")
        close_btn.pack(pady=(10, 0))

    def show_instructions(self):
        """Show instructions dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(self._t("instructions"))
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.grab_set()

        main_frame = tk.Frame(dialog, bg="#F5F5F5", pady=10, padx=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        instructions_text = self._t("instructions_text")
        label = tk.Label(main_frame, text=instructions_text, font=("Arial", 10), bg="#F5F5F5", fg="#333333", anchor=tk.W, justify=tk.LEFT, wraplength=460)
        label.pack(fill=tk.X, pady=(0, 10))

        close_btn = tk.Button(main_frame, text="OK", command=dialog.destroy, bg="#4CAF50", fg="white", bd=2, relief=tk.RAISED, font=("Arial", 10, "bold"), cursor="hand2")
        close_btn.pack(pady=(10, 0))

    def center_window(self):
        """Центрируем окно на экране"""
        window_width = 700
        window_height = 450
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def create_widgets(self):
        """Создаём элементы интерфейса"""
        # Main container frame with padding and background
        main_frame = tk.Frame(self.root, bg="#F5F5F5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top frame for language buttons and action buttons
        top_frame = tk.Frame(main_frame, bg="#F5F5F5", pady=10)
        top_frame.pack(fill=tk.X)

        # Language buttons frame (left side)
        lang_frame = tk.Frame(top_frame, bg="#F5F5F5")
        lang_frame.pack(side=tk.LEFT)

        self.ru_btn = tk.Button(lang_frame, text="Русский", width=14, command=lambda: self.set_language("ru"), bg="#FFFFFF", fg="#333333", bd=2, relief=tk.GROOVE, font=("Arial", 10))
        self.en_btn = tk.Button(lang_frame, text="English", width=14, command=lambda: self.set_language("en"), bg="#FFFFFF", fg="#333333", bd=2, relief=tk.GROOVE, font=("Arial", 10))
        self.zh_btn = tk.Button(lang_frame, text="\u4e2d\u6587", width=14, command=lambda: self.set_language("zh"), bg="#FFFFFF", fg="#333333", bd=2, relief=tk.GROOVE, font=("Arial", 10))

        self.ru_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.en_btn.pack(side=tk.LEFT, padx=(5, 0))
        self.zh_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Store references for update_lang_buttons
        self._lang_buttons = [self.ru_btn, self.en_btn, self.zh_btn]

        # Right side buttons frame (contact + instructions)
        right_frame = tk.Frame(top_frame, bg="#F5F5F5")
        right_frame.pack(side=tk.RIGHT)

        self.contact_btn = tk.Button(right_frame, text=self._t("contact"), width=18, command=self.show_contact, bg="#E3F2FD", fg="#1563C0", bd=2, relief=tk.RAISED, font=("Arial", 10, "bold"))
        self.contact_btn.pack(side=tk.LEFT, padx=(5, 0))

        self.instructions_btn = tk.Button(right_frame, text=self._t("instructions"), width=18, command=self.show_instructions, bg="#E3F2FD", fg="#1563C0", bd=2, relief=tk.RAISED, font=("Arial", 10, "bold"))
        self.instructions_btn.pack(side=tk.LEFT)

        # Update language buttons appearance based on current language
        self.update_lang_buttons()

        # Title frame with background
        title_frame = tk.Frame(main_frame, bg="#F5F5F5", pady=10)
        title_frame.pack(fill=tk.X)

        self.title_label = tk.Label(title_frame, text=self._t("title"), font=("Arial", 20, "bold"), fg="#1976D8", bg="#F5F5F5")
        self.title_label.pack()

        # Source folder selection with styled frame
        source_frame = tk.Frame(main_frame, bg="#F5F5F5", pady=5)
        source_frame.pack(fill=tk.X, padx=30)

        self.source_label = tk.Label(source_frame, text=self._t("source_folder"), font=("Arial", 12, "bold"), fg="#424242", bg="#F5F5F5")
        self.source_label.pack(anchor=tk.W)

        path_row = tk.Frame(source_frame, bg="#F5F5F5")
        path_row.pack(fill=tk.X, pady=(3, 0))

        self.source_entry = tk.Entry(path_row, textvariable=self.source_path, width=45, font=("Arial", 11), bg="#FFFFFF", fg="#333333", relief=tk.GROOVE, bd=2)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_btn_source = tk.Button(path_row, text=self._t("browse"), command=self.browse_source, width=10, bg="#4CAF50", fg="white", bd=2, relief=tk.FLAT, font=("Arial", 10, "bold"))
        self.browse_btn_source.pack(side=tk.RIGHT, padx=(5, 0))

        # Output folder selection with styled frame
        output_frame = tk.Frame(main_frame, bg="#F5F5F5", pady=5)
        output_frame.pack(fill=tk.X, padx=30)

        self.output_label = tk.Label(output_frame, text=self._t("output_folder"), font=("Arial", 12, "bold"), fg="#424242", bg="#F5F5F5")
        self.output_label.pack(anchor=tk.W)

        path_row2 = tk.Frame(output_frame, bg="#F5F5F5")
        path_row2.pack(fill=tk.X, pady=(3, 0))

        self.output_entry = tk.Entry(path_row2, textvariable=self.output_path, width=45, font=("Arial", 11), bg="#FFFFFF", fg="#333333", relief=tk.GROOVE, bd=2)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.browse_btn_output = tk.Button(path_row2, text=self._t("browse"), command=self.browse_output, width=10, bg="#4CAF50", fg="white", bd=2, relief=tk.FLAT, font=("Arial", 10, "bold"))
        self.browse_btn_output.pack(side=tk.RIGHT, padx=(5, 0))

        # Convert button - prominent styling
        convert_frame = tk.Frame(main_frame, bg="#F5F5F5")
        convert_frame.pack(pady=15)

        self.convert_btn = tk.Button(convert_frame, text=self._t("convert"), command=self.start_conversion, width=35, height=2, font=("Arial", 14, "bold"), bg="#1976D8", fg="white", bd=3, relief=tk.RAISED, cursor="hand2")
        self.convert_btn.pack()

        # Progress label with styled appearance
        progress_label = tk.Label(main_frame, textvariable=self.progress_text, fg="#757575", font=("Arial", 9), bg="#F5F5F5")
        progress_label.pack(pady=(5, 10))

        # Fix 4: Add version info label at bottom (like in v1.0.0)
        version_label = tk.Label(main_frame, text=f"Версия {APP_VERSION} | Revopoint 6 -> Revopoint 5", font=("Arial", 9), bg="#F5F5F5", fg="#888888")
        version_label.pack(pady=(0, 5))

    def browse_source(self):
        """Выбираем исходную папку"""
        path = filedialog.askdirectory(title="Выберите исходную папку проекта Revopoint 6")
        if path:
            self.source_path.set(path)

    def browse_output(self):
        """Выбираем папку для результата"""
        path = filedialog.askdirectory(title="Выберите папку для сохранения конвертированного проекта")
        if path:
            self.output_path.set(path)

    def start_conversion(self):
        """Запускаем конвертацию"""
        source = self.source_path.get()
        output = self.output_path.get()

        if not source or not output:
            # Fix 2: Use translations for error message
            messagebox.showerror(self._t("error_title"), self._t("error_both_folders"))
            return

        # Update UI
        self.progress_text.set(self._t("converting"))
        self.convert_btn.config(state=tk.DISABLED)

        def update_progress(msg):
            self.root.after(0, lambda: self.progress_text.set(msg))

        try:
            converter = RevopointConverter()
            output_path = converter.convert(source, output, progress_callback=update_progress)
            messagebox.showinfo(self._t("success_title"), f"{self._t('success_message')}\n\nРезультат:\n{output_path}")
            update_progress(f"{self._t('ready')}! Результат: {output_path}")
        except Exception as e:
            messagebox.showerror(self._t("error_title"), str(e))
            update_progress(self._t("error"))
            update_progress("Ошибка!")

        self.convert_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    # Disable window resizing
    root.resizable(False, False)
    app = ConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()