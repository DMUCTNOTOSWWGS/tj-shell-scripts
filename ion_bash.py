#!/usr/bin/env python3


# change these
USERNAME = '2017kgeng'
BLOCK_ID = 3162
ACTIVITY_ID = 814
TIMEOUT = 86.4


import email.mime.text
import getpass
import requests
import smtplib
import time


def send_email_to_self(subject, message):
    s = smtplib.SMTP_SSL('smtp.tjhsst.edu')
    s.login(USERNAME, PASSWORD)

    addr = USERNAME + '@tjhsst.edu'
    msg = email.mime.text.MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = addr
    msg['To'] = addr

    s.send_message(msg)
    s.quit()


def main():
    # get password
    global PASSWORD
    PASSWORD = getpass.getpass()

    # poll for signup
    while True:
        auth = (USERNAME, PASSWORD)
        data = {'block': BLOCK_ID, 'activity': ACTIVITY_ID}
        r = requests.post('https://ion.tjhsst.edu/api/signups/user',
                auth=auth, data=data)

        print("time: <{}>, status: <{}>, "
            .format(time.ctime(), r.status_code), end='')
        if r.status_code == 400:
            print("details: <{}>".format(r.json()['details']))
        else:
            break

        time.sleep(max(30, TIMEOUT))


    # send notification email
    if r.status_code == 201:
        print("quit due to success.")
        activity_name = r.json()['name']
        subject = "ion_bash.py: Signed up for {}!".format(activity_name)
        message = (
            "Successfully signed up for block {}, activity {}!\n"
            "Yay, much happy."
        ).format(BLOCK_ID, ACTIVITY_ID)
    else:
        print("quit due to unexpected response code.")
        subject = "ion_bash.py: Unexpected response code {}".format(r.status_code)
        message = (
            "Tried to sign up for block {}, activity {}, but something "
            "went wrong. Check console for details. Quitting."
        ).format(BLOCK_ID, ACTIVITY_ID)

    send_email_to_self(subject, message)
    print("Sent email successfully.")


if __name__ == '__main__':
    main()
