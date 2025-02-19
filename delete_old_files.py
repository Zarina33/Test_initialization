import os
import json
import logging
from datetime import datetime

# Set up logging
log_filename = f'json_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_json_file(file_path):
    """Анализирует отдельный JSON файл"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            file_size = len(content)  # размер в байтах
            data = json.loads(content)
            
            # Анализ структуры
            num_questions = len(data.get('questions', []))
            
            # Проверка пустых полей
            empty_fields = []
            if not data.get('title'):
                empty_fields.append('title')
            
            empty_questions = []
            for i, q in enumerate(data.get('questions', []), 1):
                if not q.get('question'):
                    empty_questions.append(f'question_{i}')
                if not q.get('options'):
                    empty_questions.append(f'options_{i}')
                if not q.get('answer'):
                    empty_questions.append(f'answer_{i}')
            
            return {
                'file_name': os.path.basename(file_path),
                'file_size': file_size,
                'num_questions': num_questions,
                'empty_fields': empty_fields,
                'empty_questions': empty_questions,
                'has_title': bool(data.get('title')),
                'structure_valid': True
            }
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'error': f"Invalid JSON: {str(e)}",
            'structure_valid': False
        }
    except Exception as e:
        logger.error(f"Error analyzing {file_path}: {e}")
        return {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'error': f"Error: {str(e)}",
            'structure_valid': False
        }

def analyze_json_directory(directory):
    """Анализирует все JSON файлы в директории и поддиректориях"""
    results = []
    problems = []
    total_files = 0
    empty_files = 0
    invalid_files = 0
    
    logger.info(f"Starting analysis of directory: {directory}")
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                total_files += 1
                file_path = os.path.join(root, file)
                
                # Анализируем файл
                analysis = analyze_json_file(file_path)
                results.append(analysis)
                
                # Проверяем проблемы
                if not analysis['structure_valid']:
                    invalid_files += 1
                    problems.append(f"Invalid JSON in {file}: {analysis.get('error', 'Unknown error')}")
                elif analysis.get('num_questions', 0) == 0:
                    empty_files += 1
                    problems.append(f"Empty questions in {file}")
                elif analysis.get('empty_fields') or analysis.get('empty_questions'):
                    problems.append(f"Empty fields in {file}: " + 
                                 f"fields={analysis.get('empty_fields', [])} " +
                                 f"questions={analysis.get('empty_questions', [])}")
    
    # Сортируем результаты по размеру файла
    results.sort(key=lambda x: x['file_size'], reverse=True)
    
    # Выводим общую статистику
    print("\nJSON Analysis Results")
    print("="*50)
    print(f"Total JSON files: {total_files}")
    print(f"Invalid JSON files: {invalid_files}")
    print(f"Files with empty questions: {empty_files}")
    print(f"Files with problems: {len(problems)}")
    print("\nTop 10 largest files:")
    for r in results[:10]:
        print(f"{r['file_name']}: {r['file_size']/1024:.2f} KB, Questions: {r.get('num_questions', 'N/A')}")
    
    print("\nProblems found:")
    for p in problems:
        print(f"- {p}")
    
    # Записываем детальный отчет в файл
    report_file = f'json_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("JSON Analysis Detailed Report\n")
        f.write("="*50 + "\n\n")
        
        f.write("General Statistics:\n")
        f.write(f"Total JSON files: {total_files}\n")
        f.write(f"Invalid JSON files: {invalid_files}\n")
        f.write(f"Files with empty questions: {empty_files}\n")
        f.write(f"Files with problems: {len(problems)}\n\n")
        
        f.write("Detailed File Analysis:\n")
        for r in results:
            f.write("-"*50 + "\n")
            f.write(f"File: {r['file_name']}\n")
            f.write(f"Size: {r['file_size']/1024:.2f} KB\n")
            if r['structure_valid']:
                f.write(f"Questions: {r.get('num_questions', 'N/A')}\n")
                f.write(f"Has title: {r.get('has_title', False)}\n")
                if r.get('empty_fields'):
                    f.write(f"Empty fields: {r['empty_fields']}\n")
                if r.get('empty_questions'):
                    f.write(f"Empty questions: {r['empty_questions']}\n")
            else:
                f.write(f"Error: {r.get('error', 'Unknown error')}\n")
            f.write("\n")
        
        f.write("\nProblems Found:\n")
        for p in problems:
            f.write(f"- {p}\n")
    
    logger.info(f"Analysis complete. Detailed report saved to {report_file}")
    return results, problems

if __name__ == "__main__":
    directory = "/mnt/ks/Works/3nd_tests/json_output"
    analyze_json_directory(directory)
