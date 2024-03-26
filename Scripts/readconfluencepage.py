from atlassian import Confluence
import pandas as pd
from datetime import datetime
from pytz import timezone
import pytz
from random import randrange
from time import sleep
import os

conf_site = 'https://revenuesolutions.atlassian.net'
conf_user = 'aarizmendi@rsimail.com'
conf_pass = ""#credentials are not working, we need a token here
service_name=os.getenv("INPUT_SERVICE")
version_number=os.getenv("INPUT_VERSION")
env_name=""

page_title = 'Set+Node+selector+in+deployment+files'
page_space = 'DevOps'
page_id = '448757803'
date_format='%m/%d/%Y %H:%M:%S %Z'
date = datetime.now(tz=pytz.utc)
date = date.astimezone(timezone('US/Pacific'))
# connect to Confluence
conf = Confluence(url=conf_site, username=conf_user, password=conf_pass)

# resolve page ID
page_id = conf.get_page_id(page_space, page_title)

# optonal: get current page content, in case you want to base your editing on that
page = conf.get_page_by_id(page_id, expand='body.storage')


page_content = page['body']['storage']['value']
print(page_content)
table = pd.read_html(page_content)
table = table[0]  # Only one table on the page
print(table)
df = pd.DataFrame(data=table)