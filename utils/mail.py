# _*_ coding:utf-8 _*_
# !/usr/bin/env python
# Date: 2016-10-13
# auth: nevermore


import smtplib
from email.mime.text import MIMEText
from django.conf import settings


class Mail:
    """
    邮件处理
    支持 HTML 标签处理
    使用： 需要发邮件的模块自定义并生成邮件内容
    """
    @classmethod
    def send(cls, to_list, subject, content):
        frm = 'Noreply' + '<' + settings.EMAIL_USER + '>'
        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = frm
        msg['To'] = ';'.join(to_list)
        try:
            client = smtplib.SMTP()
            client.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
            client.login(settings.EMAIL_USER, settings.EMAIL_PASS)
            client.sendmail(frm, to_list, msg.as_string())
            client.close()
            return True
        except Exception as e:
            print('error: %s' % str(e))
            return False
