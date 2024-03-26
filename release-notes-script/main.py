import os
import requests
import json
from bs4 import BeautifulSoup
from atlassian import Confluence
from datetime import datetime
import pytz
import urllib.parse

class ScrapyData:
    def __init__(self,api_url1, confluence_url, base_url, username,api_token, page_no,services_to_deploy_str,deployment_type,target_environment):
        self.api_url1 = api_url1
        self.confluence_url = confluence_url
        self.base_url = base_url
        self.username = username
        self.api_token = api_token
        self.pageNo = page_no
        self.services_to_deploy_str = services_to_deploy_str
        self.deployment_type = deployment_type    
        self.target_environment = target_environment
    
    def getversion(self):
        services_to_deploy_str = self.services_to_deploy_str.replace("'", '"')
        try:
        # Convert the JSON string to a Python dictionary
            services_to_deploy = json.loads(services_to_deploy_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from 'services_to_deploy': {e}")
            services_to_deploy = {}  # Fallback to an empty dictionary
    
        # Write the Python dictionary to a JSON file
        with open('services_to_deploy.json', 'w', encoding='utf-8') as file:
            json.dump(services_to_deploy, file, indent=4)

    def confluencePage(self):
        # Create a timezone object for Central Standard Time
        cst = pytz.timezone('America/Chicago')
        utc_now = datetime.now(pytz.utc)
        # Make the current time timezone-aware (UTC)
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        # Convert UTC time to CST
        cst_now = utc_now.astimezone(cst)
        auth = requests.auth.HTTPBasicAuth(self.username, self.api_token)

        # Prepare your headers
        headers = {
           "Accept": "application/json",
           "Content-Type": "application/json"
        }
        add_datetime = cst_now.strftime("%m-%d-%Y")
        datetime_with_min = cst_now.strftime("%m-%d-%Y %H:%M")
        confluence = Confluence( url=self.confluence_url,username=self.username,password=self.api_token,api_version="cloud")
        if deployment_type == 'Full-Deployment' and target_environment == "REF":
            title = f"REF-Full Deployment(WIP) Release Notes-{add_datetime}"
        elif deployment_type == 'Full-Deployment' and target_environment == "STG":
            title = f"Staging-Full Deployment(WIP) Release Notes-{add_datetime}"
        elif deployment_type == 'Full-Deployment' and target_environment == "PRD":
            title = f"PROD-Full Deployment(WIP) Release Notes-{add_datetime}"
        else:
            title = f"{target_environment}-Partial Deployment(WIP) Release Notes-{datetime_with_min}"

        space_key = "DevOps"
        info = []
        body = f"""
            <table>
                <tr>
                    <th><strong>Service</strong></th>
                    <th><strong>Previous Version</strong></th>
                    <th><strong>Deploy Version</strong></th>
                    <th><strong>Changes</strong></th>
                </tr>
            </table>
            """
        page = confluence.get_page_id(space=space_key, title=title)
        if page:
            confluence.remove_page(page, status=None, recursive=False)
        confluence.create_page(space=space_key, title=title, body=body, type='page', representation='storage',full_width=True)
        search_url = f"{self.api_url1}?title={title}&spaceKey={space_key}&expand=body.storage"
        search_response = requests.get(search_url, headers=headers, auth=auth)
        if search_response.status_code == 200:
            page = confluence.get_page_by_title(space=space_key, title=title)
            page_id = page['id']
            link = f"https://revenuesolutions.atlassian.net/wiki/spaces/{space_key}/pages/{page_id}"
            info.append({
                'page_id':page_id,
                'link':link
            })
            print(f"Page has been created Successfully: {link}")
            if info:
                with open("info.json", 'w', encoding='utf-8') as json_file:
                    json.dump(info, json_file, indent=4)

confluence_url = os.environ.get('CONFLUENCE_URL')
base_url = os.environ.get('BASE_URL')
username = os.environ.get('USERNAME')
api_token = os.environ.get('API_TOKEN')
page_no = os.environ.get('PAGE_NO')
api_url1 = os.environ.get('API_URL1')
services_to_deploy_str = os.environ.get('services_to_deploy', '{}')
deployment_type = os.environ.get('deployment_type')
target_environment = os.environ.get('target_environment')

scrapy_instance = ScrapyData(api_url1,confluence_url,base_url,username,api_token,page_no,services_to_deploy_str,deployment_type,target_environment)
scrapy_instance.confluencePage()
scrapy_instance.getversion()
