import email
import imaplib
import board
import adafruit_ws2801
import time
from timeloop import Timeloop
import datetime
from datetime import timedelta

tl = Timeloop()
checkdate=(datetime.date.today()-datetime.timedelta(1)).strftime("%d-%b-%Y")

odata = board.MOSI
oclock = board.SCK
numleds = 50
bright = 1.0
leds = adafruit_ws2801.WS2801(oclock, odata, numleds, brightness=bright, auto_write=False)
leds.fill((0,0,255))
leds.show()
print(checkdate)

EMAIL = 'lighttest@rich-path.com'
PASSWORD = '***'
SERVER = 'mail.rich-path.com'

mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('inbox')

@tl.job(interval=timedelta(seconds=30))
def check_mail_every_60s():
    global checkdate
    status, data = mail.search(None, '(FROM "richpath2@gmail.com" SUBJECT "status" SINCE {0})'.format(checkdate))
    mail_ids = []
    for block in data:
        mail_ids += block.split()
    print(f'{mail_ids}')
    status, data = mail.fetch(mail_ids[-1], '(RFC822)')
    for response_part in data:
        if isinstance(response_part, tuple):
            message = email.message_from_bytes(response_part[1])
            mail_from = message['from']
            mail_subject = message['subject']
            mail_date = message['date']
            if message.is_multipart():
                mail_content = ''
                for part in message.get_payload():
                    if part.get_content_type() == 'text/plain':
                        mail_content += part.get_payload()
            else:
                mail_content = message.get_payload()

            print(f'From: {mail_from}')
            print(f'Subject: {mail_subject}')
            print(f'Date: {mail_date}')
            print(f'Content: {mail_content}')
            if "red" in mail_content:
                print(f'Red found!')
                leds.fill((255,0,0))
            elif "green" in mail_content:
                print(f'Green found!')
                leds.fill((0,255,0))
            elif "orange" in mail_content:
                print(f'Orange found!')
                leds.fill((255,50,0))
            elif "yellow" in mail_content:
                print(f'Yellow found!')
                leds.fill((255,255,0))
            date_comp = datetime.datetime.strptime(mail_date, '%a, %d %b %Y %H:%M:%S %z')
            date_string = date_comp.strftime("%d-%b-%Y")
            print(f'comp date string: {date_string}')
            if date_string > checkdate:
                checkdate=date_string
                print(f'New date: {checkdate}')
    leds.show()
tl.start()

while True:
  try:
    time.sleep(1)
  except KeyboardInterrupt:
    tl.stop()
    break
