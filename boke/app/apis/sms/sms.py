from twilio.rest import Client
import json

with open('sms/creds.json') as f:
    data = json.load(f)
    account_sid, auth_token = data['sid'], data['tok']

client = Client(account_sid, auth_token)

msg = f'test'

sms = client.messages.create(body=msg, from_='+12016279612', to='+905392346686')



