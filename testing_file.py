from email.message import EmailMessage
import smtplib 
import ssl

email_sender = "ScheduleOptimizerap@gmail.com"

email_recevier = "steveverney@hotmail.com"

email_password = "yyhz oouv wrlr hjlp"

subject = "Thanks for registering on Schedule Optimizer"

body = """

Hi thanks for your registration, enjoy your new journey into schedule optimization


"""

em = EmailMessage()

em["From"] = email_sender
em["To"] = email_recevier
em["subject"] = subject
em.set_content(body)

context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
    smtp.login(email_sender,email_password)
    smtp.sendmail(email_sender,email_recevier,em.as_string())
