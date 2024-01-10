from datetime import datetime
import pytz  # pip install pytz


def online_date_time():
    moscow_time = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%Y-%m-%d %H:%M:%S")
    return moscow_time
