import os
import json
from pathlib import Path

class FileAnalyzer:
    def __init__(self, base_dir, output_dir):
        self.base_dir = Path(base_dir)
        self.output_dir = Path(output_dir)
        # Создаем output_dir, если она не существует
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_extracted_dir(self, json_file):
        """Находит директорию extracted_files для конкретного JSON файла"""
        # Получаем базовое имя JSON файла без расширения
        base_name = json_file.stem  # например 'W-9-001-T-kg'
        
        # Ищем папку extracted_files с соответствующим суффиксом
        expected_dir_name = f"extracted_files_{base_name}"
        extracted_dir = json_file.parent / expected_dir_name
        
        if extracted_dir.exists() and extracted_dir.is_dir():
            return {
                'extracted_dir': extracted_dir,
                'math_files_dir': extracted_dir / "math_files",
                'images_dir': extracted_dir / "images"
            }
        return None

    def check_has_related_files(self, json_file):
        """Проверяет наличие связанных файлов формул и изображений"""
        dirs = self._find_extracted_dir(json_file)
        if not dirs:
            return False
            
        has_related_files = False
        base_name = json_file.stem
        
        # Проверяем наличие файлов в папке math_files
        math_files_dir = dirs['math_files_dir']
        if math_files_dir.exists():
            formula_files = list(math_files_dir.glob(f"{base_name}*"))
            if formula_files:
                has_related_files = True
                print(f"Найдены файлы формул для {json_file.name}")
        
        # Проверяем наличие файлов в папке images
        images_dir = dirs['images_dir']
        if images_dir.exists():
            image_files = list(images_dir.glob(f"{base_name}*"))
            if image_files:
                has_related_files = True
                print(f"Найдены файлы изображений для {json_file.name}")
        
        return has_related_files

    def find_files_with_images_and_formulas(self):
        """Находит все JSON файлы с изображениями или формулами"""
        files_with_related = []
        remaining_files = []
        
        json_files = list(self.base_dir.rglob("*.json"))
        print(f"\nНайдено JSON файлов: {len(json_files)}")
        
        for json_file in json_files:
            print(f"\nПроверка файла: {json_file.name}")
            if self.check_has_related_files(json_file):
                files_with_related.append(str(json_file.absolute()))
                print(f"- Файл {json_file.name} имеет связанные файлы")
            else:
                remaining_files.append(json_file)
                print(f"- Файл {json_file.name} не имеет связанных файлов")
                
        # Сохраняем файлы с изображениями и формулами
        images_file = self.output_dir / "images.txt"
        with open(images_file, 'w', encoding='utf-8') as f:
            for file_path in files_with_related:
                f.write(f"{file_path}\n")
                
        return remaining_files

    def check_json_correctness(self, json_file):
        """Проверяет корректность JSON файла"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if not isinstance(data, dict):
                    return False, "Неверная структура документа"
                    
                if "questions" not in data:
                    return False, "Отсутствует секция questions"
                
                for idx, question in enumerate(data["questions"], 1):
                    if "answer" not in question or not question["answer"].strip():
                        return False, f"Вопрос {idx}: пустой ответ"
                
                return True, None
                    
        except json.JSONDecodeError as e:
            return False, f"Невалидный JSON файл: {str(e)}"
        except Exception as e:
            return False, f"Ошибка при обработке: {str(e)}"
                
    def analyze_remaining_files(self, remaining_files):
        """Анализирует оставшиеся файлы на корректность"""
        results = {
            "correctly_parsed": [],
            "incorrectly_parsed": []
        }
        
        print("\nПроверка оставшихся файлов на корректность:")
        for json_file in remaining_files:
            print(f"\nПроверка файла: {json_file.name}")
            is_correct, error = self.check_json_correctness(json_file)
            if is_correct:
                results["correctly_parsed"].append(str(json_file.absolute()))
                print("- Файл корректен")
            else:
                results["incorrectly_parsed"].append(str(json_file.absolute()))
                print(f"- Ошибка: {error}")
                
        return results
    
    def save_results_to_txt(self, results, total_files, files_with_related):
        """Сохраняет результаты в txt файлы"""
        # Сохраняем корректные файлы
        correct_file = self.output_dir / "correct_files.txt"
        with open(correct_file, 'w', encoding='utf-8') as f:
            for file_path in results['correctly_parsed']:
                f.write(f"{file_path}\n")
                
        # Сохраняем некорректные файлы
        incorrect_file = self.output_dir / "incorrect_files.txt"
        with open(incorrect_file, 'w', encoding='utf-8') as f:
            for file_path in results['incorrectly_parsed']:
                f.write(f"{file_path}\n")
        
        # Сохраняем статистику
        stats_file = self.output_dir / "statistics.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("=== Отчет по анализу файлов ===\n")
            f.write(f"Всего JSON файлов: {total_files}\n")
            f.write(f"Файлов с изображениями/формулами: {files_with_related}\n")
            f.write(f"Корректно обработанных файлов: {len(results['correctly_parsed'])}\n")
            f.write(f"Некорректно обработанных файлов: {len(results['incorrectly_parsed'])}\n")
    
    def generate_report(self):
        """Генерирует отчет анализа"""
        print("\nПоиск файлов с изображениями и формулами...")
        remaining_files = self.find_files_with_images_and_formulas()
        
        print("\nАнализ оставшихся файлов...")
        results = self.analyze_remaining_files(remaining_files)
        
        # Подсчет статистики
        files_with_related = len(list(Path(self.output_dir / 'images.txt').read_text().splitlines()))
        total_files = len(remaining_files) + files_with_related
        
        print("\n=== Отчет по анализу файлов ===")
        print(f"Всего JSON файлов: {total_files}")
        print(f"Файлов с изображениями/формулами: {files_with_related}")
        print(f"Корректно обработанных файлов: {len(results['correctly_parsed'])}")
        print(f"Некорректно обработанных файлов: {len(results['incorrectly_parsed'])}")
        
        self.save_results_to_txt(results, total_files, files_with_related)
        
        print(f"\nРезультаты сохранены в директории: {self.output_dir}")

def main():
    base_dir = "/mnt/ks/Works/3nd_tests/ready(last)"
    output_dir = "/mnt/ks/Works/3nd_tests/results"
    
    analyzer = FileAnalyzer(base_dir, output_dir)
    analyzer.generate_report()

if __name__ == "__main__":
    main()
