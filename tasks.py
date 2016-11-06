#  import os
#  import sys
#  sys.path.insert(0, os.getcwd())
from manage import app as application
app_context = application.app_context()
app_context.push()

from app import db
from app import mail
from app.models import Task

import time
from datetime import datetime


from threading import Thread
from flask import current_app
from flask_mail import Message


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, **kw):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    stub = """
    <body>
    <h1>Question</h1>
    <div class="question">
    {question}
    </div>
    <h1>Answer</h1>
    <details class="question">
    {answer}
    </details>
    </body>
    """
    msg.body = stub.format(subject=subject, question=kw['question'],
                           answer=kw['answer']).encode('utf-8')
    msg.html = stub.format(subject=subject, question=kw['question'],
                           answer=kw['answer']).encode('utf-8')
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def get_tasks():
    return db.session.query(Task).filter(
        Task.start_timestamp < datetime.now()).all()


def main():
    while True:
        for task in get_tasks():
            to = task.post.author.email
            subject = task.post.question
            kw = dict(
                question=task.post.question_html,
                answer=task.post.answer_html
            )
            send_email(to, subject, **kw)
            db.session.delete(task)
            db.session.commit()
        time.sleep(60)


if __name__ == '__main__':
    main()
