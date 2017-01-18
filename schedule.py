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
    progress = max(1, int(round(percent * 24)))
    status1 = '\x1b[36m{}>\x1b[0;2m{}'.format(
        '=' * (progress - 1), '-' * (24 - progress))
    status2 = '\x1b[36m{:02}:{:02}\x1b[0;2m / {:02}:{:02}\x1b[0m'.format(
        start_delta.seconds // 60, start_delta.seconds % 60,
        total_delta.seconds // 60, total_delta.seconds % 60)

    print('+' + '-' * 28 + '+')
    print('|\x1b[1m {} \x1b[0m|'.format(text))
    print('|\x1b[2m |{}| \x1b[0m|'.format(status1))
    print('|       {}        |'.format(status2))
    print('+' + '-' * 28 + '+')
    return 5  # lines_printed


def print_schedule(sched, sched_date, now):
    lines_printed = 0
    is_today = sched_date == now.date()

    # print date
    print(pad_width('{:%a, %b %d}'.format(sched_date)))
    lines_printed += 1

    # clean up day type
    day_type = sched['day_type']['name']
    day_type = re.sub(r'<.+?>', ' ', day_type)
    day_type = pad_width(' '.join(day_type.split()))

    # select day color
    if 'Blue' in day_type:
        day_color = '34'
    elif 'Red' in day_type:
        day_color = '31'
    elif 'Anchor' in day_type:
        day_color = '35'
    else:
        day_color = '37'

    print('\x1b[1;{}m{}\x1b[0m'.format(
        day_color, pad_width(day_type)))
    lines_printed += 1 + day_type.count('\n')

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
        # attempt to parse date
        try:
            req_date = parse_date(sys.argv[1])
        except ValueError:
            print('Please enter a valid date.', file=sys.stderr)
            return 1
        sched = get_schedule(req_date)
    else:
        sched = get_schedule()['results'][0]
        req_date = parse_date(sched['date'])


    if 'day_type' not in sched:
        print('No schedule available.')
        return 0

    while True:
        now = datetime.datetime.now()
        lines_printed, do_update = print_schedule(sched, req_date, now)
        if not do_update:
            break

        now = datetime.datetime.now()
        time.sleep(1 - now.microsecond / 1e6)
        clear_lines(lines_printed)

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        print('Goodbye!')
