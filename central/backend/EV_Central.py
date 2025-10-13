import requests
import time

URL_DB = "http://ev-db-controller:4000/CPs"
URL_FRONT = "http://ev-db-controller:3000/CPs"

try:
  time.sleep(5)
  response = requests.get(URL)
  print("Status: ", response.status_code)
  print(response.json())  
except requests.exceptions.RequestException as e:
  print(e)
    
time.sleep(1)





