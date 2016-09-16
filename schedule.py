#!/usr/bin/env python3

import datetime
import re
import requests
import sys
import time


def get_schedule(date=''):
    url = 'https://ion.tjhsst.edu/api/schedule/{}'.format(date)
    r = requests.get(url)
    return r.json()


def parse_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

def parse_time(s):
    return datetime.datetime.strptime(s, '%H:%M').time()

def pad_width(s):
    return '{:^30}'.format(s)


def print_schedule(sched, now):
    lines_printed = 0

    sched_date = parse_date(sched['date'])
    is_today = sched_date == now.date()

    # print date
    print(pad_width('{:%a, %b %d}'.format(sched_date)))
    lines_printed += 1

    # print day type with color
    day_type = pad_width(re.sub(r'<.+?>', '', sched['day_type']['name']))
    if 'Blue' in day_type:
        day_color = '34'
    elif 'Red' in day_type:
        day_color = '31'
    elif 'Anchor' in day_type:
        day_color = '35'
    else:
        day_color = '37'
    print('\033[1;{}m'.format(day_color) + day_type + '\033[0m')
    lines_printed += 1

    # print each block
    do_update = False
    for block in sched['day_type']['blocks']:
        start = parse_time(block['start'])
        end = parse_time(block['end'])

        text = '{:<10}   {:>5} - {:>5}'.format(block['name'],
            '{:%H:%M}'.format(start), '{:%H:%M}'.format(end))

        if is_today and start <= now.time() <= end:
            start_date = datetime.datetime.combine(sched_date, start)
            start_delta = now - start_date

            end_date = datetime.datetime.combine(sched_date, end)
            end_delta = end_date - now

            print('\033[1m  ' + text + '  \033[0m')
            print('\033[2m    {:02}:{:02} ~~ {:02}:{:02} \033[0m'.format(
                start_delta.seconds // 60, start_delta.seconds % 60,
                end_delta.seconds // 60, end_delta.seconds % 60))
            lines_printed += 2
            do_update = True

        else:
            print('  ' + text + '  ')
            lines_printed += 1

    return lines_printed, do_update


def clear_lines(n):
    print(''.join(['\033[A\r'] * n), end='')


def main():
    now = datetime.datetime.now()
    if len(sys.argv) >= 2:
        sched = get_schedule(sys.argv[1])
    else:
        sched = get_schedule()['results'][0]

    while True:
        lines_printed, do_update = print_schedule(sched, now)
        if not do_update:
            break

        time.sleep(0.5)
        now = datetime.datetime.now()

        clear_lines(lines_printed)


if __name__ == '__main__':
    try:
        while main():
            pass
    except KeyboardInterrupt:
        print()
        print('bye')



