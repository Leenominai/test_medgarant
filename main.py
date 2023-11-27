import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

start_time = '09:00'
end_time = '21:00'

busy = [
    {'start': '10:30', 'stop': '10:50'},
    {'start': '18:40', 'stop': '18:50'},
    {'start': '14:40', 'stop': '15:50'},
    {'start': '16:40', 'stop': '17:20'},
    {'start': '20:05', 'stop': '20:20'}
]


def generate_free_windows(start_time, end_time, busy_intervals):
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

    Примечания:
        Для удобства чтения вывод представляет собой один вариант свободных окон
        без возможных вариаций сдвигов на 5 или более минут.

        Для более точного определения количества интервалов для записи в «окнах» нужно понимать минимальный шаг записи.
        В программе айдент (IDENT), например, установлен минимальный шаг 15 мин. То есть (для примера) программа
        не подразумевает возможности записи на 8:05, 8:10, 8:20 - только 8:00/8:15/8:30

    """
    start_time_format = datetime.strptime(start_time, '%H:%M')
    end_time_format = datetime.strptime(end_time, '%H:%M')

    busy_intervals_format = sorted(
        [
            (datetime.strptime(interval['start'], '%H:%M'),
             datetime.strptime(interval['stop'], '%H:%M')) for interval in busy_intervals
        ],
        key=lambda x: x[0]
    )

    busy_intervals_format.insert(0, (start_time_format, start_time_format))
    busy_intervals_format.append((end_time_format, end_time_format))

    free_windows = []

    logging.info("Начало генерации свободных окон.")

    for i in range(len(busy_intervals_format) - 1):
        current_start = busy_intervals_format[i][1]
        next_stop = busy_intervals_format[i + 1][0]

        time_difference = next_stop - current_start

        if time_difference >= timedelta(minutes=30):
            max_windows = (time_difference.total_seconds() // (30 * 60))

            for j in range(int(max_windows)):
                window_start = current_start + timedelta(minutes=30 * j)
                window_stop = window_start + timedelta(minutes=30)
                free_windows.append({'start': window_start, 'stop': window_stop, 'type': 'Свободное окно'})

    for interval in busy_intervals_format[1:-1]:
        busy_interval_start = interval[0]
        busy_interval_stop = interval[1]
        busy_interval = {'start': busy_interval_start, 'stop': busy_interval_stop, 'type': 'Перерыв'}
        free_windows.append(busy_interval)

    free_windows = sorted(free_windows, key=lambda x: x['start'])

    logging.info("Генерация свободных окон завершена.")

    return free_windows


def print_intervals(intervals):
    """
    Выводит интервалы в консоль.

    Parameters:
        intervals (list): Список словарей, представляющих свободные окна и занятые интервалы в рабочем дне.

    Returns:
        None
    """
    print(f"Начало рабочего дня: {start_time}")
    for interval in intervals:
        start_str = interval['start'].strftime('%H:%M')
        stop_str = interval['stop'].strftime('%H:%M')
        interval_type = interval.get('type', 'Свободное окно')
        print(f"{interval_type.capitalize()}: {start_str} - {stop_str}")
    print(f"Конец рабочего дня: {end_time}.")


free_windows = generate_free_windows(start_time, end_time, busy)
print_intervals(free_windows)
