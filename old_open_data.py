'''
from pydap.client import open_url
from pydap.cas.urs import setup_session

dataset_url = 'https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002/1979/001/NLDAS_FORA0125_H.A19790101.1300.002.grb'
username = 'yymjzq'
password = '6912448zZ'

session = setup_session(username, password, check_url=dataset_url)
dataset = open_url(dataset_url, session=session)
'''

import requests, base64

params={'client_id' : 'e2WVk8Pw6weeLUKZYOxvTQ', 
        'response_type' : 'code',
        'redirect_uri' : 'https://hydro1.gesdisc.eosdis.nasa.gov/data-redirect',
		'state' : 'aHR0cHM6Ly9oeWRybzEuZ2VzZGlzYy5lb3NkaXMubmFzYS5nb3YvZGF0YS9OTERBUy9OTERBU19GT1JBMDEyNV9ILjAwMi8xOTc5LzAwMS9OTERBU19GT1JBMDEyNV9ILkExOTc5MDEwMS4xMzAwLjAwMi5ncmI'
		}

b64Val = base64.b64encode(b'yymjzq:6912448zZ')
authVal = 'Basic eXltanpxOjY5MTI0NDh6Wg=='
headers = {'Authentication' : authVal}
r = requests.get('https://urs.earthdata.nasa.gov/oauth/authorize/', params=params, headers=headers)
print(r.status_code)
print(r.cookies)

print('################')

reqForData = requests.get('https://hydro1.gesdisc.eosdis.nasa.gov/data/NLDAS/NLDAS_FORA0125_H.002', cookies=r.cookies, stream=True)
print(r.status_code)
print(r.headers)
with open('NLDAS.grb', 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)