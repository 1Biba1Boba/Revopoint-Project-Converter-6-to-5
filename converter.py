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
        revo_data['guid'] = self.project_name_without_prefix  # Step 8: guid in nodes section

        # Update nodes section
        for node in revo_data.get('nodes', []):
            node['guid'] = self.project_name_without_prefix  # Step 8
            node['name'] = self.project_name_without_prefix    # Step 9

        with open(revo_path, 'w', encoding='utf-8') as f:
            json.dump(revo_data, f, indent=4, ensure_ascii=False)

        return output_path


class ConverterApp:
    """GUI приложение для конвертера"""

    def __init__(self, root):
        self.root = root
        self.root.title("Revopoint 6 -> Revopoint 5 Конвертер")
        self.root.geometry("700x450")
        self.converter = RevopointConverter()

        # Variables for paths
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.progress_text = tk.StringVar(value="Готов к конвертации")

        self.create_widgets()
        self.center_window()

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
        # Title
        title_frame = tk.Frame(self.root)
        title_frame.pack(fill=tk.X, pady=10)

        title_label = tk.Label(title_frame, text="Revopoint 6 -> Revopoint 5", font=("Arial", 18, "bold"))
        title_label.pack()

        # Source folder selection
        source_frame = tk.Frame(self.root)
        source_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(source_frame, text="Исходная папка (Revopoint 6):", font=("Arial", 11)).pack(anchor=tk.W)
        path_row = tk.Frame(source_frame)
        path_row.pack(fill=tk.X, pady=(3, 0))

        self.source_entry = tk.Entry(path_row, textvariable=self.source_path, width=50)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        browse_btn = tk.Button(path_row, text="Выбрать", command=self.browse_source, width=12)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Output folder selection
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.X, padx=20, pady=5)

        tk.Label(output_frame, text="Папка для результата:", font=("Arial", 11)).pack(anchor=tk.W)
        path_row2 = tk.Frame(output_frame)
        path_row2.pack(fill=tk.X, pady=(3, 0))

        self.output_entry = tk.Entry(path_row2, textvariable=self.output_path, width=50)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        browse_btn2 = tk.Button(path_row2, text="Выбрать", command=self.browse_output, width=12)
        browse_btn2.pack(side=tk.RIGHT, padx=(5, 0))

        # Convert button
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=15)

        self.convert_btn = tk.Button(btn_frame, text="Конвертировать", command=self.start_conversion, width=30, height=2, font=("Arial", 14))
        self.convert_btn.pack()

        # Progress label
        progress_label = tk.Label(self.root, textvariable=self.progress_text, font=("Arial", 10), fg="#333")
        progress_label.pack(pady=5)

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
            messagebox.showerror("Ошибка", "Укажите обе папки!")
            return

        # Update UI
        self.progress_text.set("Конвертация...")
        self.convert_btn.config(state=tk.DISABLED)

        def update_progress(msg):
            self.root.after(0, lambda: self.progress_text.set(msg))

        try:
            converter = RevopointConverter()
            output_path = converter.convert(source, output, progress_callback=update_progress)
            messagebox.showinfo("Успех", f"Проект успешно конвертирован!\n\nРезультат:\n{output_path}")
            update_progress(f"Готово! Результат: {output_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
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