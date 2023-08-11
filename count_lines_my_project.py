import os


def count_lines_in_file(file_path):
    with open(file_path, 'r', encoding='cp1251', errors='ignore') as file:
        return len(file.readlines())


def count_lines_in_project(current_directory):
    total_lines = 0
    for file_name in os.listdir(current_directory):
        if file_name.endswith(".py"):
            file_path = os.path.join(current_directory, file_name)
            total_lines += count_lines_in_file(file_path)
    return total_lines


current_directory = os.getcwd()
print("Текущая рабочая директория:", current_directory)
total_lines = count_lines_in_project(current_directory)
print("Общее количество строк в проекте:", total_lines)

if __name__ == "__main__":
    count_lines_in_project(current_directory)
