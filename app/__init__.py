from datetime import datetime


def log(message):
    ts = datetime.now().strftime('%H:%M:%S')
    print('[LifeOS {}] {}'.format(ts, message))
