import os
from openai import OpenAI
import json
import logging
from datetime import datetime

# Set up logging
log_filename = f'conversion_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.DEBUG,  # Изменил уровень на DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key='')
logger.info("OpenAI client initialized")

def read_text_from_file(file_path):
    try:
        logger.info(f"Attempting to read file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.debug(f"File content:\n{content}")  # Добавил вывод содержимого
            return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def send_to_gpt4_for_json(content, model="gpt-4o-mini-2024-07-18", max_tokens=3000):
    try:
        logger.info(f"Sending content to GPT-4")
        print("\nInput Text:")
        print("="*50)
        print(content)
        print("="*50)
        
        prompt = """Преобразуй текст теста в JSON формат.

Пример входного текста:
```
АЛГЕБРА, 8-КЛАСС
9-сабак. Квадраттык тамыр түшүнүгү
Тест
1-суроо 
туюнтмасынын маанисин тапкыла
Жооптордун варианттары:
а) 5
б) 2
в) 3
г) 4
Туура жообу: а
```

Требуемый формат JSON:
```json
{
    "title": "АЛГЕБРА, 8-КЛАСС. 9-сабак. Квадраттык тамыр түшүнүгү",
    "questions": [
        {
            "number": 1,
            "question": "туюнтмасынын маанисин тапкыла",
            "options": [
                "а) 5",
                "б) 2",
                "в) 3",
                "г) 4"
            ],
            "answer": "а"
        }
    ]
}
```

Правила:
1. В title объедини название предмета, класс и тему
2. В number используй только число без дефиса и точки
3. В options включай буквы вариантов
4. В answer укажи букву или номер правильного ответа
5. Сохраняй все пути к формулам и изображениям без изменений

Теперь преобразуй следующий текст:"""

        messages = [
            {"role": "system", "content": "Ты помощник, который преобразует тексты тестов в JSON формат точно по заданному шаблону."},
            {"role": "user", "content": prompt + "\n\n" + content}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3  # Уменьшил temperature для более точных ответов
        )
        
        result = response.choices[0].message.content
        logger.debug(f"GPT response:\n{result}")
        print("\nGPT Response:")
        print("="*50)
        print(result)
        print("="*50)
        return result
    except Exception as e:
        logger.error(f"Error contacting GPT-4 API: {e}")
        return ""

def validate_and_fix_json(json_data):
    try:
        logger.debug(f"Validating JSON data:\n{json.dumps(json_data, ensure_ascii=False, indent=2)}")
        
        if not isinstance(json_data, dict):
            logger.error(f"Invalid JSON: not a dictionary but {type(json_data)}")
            raise ValueError("Invalid JSON structure")
            
        if "title" not in json_data or "questions" not in json_data:
            logger.error("Missing required fields 'title' or 'questions'")
            raise ValueError("Missing required fields")
        
        if not isinstance(json_data["questions"], list):
            logger.error("'questions' is not a list")
            json_data["questions"] = []
        
        for i, question in enumerate(json_data["questions"]):
            if not isinstance(question, dict):
                logger.error(f"Question {i+1} is not a dictionary")
                continue
                
            # Ensure required keys exist
            question.setdefault("number", i+1)
            question.setdefault("question", "")
            question.setdefault("options", [])
            question.setdefault("answer", "")
            
            logger.debug(f"Processed question {i+1}:\n{json.dumps(question, ensure_ascii=False, indent=2)}")
        
        return json_data
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return {
            "title": "",
            "questions": []
        }

def process_file(file_path, output_base_dir):
    try:
        logger.info(f"\n{'='*50}\nProcessing file: {file_path}")
        
        rel_path = os.path.relpath(file_path, "/mnt/ks/Works/3nd_tests/extracted_text")
        json_file_path = os.path.join(output_base_dir, rel_path.replace(".txt", ".json"))
        
        if os.path.exists(json_file_path):
            logger.info(f"JSON file already exists: {json_file_path}")
            return
            
        content = read_text_from_file(file_path)
        if not content:
            logger.error("No content read from file")
            return
        
        gpt_response = send_to_gpt4_for_json(content)
        if not gpt_response:
            logger.error("No response from GPT-4")
            return
        
        try:
            # Remove any markdown code block syntax
            stripped_response = gpt_response.strip()
            if stripped_response.startswith("```"):
                logger.debug("Removing code block markers")
                stripped_response = stripped_response.split("```json")[-1].split("```")[0].strip()
            
            logger.debug(f"Parsing JSON response:\n{stripped_response}")
            parsed_data = json.loads(stripped_response)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Failed JSON string: {stripped_response}")
            parsed_data = {"title": "", "questions": []}
        
        validated_data = validate_and_fix_json(parsed_data)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(validated_data, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved JSON to: {json_file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing file: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    try:
        logger.info("Starting conversion process")
        
        input_directory = "/mnt/ks/Works/3nd_tests/extracted_text"
        output_base_dir = "/mnt/ks/Works/3nd_tests/json_output"
        
        if not os.path.exists(input_directory):
            logger.error(f"Input directory not found: {input_directory}")
            exit(1)
            
        os.makedirs(output_base_dir, exist_ok=True)
        
        files_processed = 0
        files_skipped = 0
        files_failed = 0
        
        for root, _, files in os.walk(input_directory):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    logger.info(f"Found txt file: {file_path}")
                    
                    if process_file(file_path, output_base_dir):
                        files_processed += 1
                    else:
                        files_failed += 1
                else:
                    files_skipped += 1
        
        logger.info(f"\nProcessing complete:")
        logger.info(f"Processed: {files_processed}")
        logger.info(f"Failed: {files_failed}")
        logger.info(f"Skipped: {files_skipped}")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
