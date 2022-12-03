from flask import Flask, request
import requests
from pythonping import ping 

import ip_config
import crud

app = Flask(__name__)


global memory_datastore 
global partition_leader
global read_value 

read_value = "none"
memory_datastore = {"msg": "hello"}
partition_leader = False


def sendData(command, key="none", value='none'):
  global memory_datastore
  global read_value

  if command == "read":
    crud.CRUD.read(memory_datastore, key)
  elif command == "create":
    crud.CRUD.create(memory_datastore, key, value)
  elif command == "update":
    crud.CRUD.update(memory_datastore, key, value)
  elif command == "delete":
    crud.CRUD.delete(memory_datastore, key)
  
  # payload = {"key" : key,
  #            "value" : value}
  
  if command == "read":
    if key in memory_datastore.keys():
      return(memory_datastore.get(key))
    else:
      payload = {"key" : key}
      read_value = "none"
      post = requests.post("http://"+ ip_config.current_ip + ":11000/s3-reserve/read", json = payload)
      while read_value == "none":
        pass
  
      return read_value
  
  elif command == "create":
    payload = {"key" : key,
             "value" : value}
    post = requests.post("http://"+ ip_config.current_ip + ":11000/s3-reserve/create", json = payload)
    return "data has been added"
  elif command == "update":
    payload = {"key" : key,
             "value" : value}
    post = requests.post("http://"+ ip_config.current_ip + ":11000/s3-reserve/update", json = payload)
    return "data has been updated"
  elif command == "delete":
    payload = {"key" : key}
    post = requests.post("http://"+ ip_config.current_ip + ":11000/s3-reserve/delete", json = payload)
    return "data has been deleted"
  elif command == "readAll":
    return memory_datastore

@app.route('/s2', methods=['POST'])
def receive():   
  global memory_datastore

  res = request.get_json() 
  memory_datastore = res
 
  return memory_datastore


@app.route('/s2-reserve/<Command>', methods=['GET', 'POST'])
def answer(Command):   
  global memory_datastore
  global read_value

  res = request.get_json() 
  if Command == "read":
    read_value = res['value']
    return str(res['value'])
 
  return memory_datastore


# sync route
@app.route('/s2-sync', methods=['GET', 'POST'])
def sync_answer():   
  global memory_datastore

  payload = memory_datastore
  post = requests.post("http://"+ ip_config.current_ip + ":9000/s1-sync", json = payload)
  
  return memory_datastore


@app.route('/s2/<Command>', methods=['GET'])
def send(Command):   
  global memory_datastore
  global partition_leader
  
  res = request.get_json() 
  
  key_value_dict = {}
  key_value_dict.update(res)

  try:
    payload = {"status" : "check"}
    post = requests.post("http://"+ ip_config.current_ip + ":9000/s1", json = payload)
    return memory_datastore
  except:
    for _key in key_value_dict:
      if _key == "key":
        key = res['key']
      elif _key == "value":
        value = res['value']

    if len(key_value_dict) == 1:    
      return(sendData(Command, key))
    elif len(key_value_dict) == 2:  
      return(sendData(Command, key, value))
    elif len(key_value_dict) == 0:
      return(sendData(Command))
  

def get_data(response):
  memory_datastore = response
  print(memory_datastore)
    
if __name__ == '__main__':
  app.run(debug=False, host="0.0.0.0", port=7000, use_reloader=False)
 