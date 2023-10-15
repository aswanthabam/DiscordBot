import requests, os, json
from dotenv import load_dotenv
load_dotenv()
web_url = os.getenv("WEBHOOK_URL")
op1 = int(input("""What you want to do?
  1) Create Channel
  2) Create Role\nChoose: """))

def permission_map(i):
  if i == 1:return "normal"
  elif i == 2:return "admin"
  elif i == 3:return "new"
  elif i == 4:return "banned"
  else: return None
def permission_map2(i):
  if i == 1:return "send_messages"
  elif i == 2: return "read_messages"
  else: return None

if op1 == 1:
  name = input("Enter channel name: ")
  perms = [permission_map(int(x)) for x in input("""Channel Access Roles:
  1) normal
  2) admin
  3) new commers
  4) banned
Choose: """).split()]
  payload = {
    "type":"create_channel",
    "name":name,
    "permissions":perms
  }
elif op1 == 2:
  name = input("Enter role name: ")
  perms = [permission_map2(int(x)) for x in input("""Channel Access Roles:
  1) send_message
  2) read_message
Choose: """).split()]
  
  payload = {
    "type":"create_role",
    "name":name,
    "permissions":perms
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