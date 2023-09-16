"""email_example.py
----------------
This module sends an email with the contents of a specified text file as the 
body. The "smtplib" and "email.message" modules are used to construct and send 
the email.
"""

import smtplib

from email.message import EmailMessage

textfile = "textfile"
with open(textfile) as fp:
    msg = EmailMessage()
    msg.set_content(fp.read())

msg["Subject"] = f"The contents of {textfile}"
msg["From"] = "roland"
msg["To"] = "roland"

s = smtplib.SMTP("localhost")
s.send_message(msg)
s.quit()
