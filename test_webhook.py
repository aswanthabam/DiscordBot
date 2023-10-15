import requests, os, json
from dotenv import load_dotenv
load_dotenv()
web_url = os.getenv("WEBHOOK_URL")
op1 = int(input("""What you want to do?
  1) Create Channel
  2) Create Role\nChoose: """))
if op1 == 1:
  name = input("Enter channel name: ")
  payload = {
    "type":"create_channel",
    "name":name
  }
elif op1 == 2:
  name = input("Enter role name: ")
  payload = {
    "type":"create_role",
    "name":name
  }
data = json.dumps(payload)
payload = {
  'content':data
}
response = requests.post(web_url,json=payload,headers={'Content-Type':'application/json'})
if response.status_code != 200 and response.status_code != 204:
  print("Eroor")
  print(response.text)
else:print("Success,",response)