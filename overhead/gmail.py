from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from apiclient import errors
from overhead.functions import scraperLogger
import base64
import os

class GmailSender():
    
    def __init__(self, client_secret):
        """
        `client_secret` (str): .json file from Google Developer's API Console. Must specify "Other" application to create the correct API key.
        """
        
        store = file.Storage(os.path.join(os.path.dirname(__file__), 'storage.json'))
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret, 'https://www.googleapis.com/auth/gmail.send')
            credentials = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=credentials.authorize(Http()))
            
    def createMessage(self, recipient, subject, message_text):
    
      message = MIMEText(message_text)
      message['from'] = ''
      message['to'] = recipient
      message['subject'] = subject
      msg = bytes( message.as_string(), 'utf-8' )
      encoded = base64.urlsafe_b64encode(msg)
      self.message = {'raw': encoded.decode('utf-8') }
      
    def sendMessage(self, recipient, subject, body):
        
        self.createMessage(recipient, subject, body)
        
        try:
            message = (self.service.users().messages().send(userId='me', body=self.message).execute())
            scraperLogger.info('Message ID: %s' % message['id'])
        except (errors.HttpError, Exception) as e:
            scraperLogger.debug('An error has occurred: %s' % e)

if __name__ == '__main__':
    
    Sender = GmailSender('client_secret.json')
    Sender.sendMessage('alex.petralia@gmail.com', 'Test subject', 'Test body')