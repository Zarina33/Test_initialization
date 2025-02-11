from docx import Document

def extract_and_format_answers(docx_path):
    # Открываем документ
    doc = Document(docx_path)
    
    # Получаем все таблицы из документа
    for table in doc.tables:
        variants = {}
        
        # Проходим по строкам таблицы
        for row in table.rows:
            # Получаем все ячейки в строке
            cells = [cell.text.strip().lower() for cell in row.cells]
            
            # Пропускаем пустые строки
            if not cells or not any(cells):
                continue
                
            # Извлекаем номер варианта и ответы
            variant = cells[0].replace('вар.', '').strip()
            # Убираем первую ячейку (номер варианта) и собираем ответы
            answers = cells[1:]
            
            if variant and answers:
                variants[variant] = answers
        
        # Форматируем и выводим результат для каждого варианта
        for var_num, answers in sorted(variants.items()):
            print(f"{var_num}-вар.")
            formatted_answers = [f"{i+1}){ans};" for i, ans in enumerate(answers) if ans]
            print(" ".join(formatted_answers))
            print()  # Пустая строка между вариантами

# Использование:
if __name__ == "__main__":
    # Замените на путь к вашему файлу
    docx_file = "path_to_your_file.docx"
    extract_and_format_answers(docx_file)

    