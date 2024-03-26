import random
import string
import datetime
import requests
import time
import os

# edit the following variables
owner = "revenue-solutions-inc" 
repo = "RevX-Katalon"
workflow = "ci-cd-smoke-autodeployment.yml"
token = os.environ.get('GITHUBTOKEN', 0)
run_identifier = os.environ.get('SMOKETEST_RUN_ID', '')

authHeader = { "Authorization": f"Token {token}" }

# generate a random id
# run_identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
# filter runs that were created after this date minus 5 minutes
delta_time = datetime.timedelta(minutes=30)
run_date_filter = (datetime.datetime.utcnow()-delta_time).strftime("%Y-%m-%dT%H:%M") 

# r = requests.post(f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow}/dispatches",
#     headers= authHeader,
#     json= {
#         "ref":"master",
#         "inputs":{
#             "id": run_identifier
#         }
#     })

# print(f"dispatch workflow status: {r.status_code} | workflow identifier: {run_identifier}")
workflow_conclusion = ""

while workflow_conclusion == "":
        
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/runs?created=%3E{run_date_filter}",
        headers = authHeader)
    runs = r.json()["workflow_runs"]

    if len(runs) > 0:
        for workflow in runs:
            jobs_url = workflow["jobs_url"]
            print(f"get jobs_url {jobs_url}")

            r = requests.get(jobs_url, headers= authHeader)
            
            jobs = r.json()["jobs"]
            if len(jobs) > 0:
                # we only take the first job, edit this if you need multiple jobs
                job = jobs[0]
                steps = job["steps"]
                if len(steps) >= 2:
                    second_step = steps[1] # if you have position the run_identifier step at 1st position
                    if second_step["name"] == run_identifier:
                        workflow_id = job["run_id"]
                        conclusion = job["conclusion"]
                        print(f"Run found with ID: {workflow_id}, with conclusion == {conclusion}")
                        
                        if conclusion == "success" or conclusion == "cancelled" or conclusion == "failure":
                            workflow_conclusion = conclusion
                            break

                else:
                    print("waiting for steps to be executed...")
                    time.sleep(3)
            else:
                print("waiting for jobs to popup...")
                time.sleep(3)
    else:
        print("waiting for workflows to popup...")
        time.sleep(3)

print(f"workflow_conclusion: {workflow_conclusion}")
print(f'::set-output name=test_result::{workflow_conclusion}')