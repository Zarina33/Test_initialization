import os
import shutil

def find_and_delete_old_files(root_dir):
    print(f"Поиск файлов с суффиксом (Old) в директории: {root_dir}")
    files_to_delete = []
    
    # Находим все файлы с суффиксом (Old)
    for current_dir, dirs, files in os.walk(root_dir):
        for file_name in files:
            if file_name.endswith(' (Old).docx'):
                file_path = os.path.join(current_dir, file_name)
                files_to_delete.append(file_path)
    
    if not files_to_delete:
        print("Файлы с суффиксом (Old) не найдены.")
        return
    
    # Показываем список файлов для удаления
    print("\nНайдены следующие файлы:")
    for file_path in files_to_delete:
        print(f"- {file_path}")
    
    # Запрашиваем подтверждение
    confirmation = input("\nВы уверены, что хотите удалить эти файлы? (y/n): ").strip().lower()
    
    if confirmation == 'y':
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Удален файл: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"Ошибка при удалении {file_path}: {str(e)}")
        
        print(f"\nУспешно удалено файлов: {deleted_count}")
    else:
        print("Операция отменена.")

if __name__ == "__main__":
    folder_path = "/mnt/ks/Works/3nd_tests/tables/Алгебра 11 класс/Кыргызча версия"
    
    if not folder_path:
        folder_path = os.getcwd()
        print(f"Используем текущую папку: {folder_path}")
    
    if os.path.exists(folder_path):
        find_and_delete_old_files(folder_path)
    else:
        print(f"Указанная папка не существует: {folder_path}")