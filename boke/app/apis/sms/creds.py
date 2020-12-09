import json

data = dict()
sid = input('Enter sid: ')
tok = input('Enter auth token: ')
data['sid'] = sid
data['tok'] = tok

outfile = 'creds.txt'
with open(outfile, 'w') as f:
    json.dump(data, f)
