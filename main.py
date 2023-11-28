import logging
from datetime import datetime, timedelta


logging.basicConfig(level=logging.INFO)

START_TIME = '09:00'
END_TIME = '21:00'

BUSY = [
    {'start': '10:30', 'stop': '10:50'},
    {'start': '18:40', 'stop': '18:50'},
    {'start': '14:40', 'stop': '15:50'},
    {'start': '16:40', 'stop': '17:20'},
    {'start': '20:05', 'stop': '20:20'}
]


def convert_to_datetime_format(time_str: str) -> datetime:
    """
    Преобразует строку времени в формат datetime.

    Parameters:
        time_str (str): Строка времени в формате HH:MM.

    Returns:
        datetime: Время в формате datetime.

    Raises:
        ValueError: Если переданная строка не соответствует формату HH:MM.
    """
    try:
        return datetime.strptime(time_str, '%H:%M')
    except ValueError:
        raise ValueError(f"Некорректный формат времени: {time_str}. Ожидается формат HH:MM.")


def generate_busy_intervals(busy_intervals: list) -> list:
    """
    Сортирует и форматирует список занятых интервалов.

    Parameters:
        busy_intervals (list): Список словарей, представляющих занятые интервалы в рабочем дне.

    Returns:
        list: Отсортированный список кортежей (datetime, datetime),
              представляющих временные интервалы занятости.

    Raises:
        ValueError: Отсутствует обязательное поле.
    """
    try:
        busy_intervals_format = sorted(
            [
                (convert_to_datetime_format(interval['start']),
                 convert_to_datetime_format(interval['stop'])) for interval in busy_intervals
            ],
            key=lambda x: x[0]
        )
        return busy_intervals_format
    except KeyError as e:
        raise ValueError(f"Отсутствует обязательное поле {e} в одном из интервалов.")


def generate_free_windows(start_time: str, end_time: str, busy_intervals: list) -> list:
    """
    Генерирует список свободных окон в рабочем дне.

    Parameters:
        start_time (str): Время начала рабочего дня в формате HH:MM.
        end_time (str): Время окончания рабочего дня в формате HH:MM.
        busy_intervals (list): Список словарей, представляющих занятые интервалы в рабочем дне.
                              Каждый словарь содержит 'start' и 'stop',
                              представляющие время начала и окончания интервала.

    Returns:
        list: Список словарей, представляющих свободные окна и занятые интервалы в рабочем дне.
              Каждый словарь содержит 'start' и 'stop' для времени начала и окончания,
              а также 'type', указывающий тип интервала ('Свободное окно' или 'Перерыв').

    Важные примечания:
        Для удобства чтения вывод представляет собой один вариант свободных окон
        без возможных вариаций сдвигов на 5 или более минут.

        Для более точного определения количества интервалов для записи в «окнах» нужно понимать минимальный шаг записи.
        В программе айдент (IDENT), например, установлен минимальный шаг 15 мин. То есть (для примера) программа
        не подразумевает возможности записи на 8:05, 8:10, 8:20 - только 8:00/8:15/8:30

    Raises:
        ValueError: Если входные данные некорректны.
    """
    try:
        start_time_format = convert_to_datetime_format(start_time)
        end_time_format = convert_to_datetime_format(end_time)

        busy_intervals_format = generate_busy_intervals(busy_intervals)

        busy_intervals_format.insert(0, (start_time_format, start_time_format))
        busy_intervals_format.append((end_time_format, end_time_format))

        free_windows = []

        logging.debug("Начало генерации свободных окон.")

        current_start = busy_intervals_format[0][1]

        for busy_start, busy_stop in busy_intervals_format[1:]:
            time_difference = busy_start - current_start

            if time_difference >= timedelta(minutes=30):
                max_windows = (time_difference.total_seconds() // (30 * 60))
                free_windows.extend(
                    {'start': current_start + timedelta(minutes=30 * j),
                     'stop': current_start + timedelta(minutes=30 * (j + 1)),
                     'type': 'Свободное окно'} for j in range(int(max_windows))
                )

            current_start = max(current_start, busy_stop)

        logging.debug("Генерация свободных окон завершена.")

        return free_windows
    except ValueError as e:
        raise ValueError(f"Ошибка во входных данных: {e}")


def print_intervals(intervals: list) -> None:
    """
    Выводит список свободных окон и перерывов между ними.

    Parameters:
        intervals (list): Список словарей, представляющих свободные окна и занятые интервалы в рабочем дне.
    Returns:
        None
    """
    logging.debug(f"Начало рабочего дня: {START_TIME}")
    for interval in intervals:
        start_str = interval['start'].strftime('%H:%M')
        stop_str = interval['stop'].strftime('%H:%M')
        interval_type = interval.get('type', 'Свободное окно')
        print(f"{interval_type.capitalize()}: {start_str} - {stop_str}")
    logging.debug(f"Конец рабочего дня: {END_TIME}.")


def main() -> None:
    """
    Генерирует свободные окна в рабочем дне и выводит результат в консоль.

    Returns:
        None
    """
    try:
        free_windows = generate_free_windows(START_TIME, END_TIME, BUSY)
        print_intervals(free_windows)
        logging.debug("Программа успешно завершена.")
    except ValueError as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()
