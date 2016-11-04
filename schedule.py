#!/usr/bin/env python3

from __future__ import print_function, division

import codecs
import datetime
import json
import re
import sys
import time

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


def get_schedule(date=''):
    url = 'https://ion.tjhsst.edu/api/schedule/{}'.format(date)
    reader = codecs.getreader('utf-8')
    resp = reader(urlopen(url))
    return json.load(resp)


def parse_date(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()


def parse_time(s):
    return datetime.datetime.strptime(s, '%H:%M').time()


def pad_width(s):
    return '{:^30}'.format(s)


def print_progress(start_delta, total_delta, text):
    percent = start_delta.total_seconds() / total_delta.total_seconds()
    progress = max(1, round(percent * 24))
    status1 = '\x1b[36m' + '=' * (progress - 1) + '>\x1b[0;2m' + '-' * (24 - progress)
    status2 = '\x1b[36m{:02}:{:02}\x1b[0;2m / {:02}:{:02}\x1b[0m'.format(
    start_delta.seconds // 60, start_delta.seconds % 60,
    total_delta.seconds // 60, total_delta.seconds % 60)

    print('+' + '-' * 28 + '+')
    print('|\x1b[1m {} \x1b[0m|'.format(text))
    print('|\x1b[2m |{}| \x1b[0m|'.format(status1))
    print('|       {}        |'.format(status2))
    print('+' + '-' * 28 + '+')
    return 5  # lines_printed


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

    print('\x1b[1;{}m'.format(day_color) + day_type + '\x1b[0m')
    lines_printed += 1

    # print each block
    do_update = False
    last_end = None
    for block in sched['day_type']['blocks']:
        start = datetime.datetime.combine(
            sched_date, parse_time(block['start']))
        end = datetime.datetime.combine(
            sched_date, parse_time(block['end']))

        # progress during passing period
        if last_end and last_end <= now < start:
            text = 'Passing      {:>5} - {:>5}'.format(
                '{:%H:%M}'.format(last_end), '{:%H:%M}'.format(start))
            start_delta = now - last_end
            total_delta = start - last_end
            lines_printed += print_progress(start_delta, total_delta, text)
            do_update = True

        # progress during block
        text = '{:<10}   {:>5} - {:>5}'.format(block['name'],
            '{:%H:%M}'.format(start), '{:%H:%M}'.format(end))

        if start <= now < end:
            start_delta = now - start
            total_delta = end - start
            lines_printed += print_progress(start_delta, total_delta, text)
            do_update = True

        else:
            print('  {}  '.format(text))
            lines_printed += 1

        # update last_end
        last_end = end

    return lines_printed, do_update


def clear_lines(n):
    print(''.join(['\x1b[A\r'] * n), end='')


def main():
    if len(sys.argv) >= 2:
        sched = get_schedule(sys.argv[1])
    else:
        sched = get_schedule()['results'][0]

    while True:
        now = datetime.datetime.now()
        lines_printed, do_update = print_schedule(sched, now)
        if not do_update:
            break

        now = datetime.datetime.now()
        time.sleep(1 - now.microsecond / 1e6)
        clear_lines(lines_printed)


if __name__ == '__main__':
    try:
        while main():
            pass
    except KeyboardInterrupt:
        print()
        print('Goodbye!')
