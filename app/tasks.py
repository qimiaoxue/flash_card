import os
import sys
sys.path.insert(0, os.getcwd())
from app import db, mail
import Task
import time
from datetime import datetime
from threading import Thread
from flask import render_template
from flask_mail import Message

FLASKY_MAIL_SUBJECT_PREFIX = "[XueYan's Blog]"
FLASKY_MAIL_SENDER = "XueYan's Blog Admin <m13488699851@163.com>"


def send_email(to, subject, template, **kwargs):
    msg = Message(FLASKY_MAIL_SUBJECT_PREFIX + ' ' + subject,
                  sender=FLASKY_MAIL_SENDER, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[msg])
    thr.start()
    return thr


def send_async_email(msg):
    mail.send(msg)


def get_tasks():
    return db.session.query(Task).filter_by(
        Task.start_timestamp < datetime.now()).all()


def main():
    while True:
        for task in get_tasks():
            to = task.post.author.email
            subject = task.post.question
            template = 'mail/quesiton'
            kw = dict(
                question=task.post.question_html,
                answer=task.post.anwser_html
            )
            send_email(to, subject, template, **kw)
        time.sleep(60)


if __name__ == '__main__':
    main()
