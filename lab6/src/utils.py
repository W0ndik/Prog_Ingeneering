def print_table(table_list, columns_list):
    """
    :param table_list: - массив с данными таблицы
    :param columns_list:  - массив в котором лежат значения столбцов в нужном порядке
    :return: None
    """
    # Проверка на соответствие количества столбцов
    assert len(table_list[0]) == len(columns_list)

    table_list = list(map(list, table_list))
    raw_limit = 50
    # Расчёт длинн столбцов
    len_list = []
    for column in range(len(table_list[0])):
        max = 0
        for raw in range(len(table_list)):
            if len(str(table_list[raw][column])) > max:
                max = len(str(table_list[raw][column]))
                if max > raw_limit:
                    max = raw_limit
                    table_list[raw][column] = (
                        str(table_list[raw][column])[: raw_limit - 3].replace("\n", " ")
                        + "..."
                    )
        if max < len(str(columns_list[column])):
            max = len(str(columns_list[column]))

        len_list.append(max)

    # Расчёт полной длинный таблицы
    finally_len = 0
    for i in len_list:
        finally_len += i

    # Вывод названий столбцов
    for column in range(len(columns_list)):
        print(
            str(" {:" + f"^{len_list[column]}" + "} |").format(columns_list[column]),
            end="",
        )
    print("\n" + "-" * (finally_len + len(columns_list) * 3))

    # Вывод данных таблицы
    for raw in range(len(table_list)):
        for column in range(len(table_list[0])):
            print(
                str(" {:" + f"^{len_list[column]}" + "} |").format(
                    str(table_list[raw][column])
                ),
                end="",
            )
        print("")
    return None


# Функция для обработки результатов доставки сообщения
def delivery_report(err, msg):
    if err is not None:
        print(f"User creation failed: {err}")
    else:
        print(f"User created {msg.topic()} [{msg.partition()}]")
