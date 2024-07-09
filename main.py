import csv
import re


def read_csv(file_path: str) -> list[list[str]]:
    """
    Чтение CSV-файла.

    :param file_path: Путь к CSV-файлу
    :return: Список с данными из CSV-файла
    """
    with open(file_path, encoding="utf-8") as f:
        rows = csv.reader(f, delimiter=",")
        contacts_list = list(rows)
    return contacts_list


def write_csv(contacts_list: list[list[str]], file_name: str) -> None:
    """
    Запись CSV-файла.

    :param contacts_list: Список с данными для записи
    :param file_name: Имя записываемого CSV-файла
    """
    with open(file_name, "w", encoding="utf-8", newline="") as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(contacts_list)


def format_name(old_full_name: list[str]) -> list[str]:
    """
    Форматирование ФИО по входящим данным.

    :param old_full_name: Список со столбцами ФИО
    :return:
        Список с ФИО. Формат: ['Фамилия', 'Имя', 'Отчество'].
        Если отсутствуют данные, то вместо него будет пустая строка.
    """
    full_name = " ".join(old_full_name).split()
    new_full_name = []
    for i in range(3):
        try:
            new_full_name.append(full_name[i])
        except IndexError:
            new_full_name.append("")
    return new_full_name


def format_phone(phone: str) -> str:
    """
    Форматирование номера телефона по различным входящим значениям.

    :param phone: Строка с номером телефона
    :return: Форматированный номер телефона в формате: +7(XXX)XXX-XX-XX доб.XXXX
    """
    pattern_compiled = re.compile(
        r"(\+7|8)?[\s-]*[( ]?(\d{3})[ -)]?[\s-]*(\d{3})[\s-]*(\d{2})[\s-]*(\d{2})(\s*\(?(доб.)\s*(\d{4})\)?)?"
    )
    new_pattern = r"+7(\2)\3-\4-\5 \7\8"  # +7(XXX)XXX-XX-XX доб.XXXX
    return pattern_compiled.sub(new_pattern, phone)


def format_contact_list(contacts_list: list[list[str]]) -> list[list[str]]:
    """
    Форматирование в списке контактов ФИО и номера телефонов.

    :param contacts_list: Список контактов
    :return: Форматированный список контактов
    """
    for contact in contacts_list:
        contact[0], contact[1], contact[2] = format_name(contact[0:3])
        contact[5] = format_phone(contact[5])
    return contacts_list


def check_and_update_duplicate(contacts_list: list[list[str]]) -> list[list[str]]:
    """
    Проверка и обновление дубликатов в списке контактов.

    :param contacts_list: Список контактов
    :return: Форматированный список контактов
    """
    indexes_to_delete = []  # Список индексов строк дубликатов
    for i in range(len(contacts_list)):
        for j in range(i + 1, len(contacts_list)):
            # Проверка дубликатов по ФИО или ФИ и отчество пустое
            if (contacts_list[i][0] == contacts_list[j][0]) and (
                    contacts_list[i][1] == contacts_list[j][1]) and (
                    contacts_list[i][2] == contacts_list[j][2] or (
                    contacts_list[i][2] == '' or contacts_list[j][2] == '')):
                # Можно начать объединять со столбца с отчеством,
                # т.к. в оригинальной строке может не быть отчества
                # после форматирования ФИО
                merging_contact_lines(contacts_list=contacts_list,
                                      row_origin=i,
                                      row_duplicate=j,
                                      start_column=2)
                indexes_to_delete.append(j)
    removing_duplicates(contacts_list=contacts_list,
                        indexes_to_delete=indexes_to_delete)
    return contacts_list


def merging_contact_lines(contacts_list: list[list[str]],
                          row_origin: int,
                          row_duplicate: int,
                          start_column: int | None = None,
                          end_column: int | None = None) -> None:
    """
    Запись данных из двух строк в одну в списке контактов.
    Если есть данные в колонке из row_duplicate,
    то они перезаписываются в колонку из row_origin,
    даже если в row_origin присутствуют данные.

    :param contacts_list: Список контактов
    :param row_origin: Индекс ряда оригинальной строки
    :param row_duplicate: Индекс ряда дубликатной строки
    :param start_column:
        Столбец начала объединения (индексация с нулевого).
        Если None, то объединение начинается с 0 столбца.
    :param end_column:
        Столбец окончания объединение (не включительно)
        Если None, то объединение до индекса последнего столбца включительно.
    """
    if start_column is None or start_column < 0:
        start_column = 0
    if end_column is None or end_column > len(contacts_list[row_origin]):
        end_column = len(contacts_list[row_origin])
    if start_column > end_column:
        raise IndexError("start_column must be less than end_column")
    for column in range(start_column, end_column):
        if contacts_list[row_duplicate][column]:
            contacts_list[row_origin][column] = (
                contacts_list[row_duplicate][column])


def removing_duplicates(contacts_list: list[list[str]],
                        indexes_to_delete: list[int]) -> None:
    """
    Удаление дубликатов в списке контактов.

    :param contacts_list: Список контактов
    :param indexes_to_delete: Список индексов строк для удаления
    """
    # Индексы строк для удаления сортируются в обратном порядке,
    # чтобы избежать возможных ошибок при удалении
    for index in sorted(indexes_to_delete, reverse=True):
        del contacts_list[index]


def main():
    file_path = "phonebook_raw.csv"
    contacts_list = read_csv(file_path)
    print(f"Файл {file_path} прочитан.")
    contacts_list = format_contact_list(contacts_list)
    print("ФИО и номера телефонов отформатированы.")
    check_and_update_duplicate(contacts_list)
    print("Дубликаты найдены и обработаны.")
    new_file_name = "phonebook.csv"
    write_csv(contacts_list, new_file_name)
    print(f"Обновленный файл {new_file_name} записан.")


if __name__ == '__main__':
    main()
