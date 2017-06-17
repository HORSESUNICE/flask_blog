from flask_mail import Message
from threading import Thread
from flask import current_app
from flask import render_template

from . import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, template, *to, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[*to])
    msg.body = template
    # msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
    # send_async_email(app, msg)

def send_confirm_email(confirm_type, *to, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + confirm_type,
                  sender=app.config['MAIL_SENDER'], recipients=[*to])
    msg.body = render_template('auth/'+ confirm_type +'_confirm.txt', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr