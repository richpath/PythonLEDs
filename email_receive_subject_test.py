import email
import imaplib
#the board library is part of the Adafruit Blinka library from this package - https://github.com/adafruit/Adafruit_Blinka
import board
#ws2801 library from Adafruit - https://github.com/adafruit/Adafruit_CircuitPython_WS2801
import adafruit_ws2801
import time
#timeloop library is used to continually run a function at a regular interval - https://github.com/sankalpjonn/timeloop
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

#the email code is based on example codes provided at the following sites: https://www.devdungeon.com/content/read-and-send-email-python; https://humberto.io/blog/sending-and-receiving-emails-with-python/

EMAIL = 'lightbox@rich-path.com'
#password string will be replaced with an encrypted version instead of passed as plain text
PASSWORD = '*****'
SERVER = 'mail.rich-path.com'

mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
mail.select('inbox')

@tl.job(interval=timedelta(seconds=60))
def check_mail_every_60s():
    global checkdate
    #email is filtered to include only messages sent from my personal gmail account with the phrase "Capacity Level" in the subject and since the date set in the checkdate variable
    status, data = mail.search(None, '(FROM "richpath2@gmail.com" SUBJECT "Capacity Level" SINCE {0})'.format(checkdate))
    mail_ids = []
    for block in data:
        mail_ids += block.split()
    if len(mail_ids) > 0:
        print(f'{mail_ids}')
        #look at only the last email in the collection that is fetched
        status, data = mail.fetch(mail_ids[-1], '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']
                mail_date = message['date']

                print(f'From: {mail_from}')
                print(f'Subject: {mail_subject}')
                print(f'Date: {mail_date}')
                if "Red" in mail_subject:
                    print(f'Red found!')
                    leds.fill((255,0,0))
                elif "Green" in mail_subject:
                    print(f'Green found!')
                    leds.fill((0,255,0))
                elif "Orange" in mail_subject:
                    print(f'Orange found!')
                    leds.fill((255,50,0))
                elif "Yellow" in mail_subject:
                    print(f'Yellow found!')
                    leds.fill((255,255,0))
                date_comp = datetime.datetime.strptime(mail_date, '%a, %d %b %Y %H:%M:%S %z')
                date_string = date_comp.strftime("%d-%b-%Y")
                print(f'comp date string: {date_string}')
                #set the checkdate variable to the date of the last email used, so that only emails after that new date are returned in filtered results
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
