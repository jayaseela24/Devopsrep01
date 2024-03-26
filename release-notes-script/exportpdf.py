from atlassian import Confluence
import os
import json

class ExportConfluencePagepdf:
    def __int__(self,confluence_url, username, api_token):
        self.confluence_url = confluence_url
        self.username = username
        self.api_token = api_token
    
    def load_json(self,filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(e)

    def confluencepdf(self):
        confluence = Confluence(
            url=f'{self.confluence_url}',
            username=f'{self.username}',
            password=f'{self.api_token}',
            api_version="cloud"
        )

        page_details = self.load_json('info.json')
        for page in page_details:
            page_id = page['page_id']

        with open("release_notes.pdf", "wb") as pdf_file:
            pdf_file.write(confluence.get_page_as_pdf(page_id))


confluence_url = os.environ.get('CONFLUENCE_URL')
username = os.environ.get('USERNAME')
api_token = os.environ.get('API_TOKEN')

exportpdf = ExportConfluencePagepdf()
exportpdf.confluence_url = confluence_url
exportpdf.username = username
exportpdf.api_token = api_token
exportpdf.confluencepdf()
