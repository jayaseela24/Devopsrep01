import os
import requests

file = open("./Scripts/apisnames.txt", "r")
apis = file.readlines()
envdomain = '.qa.revxplatform.com'
revxuisubdomain = 'revxui'


for api in apis:
    api = api.rstrip()
    #url = f'https://{repo.rstrip()}{envdomain}/health'
    print(api.ljust(65), end =" | ")
    try:
        response = ''
        status_code = ''
        if api.endswith('health') or api.endswith('/') or api.endswith('ping') or api.endswith('status'):
            res = requests.get( api )
        elif 'graphapi' in api:
            payload = f'{{"query":"query ($domain: String!) {{TenantCredentials(domain: $domain) {{ clientId }}  }}","variables":{{"domain":"{revxuisubdomain}{envdomain}"}}}}'
            res = requests.post( api, data=payload, headers= {'Content-Type': 'application/json', 'Accept': 'application/vnd.github+json'} )
        
        response = res.content.decode("utf-8")
        status_code = res.status_code
        if status_code == 200:
            print('Healthy')
        else:
            #print(f'{status_code} {res.reason} - {response}')
            print(f'{status_code} {res.reason}')
        
    except requests.exceptions.RequestException as e:
        print('Exception: ', e)
        print()
    print('-'*100)