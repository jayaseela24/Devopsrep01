import os
import subprocess
import re
import requests
import json
from atlassian import Confluence
from bs4 import BeautifulSoup


class InsertData:

    def __init__(self,confluence_url,username,api_token):

        self.confluence_url = confluence_url
        self.username = username
        self.api_token = api_token
        self.secret_value = os.environ.get('SECRET_VALUE', 'default_secret_value')

        page_details = self.load_json('info.json')
        for page in page_details:
            self.page_id = page['page_id']
        
        self.versions = self.load_json('services_to_deploy.json')
        
    def load_json(self,filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(e)

    def getPutJiraTicketUrl(self):
        new_data = []
        arrugment = self.load_json('services_to_deploy.json')
        linked_changes = []
        two_D_linked_issue_array = []
        source_environment = self.versions['source_environment']
        target_environment = self.versions['target_environment']
        for services_to_deploy in self.versions['services_to_deploy']:
            service_name = services_to_deploy['service_name']
            source_version = services_to_deploy['source_version']
            target_version = services_to_deploy['target_version']

            repo_url = f"{'https://github.com/revenue-solutions-inc/'}{service_name}"
            clone_url = repo_url.replace('https://', f'https://{self.secret_value}@')

            try:
                # Cloning the repository
                subprocess.run(['git', 'clone', '-b', 'develop', '--depth', '200', clone_url], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone {service_name}: {e}")

            command = f"cd {service_name} && ls && git fetch --tags && pwsh -File ../release-notes-script/rn1.ps1 -repository {service_name} -previousVersion {source_version} -targetVersion {target_version} -SecretValue {self.secret_value}"
            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            # Define a regex pattern for your specific URL format
            url_pattern = r'https://revenuesolutions\.atlassian\.net/browse/NEX-\d+'
            auth = requests.auth.HTTPBasicAuth(self.username,self.api_token)

            # Prepare your headers
            headers = {
               "Accept": "application/json",
               "Content-Type": "application/json"
            }

            # Extract URLs from the output
            urls = re.findall(url_pattern, result.stdout)
            changes = []
            

            for url in urls:
                issue_key = url.split('/')[-1]
                issue_url = f"{self.confluence_url}/rest/api/3/issue/{issue_key}?fields=summary,status,issuetype,issuelinks"
                
                response1 = requests.get(issue_url, headers=headers, auth=auth)
                if response1.status_code == 200:
                    issue_data = response1.json()
                    title = issue_data['fields']['summary']
                    status = issue_data['fields']['status']['name']
                    issue_type = issue_data['fields']['issuetype']
                    icon_url = issue_type.get('iconUrl')
                    # link = issue_data['fields'].get('issuelinks'):
                    for link in issue_data['fields'].get('issuelinks', []):
                        linked_issue_info = link.get('outwardIssue') or link.get('inwardIssue')
                        if linked_issue_info:
                            linked_issue_key = linked_issue_info['key']
                            if linked_issue_key.startswith('STL'):
                                linked_issue_url = f"{self.confluence_url}/rest/api/3/issue/{linked_issue_key}"
                                linked_response = requests.get(linked_issue_url, headers=headers, auth=auth)
                                if linked_response.status_code == 200:
                                    linked_issue_data = linked_response.json()
                                    linked_title = linked_issue_data['fields']['summary']
                                    if not any(entry['issue'] == linked_issue_key or entry['description'] == linked_title for entry in linked_changes):
                                        linked_changes.append({
                                            'issue': linked_issue_key,
                                            'description': linked_title
                                        })


                    changes.append({
                        'issue_key': issue_key,
                        'url': url,
                        'title': title,
                        'status': status,
                        'icon':icon_url
                    })
                else:
                    print("Failed to fetch issue data: Status code", response1.status_code)
            
            
            

            if changes:
                changes_html = ''.join([f'<a href="{change["url"]}"><img src={change["icon"]}/><b>{change["issue_key"]}:</b> {change["title"]} - <strong>{change["status"]}</strong></a><br/>' for change in changes])
            elif source_version == target_version:
                changes_html = "No Changes"
            else:
                changes_html = "No Jira Ticket"

            td_data=[service_name,source_version,target_version,changes_html]
            new_data.append(td_data)

        two_D_linked_issue_array.extend(linked_changes)
        print(two_D_linked_issue_array)

        confluence = Confluence(url=self.confluence_url,username=self.username,password=self.api_token,api_version="cloud")

        page_info = confluence.get_page_by_id(self.page_id, expand='body.storage')
        current_content = page_info['body']['storage']['value']

        # Use BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(current_content, 'html.parser')

        # Find the table - adjust this as needed to target the correct table
        table = soup.find('table')
        print(new_data)
        for row_data in new_data: # new_data is 2-D list
            new_row = soup.new_tag('tr')
            for cell_data in row_data:
            # If the cell data is HTML, parse and append it
                if isinstance(cell_data, str) and ('<' in cell_data and '>' in cell_data):
                    new_cells_html = BeautifulSoup(cell_data, 'html.parser')
                    new_cell = soup.new_tag('td')
                    new_cell.append(new_cells_html)
                    new_row.append(new_cell)
                else:
                    # Otherwise, treat it as text
                    new_cell = soup.new_tag('td')
                    new_cell.string = str(cell_data)
                    new_row.append(new_cell)

            table.append(new_row)

        # Update the content with the modified HTML
        modified_content = str(soup)

        # Update the page with the new content
        confluence.update_page(
            page_id=self.page_id,
            title=page_info['title'],  # Keep the same title
            body=modified_content,
            representation='storage',
            full_width=True
        )

        with open('STL_issue.json', 'w', encoding='utf-8') as file:
            json.dump(linked_changes, file, ensure_ascii=False, indent=4)

        print(f"Data Insert Successfully: https://revenuesolutions.atlassian.net/wiki/spaces/Devops/pages/{self.page_id}")

confluence_url = os.environ.get('CONFLUENCE_URL')
username = os.environ.get('USERNAME')
api_token = os.environ.get('API_TOKEN')

insertData = InsertData(confluence_url,username,api_token)

# insertData = InsertData()
insertData.getPutJiraTicketUrl()
