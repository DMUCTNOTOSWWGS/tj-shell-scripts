#!/usr/bin/env python

import datetime
import getpass
import os
import requests


USERNAME = os.getenv('USER')
PASSWORD = None


'''
def get_blocks(date):
    auth = (USERNAME, PASSWORD)
    r = requests.get('https://ion.tjhsst.edu/api/blocks', auth=auth)
    if r.status_code != 200:
        raise ValueError(r.text)
    return r.json()['results']


def get_block_activities(block_id):
    auth = (USERNAME, PASSWORD)
    r = requests.get('https://ion.tjhsst.edu/api/blocks/{}'.format(block_id), auth=auth)
    if r.status_code != 200:
        raise ValueError(r.text)
'''

def main():
    print('Username:', USERNAME)

    # get password
    global PASSWORD
    PASSWORD = getpass.getpass()

    today = datetime.datetime.now().date()
    print('Today is', today)

    auth = (USERNAME, PASSWORD)
    r = requests.get('https://ion.tjhsst.edu/eighth/profile/32080', auth=auth)
    print(r.text)

    #block_list = get_blocks()
    #for block in block_list:
    #    print(block['date'], block['block_letter'])


if __name__ == '__main__':
    main()

