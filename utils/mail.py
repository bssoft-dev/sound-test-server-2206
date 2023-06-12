import smtplib
from email.mime.text import MIMEText
from environment import mail_id, mail_passwd

def send_mail(to, subject, text, mail_from = mail_id):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    if mail_from == mail_id:
        s.login(mail_from, mail_passwd)
    else:
        print('invalid "mail_from" value')
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = to
    try:
        s.sendmail(mail_from, to, msg.as_string())
    except Exception as e:
        print('Error: unable to send email')
        print(e)
    s.quit()