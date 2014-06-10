import imaplib
import email
import datetime
import sys


def returnUsernamePassword(self):
    with open('../really_secret.txt', 'r') as f:
        lines = f.readlines()[0]
    return lines.split(',')

def process_mailbox(mail):
  rv, data = mail.search(None, "ALL")
  if rv != 'OK':
      print "No messages found!"
      return

  for num in data[0].split():
      rv, data = mail.fetch(num, '(RFC822)')
      if rv != 'OK':
          print "ERROR getting message", num
          return

      msg = email.message_from_string(data[0][1])
      print(msg)
      print 'Message %s: %s\n%s' % (num, msg['Subject'], msg['Body'])
      print 'Raw Date:', msg['Date']
      date_tuple = email.utils.parsedate_tz(msg['Date'])
      if date_tuple:
          local_date = datetime.datetime.fromtimestamp(
              email.utils.mktime_tz(date_tuple))
          print "Local Date:", \
              local_date.strftime("%a, %d %b %Y %H:%M:%S")
    return

def returnDownloadLinks():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        mail.login(username, password)
    except imaplib.IMAP4.error:
        print "LOGIN FAILED!!! "
    rv, mailboxes = mail.list()
    if rv == 'OK':
        print "Mailboxes:"
        print mailboxes

    rv, data = mail.select("inbox")
    if rv == 'OK':
        print "Processing mailbox...\n"
        results = process_mailbox(mail) # ... do something with emails, see below ...
        mail.close()
    mail.logout()
    return results

values = returnUsernamePassword()
username = values[0]
password = values[1].rstrip('\r\n')

returnDownloadLinks()