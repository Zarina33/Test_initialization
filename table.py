#!/usr/bin/env python3
import os
import logging
from pathlib import Path

# Настройка логирования: вывод в консоль и запись в файл
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("empty_files_check.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def check_empty_files(directory):
    """
    Рекурсивно проходит по директории и ищет пустые файлы.
    
    Файл считается пустым, если его размер равен 0 байт
    или если после удаления пробельных символов он оказывается пустым.
    
    Args:
        directory (str или Path): Путь к директории для проверки.
        
    Returns:
        list: Список путей пустых файлов.
    """
    empty_files = []
    directory = Path(directory)
    
    logging.info(f"Начинаем проверку файлов в директории: {directory}")
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                # Если размер файла 0 байт
                if file_path.stat().st_size == 0:
                    logging.info(f"Пустой файл (0 байт): {file_path}")
                    empty_files.append(file_path)
                else:
                    # Если файл содержит только пробельные символы
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if not content.strip():
                            logging.info(f"Файл содержит только пробелы: {file_path}")
                            empty_files.append(file_path)
            except Exception as e:
                logging.error(f"Ошибка при проверке файла {file_path}: {e}")
    
    logging.info(f"Проверка завершена. Найдено пустых файлов: {len(empty_files)}")
    return empty_files

if __name__ == "__main__":
    # Укажите путь к директории, в которой нужно проверить файлы
    output_directory = "/mnt/ks/Works/3nd_tests/extracted_text"
    empty_files = check_empty_files(output_directory)


    
