#-*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import os

class emaillib:
    def sendMail(self, to_email, file_list, append_text):
        to_list = []

        msg = MIMEMultipart()
        message = ""
        for append_msg in append_text:
            if len(append_msg) > 0:
                if append_msg[-1] != '\n':
                    append_msg += '\n'
            else:
                append_msg = '\n'
            message += append_msg

        # setup the parameters of the message
        password = "qkrdbwls00"
        msg['From'] = "pyj0827@midasit.com"
        msg['To'] = to_email
        msg['Subject'] = "nGen Regression Testing Error !!!"
 
        # add in the message body
        msg.attach(MIMEText(message,_charset='UTF-8'))

        for f in file_list or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name = os.path.basename(f))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
            msg.attach(part)

        #create server
        server = smtplib.SMTP_SSL('smtp.mailplug.co.kr: 465')
 
        # Login Credentials for sending the mail
        server.login(msg['From'], password)
 
        # send the message via the server.
        server.sendmail(msg['From'], msg['To'], msg.as_string())
 
        server.quit()
 
        print("successfully sent email to %s:" % (msg['To']))