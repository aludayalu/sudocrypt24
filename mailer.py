from secrets_parser import parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

password=parse("variables.txt")["password"]

def mail(to, subject, content):
    sender_email = "Exun Clan <exun@dpsrkp.net>"
    sender_password = password
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("exun@dpsrkp.net", sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()