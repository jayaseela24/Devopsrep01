# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd



url = "https://revenuesolutions.atlassian.net/wiki/rest/api/content/448757803?expand=body.storage"

auth = HTTPBasicAuth("aarizmendi@rsimail.com", "ATATT3xFfGF0g44lyQOVun40zcoB5BXlbvHmvr6Ea5hF2GitCFMBilKgrNl4y0aalwVjcDBa8kezns2vxhNvaMFFw9XDIicaQHMMZJZmTB8VYfMvq5iESrBXoc3AzAABpU9D4ZekCBZIWK4cFZ6uN440Z29bNEqvqHvVgn_C5Eftf87ps0a7kYU=D19C7DD8")

headers = {
  "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)
result=json.loads(response.text)
page_content = result['body']['storage']['value']
# print('body: ', page_content)

table = pd.read_html(page_content)
table = table[0]  # Only one table on the page
df = pd.DataFrame(data=table)

source_environment = ['REF']
target_environment = ['STG']

print('Source versions:')
source_versions = df.loc[(df['Environment'].isin(source_environment))]
print('df: ', source_versions)

print('Target versions:')
target_versions = df.loc[(df['Environment'].isin(target_environment))]
print('df: ', target_versions)

print('verifying the services to be deployed..')
services_to_deploy = []
target_versions = target_versions.values
for service in source_versions.values:
  try:
    service_name = service[0]
    source_version = service[2]
    target_version = df.loc[df['Service'].isin([service_name]) & df['Environment'].isin(target_environment), 'Version'].fillna(0).astype(int).values[0]
    source_env_version = int(source_version)
    target_env_version = int(target_version)
    
    # if source_env_version == target_env_version:
      # print(f'\tSkipping {service_name}, same version in both env: v{source_env_version}')
    # elif source_env_version > target_env_version:
    print(service[0], source_environment, source_env_version, ' --> ', target_environment, target_env_version)
    services_to_deploy.append(
      {
        "service_name": service_name,
        "service_repository": f'https://github.com/revenue-solutions-inc/{service_name}.git',
        "source_version": f'v{source_version}',
        "target_version": f'v{target_version}'
      }
    )
  except:
    print(f'{service_name}: Error while getting the target environment')
# print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

services_to_deploy_mapping = {
  "source_environment": source_environment[0],
  "target_environment": target_environment[0],
  "deployment": {
    "sql_migrations": 'true',
    "sql_fd": 'true',
    "aks": 'true',
    "function_app": 'true',
  },
  "services_to_deploy": services_to_deploy
}

json_str = json.dumps(services_to_deploy_mapping, indent=2)
json_file = open( "services_to_deploy_mapping.json", 'w')
json_file.write(json_str)
json_file.close()