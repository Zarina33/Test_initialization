import json

def update_paths_in_json(input_json, output_json):
    """
    Заменяет пути в JSON-файле внутри списка "errors".
    
    Пример исходной строки:
    "Skipped empty JSON file: D:\\UlutSoft\\ready(last)\\Алгебра 8-класс\\Кыргызча версия\\W-8-032\\W-8-032-T-kg.json"
    
    Преобразуется в:
    "Skipped empty JSON file: /mnt/ks/Works/3nd_tests/ready(last)/Алгебра 8-класс/Кыргызча версия/W-8-032/W-8-032-T-kg.json"
    
    Args:
        input_json (str): Путь к входному JSON-файлу.
        output_json (str): Путь для сохранения обновлённого JSON-файла.
    """
    # Задаём старый базовый путь и новый базовый путь
    old_base = "D:\\UlutSoft\\ready(last)\\"
    new_base = "/mnt/ks/Works/3nd_tests/ready(last)/"

    try:
        # Читаем исходный JSON-файл
        with open(input_json, 'r', encoding='utf-8') as infile:
            data = json.load(infile)
        
        # Если в JSON есть ключ "errors" и он представляет список, обновляем каждую строку
        if "errors" in data and isinstance(data["errors"], list):
            updated_errors = []
            for error in data["errors"]:
                # Сначала заменяем старый базовый путь на новый
                updated_error = error.replace(old_base, new_base)
                # Затем меняем все обратные слэши на прямые
                updated_error = updated_error.replace("\\", "/")
                updated_errors.append(updated_error)
            data["errors"] = updated_errors
        
        # Записываем обновлённый JSON в новый файл
        with open(output_json, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile, ensure_ascii=False, indent=4)
        
        print(f"Обновлено и сохранено в {output_json}")
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    input_json = "/mnt/ks/Works/3nd_tests/errors2.json"
    output_json = "/mnt/ks/Works/3nd_tests/Errors_updated.json"
    update_paths_in_json(input_json, output_json)

