import os
from openai import OpenAI
import json
import logging
from datetime import datetime
import re

# Set up logging
log_filename = f'conversion_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.DEBUG,
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

def fix_formula_paths(text):
    """Исправляет обрезанные пути к формулам"""
    try:
        pattern = r'\[Формула заменена: [^\]]*(?:\]|$)'
        paths = re.finditer(pattern, text)
        fixed_text = text
        
        for path in paths:
            if not path.group().endswith(']'):
                # Если путь обрезан, пытаемся его восстановить
                original_path = path.group()
                fixed_path = original_path + ']'
                fixed_text = fixed_text.replace(original_path, fixed_path)
        
        return fixed_text
    except Exception as e:
        logger.error(f"Error fixing formula paths: {e}")
        return text

def validate_json_response(text):
    """Проверяет и исправляет JSON-ответ"""
    try:
        # Проверяем, есть ли незакрытые строки с формулами
        if '[Формула заменена:' in text and not text.endswith('}'):
            text = fix_formula_paths(text)
        
        # Пытаемся загрузить JSON
        try:
            data = json.loads(text)
            return text
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            
            # Если это похоже на обрезанный JSON, попробуем его восстановить
            if text.count('{') > text.count('}'):
                text = text.rstrip() + '}'
            if '"questions": [' in text and not '"]}' in text:
                text = text.rstrip() + ']}}'
                
            return text
    except Exception as e:
        logger.error(f"Error validating JSON: {e}")
        return text

def read_text_from_file(file_path):
    try:
        logger.info(f"Attempting to read file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            logger.debug(f"File content:\n{content}")
            return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def send_to_gpt4_for_json(content, model="gpt-4o-mini-2024-07-18", max_tokens=4000):
    try:
        logger.info(f"Sending content to GPT-4")
        print("\nInput Text:")
        print("="*50)
        print(content)
        print("="*50)
        
        system_prompt = """Ты конвертер тестов в JSON формат. ОЧЕНЬ ВАЖНО: всегда сохраняй полные пути к формулам целиком, никогда не обрезай их."""

        user_prompt = """Преобразуй тест в такую JSON структуру:
{
    "title": "Название предмета, класс и название урока",
    "questions": [
        {
            "number": число,
            "question": "полный текст вопроса",
            "options": [
                "полный вариант ответа",
                ...
            ],
            "answer": "буква ответа"
        }
    ]
}

ВАЖНО:
1. ВСЕГДА сохраняй полные пути к формулам, не обрезай их
2. Каждый путь к формуле должен заканчиваться закрывающей скобкой ]
3. Проверяй, что все JSON-строки правильно закрыты
4. В options включай полный текст вариантов с буквами и знаками препинания
5. В answer указывай только букву без точки и скобки

Теперь преобразуй следующий текст:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt + "\n\n" + content}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        logger.debug(f"Raw GPT response:\n{result}")
        
        # Проверяем и исправляем JSON
        fixed_result = validate_json_response(result)
        logger.debug(f"Fixed JSON response:\n{fixed_result}")
        
        print("\nGPT Response:")
        print("="*50)
        print(fixed_result)
        print("="*50)
        return fixed_result
    except Exception as e:
        logger.error(f"Error contacting GPT-4 API: {e}")
        return ""

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
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=4)
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
