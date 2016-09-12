#!/usr/bin/env python3

import datetime
import re
import requests
import time

def get_schedule():
    r = requests.get('https://ion.tjhsst.edu/api/schedule')
    return r.json()

def parse_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

def parse_time(s):
    return datetime.datetime.strptime(s, '%H:%M').time()


def main():
    lines_printed = 0
    obj = get_schedule()

    sched = obj['results'][0]
    sched_date = parse_date(sched['date'])
    #now = datetime.datetime(2016, 9, 12, 9, 29, 50)
    now = datetime.datetime.now()
    is_today = sched_date == now.date()

    lines = [
        '{:%a, %b %d}'.format(sched_date),
        re.sub(r'<.+?>', '', sched['day_type']['name'])
    ]
    for line in lines:
        print('{:^26}'.format(line))
        lines_printed += 1

    current_block = None
    for block in sched['day_type']['blocks']:
        start = parse_time(block['start'])
        end = parse_time(block['end'])

        text = '{:>10}   {:>5} - {:>5}'.format(
                block['name'],
                '{:%H:%M}'.format(start),
                '{:%H:%M}'.format(end))
        if is_today and start <= now.time() <= end:
            print('\033[1;32m' + text + '\033[0m')
            current_block = dict(block, start_t=start, end_t=end)
        else:
            print(text)
        lines_printed += 1

    if current_block:
        print()
        lines_printed += 1
        block_end = datetime.datetime.combine(
                sched_date, current_block['end_t'])
        while True:
            delta = block_end - now
            if delta < datetime.timedelta(0):
                break
            print('\r\033[K{:02}:{:02} until next block'.format(
                    delta.seconds // 60, delta.seconds % 60), end='')
            time.sleep(0.5)
            now = datetime.datetime.now()
            #now += datetime.timedelta(milliseconds=500)
        print()
        lines_printed += 2

        print(''.join(['\033[A\r\033[K'] * (lines_printed - 1)), end='')
        return True

    return False

if __name__ == '__main__':
    try:
        while main():
            pass
    except KeyboardInterrupt:
        print()
        print('bye')



