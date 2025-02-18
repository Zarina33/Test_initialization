#!/usr/bin/env python3

import os
import shutil
import json
from pathlib import Path

def load_json(json_file):
    """
    Загружает данные из JSON-файла.
    Ожидается, что файл содержит объект с ключом "errors", значением которого является список строк.
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Ошибка загрузки JSON: {e}")
        return None

def copy_directories_from_json(json_file, source_base, target_base):
    """
    Из JSON-файла выбирает пути к файлам и копирует всю директорию, в которой они находятся,
    в новую целевую директорию, сохраняя относительный путь.
    
    Аргументы:
      json_file    - путь к JSON-файлу, содержащему список сообщений вида:
                     "Skipped empty JSON file: /mnt/ks/Works/3nd_tests/ready(last)/.../S-10-026/..."
      source_base  - базовая директория исходных данных, например, "/mnt/ks/Works/3nd_tests/ready(last)"
      target_base  - базовая директория для копирования, например, "/mnt/ks/Works/3nd_tests/copied_dirs"
    """
    data = load_json(json_file)
    if data is None:
        return

    errors = data.get("errors")
    if not errors or not isinstance(errors, list):
        print("В JSON-файле отсутствует ключ 'errors' или он имеет неверный формат.")
        return

    # Множество для хранения уникальных директорий (извлечённых из путей)
    dirs_to_copy = set()
    prefix = "Skipped empty JSON file: "

    for entry in errors:
        if not entry.startswith(prefix):
            continue
        # Извлекаем путь после префикса
        file_path = entry[len(prefix):].strip()
        # Определяем родительскую директорию файла
        parent_dir = os.path.dirname(file_path)
        dirs_to_copy.add(parent_dir)

    # Копирование найденных директорий
    for src_dir in dirs_to_copy:
        try:
            # Вычисляем относительный путь от source_base
            rel_path = os.path.relpath(src_dir, source_base)
        except Exception as e:
            print(f"Не удалось вычислить относительный путь для {src_dir}: {e}")
            continue

        target_dir = os.path.join(target_base, rel_path)
        print(f"Копирование директории:\n  Источник: {src_dir}\n  Назначение: {target_dir}")
        
        try:
            # Создаём промежуточные директории, если необходимо
            os.makedirs(os.path.dirname(target_dir), exist_ok=True)
            # Копируем всю директорию (с версии Python 3.8 можно использовать dirs_exist_ok=True)
            shutil.copytree(src_dir, target_dir, dirs_exist_ok=True)
        except Exception as e:
            print(f"Ошибка при копировании {src_dir} в {target_dir}: {e}")

if __name__ == "__main__":
    # Задайте пути:
    # JSON-файл с данными (обязательно должен быть корректный JSON-объект, например:
    # { "errors": [ "Skipped empty JSON file: /mnt/ks/Works/3nd_tests/ready(last)/Геометрия 10 класс/Кырг версия/S-10-026/S-10-026-T-kg.json", ... ] }
    json_file = "/mnt/ks/Works/3nd_tests/Errors_updated.json"
    
    # Исходная база данных
    source_base = "/mnt/ks/Works/3nd_tests/ready(last)"
    # Целевая база для копирования директорий
    target_base = "/mnt/ks/Works/3nd_tests/errors_folder"
    os.makedirs(target_base, exist_ok=True)
    
    copy_directories_from_json(json_file, source_base, target_base)
    print("Обработка завершена")

