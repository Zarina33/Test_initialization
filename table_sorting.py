#!/usr/bin/env python3

import os
import shutil
from docx import Document
from pathlib import Path

def check_for_tables(source_path):
    """
    Проверяет, содержит ли .docx файл таблицы.
    """
    try:
        doc = Document(source_path)
        has_tables = len(doc.tables) > 0
        print(f"Checked {source_path}: {'Has tables' if has_tables else 'No tables'}")
        return has_tables
    except Exception as e:
        print(f"Error checking tables in {source_path}: {str(e)}")
        return False

def move_directory_with_content(source_dir, tables_dir):
    """
    Перемещает всё содержимое папки, если в ней есть .docx файл с таблицами.
    """
    # Список для отслеживания уже обработанных папок
    processed_dirs = set()

    for root, dirs, files in os.walk(source_dir):
        # Пропускаем уже обработанные папки
        if root in processed_dirs:
            continue

        # Проверяем только .docx файлы в текущей папке
        docx_files = [f for f in files if f.endswith('.docx')]
        has_table_in_folder = False

        # Проверяем, есть ли хотя бы один .docx файл с таблицами
        for docx_file in docx_files:
            docx_path = os.path.join(root, docx_file)
            if check_for_tables(docx_path):
                has_table_in_folder = True
                break  # Достаточно найти хотя бы один файл с таблицами

        # Если найден .docx файл с таблицами, перемещаем всё содержимое папки
        if has_table_in_folder:
            source_doc_dir = root
            rel_path = os.path.relpath(source_doc_dir, source_dir)
            target_path = os.path.join(tables_dir, rel_path)
            os.makedirs(target_path, exist_ok=True)

            print(f"Processing directory: {source_doc_dir}")
            for item in os.listdir(source_doc_dir):
                src_item = os.path.join(source_doc_dir, item)
                dst_item = os.path.join(target_path, item)
                if os.path.isfile(src_item):
                    print(f"Moving file: {src_item} -> {dst_item}")
                    shutil.move(src_item, dst_item)
                elif os.path.isdir(src_item):
                    print(f"Moving directory: {src_item} -> {dst_item}")
                    shutil.move(src_item, dst_item)

            # Добавляем папку в список обработанных
            processed_dirs.add(source_doc_dir)

# Основная часть программы
source_dir = Path("/mnt/ks/Works/3nd_tests/ready(last)")
tables_dir = Path("/mnt/ks/Works/3nd_tests/tables")
os.makedirs(tables_dir, exist_ok=True)

# Запуск скрипта
move_directory_with_content(source_dir, tables_dir)
print("Processing completed")

