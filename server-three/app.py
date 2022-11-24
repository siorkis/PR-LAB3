from flask import Flask, request
import requests
from pythonping import ping 

import ip_config
import crud

app = Flask(__name__)

global memory_datastore 
memory_datastore = {"msg": "hello"}

partition_leader = False

def sendData(command, key="none", value='none'):
  
    if command == "read":
      crud.CRUD.read(memory_datastore, key)
    elif command == "create":
      crud.CRUD.create(memory_datastore, key, value)
    elif command == "update":
      crud.CRUD.update(memory_datastore, key, value)
    elif command == "delete":
      crud.CRUD.delete(memory_datastore, key)

    if command == "read":
      payload = {"value" : memory_datastore.get(key)}
      post = requests.post("http://"+ ip_config.current_ip + ":10000/s2-reserve/read", json = payload)
      print(payload, "data has been sended to server_2")
      return(memory_datastore.get(key))

    # elif command == "create":
    #   return "data has been added"
    # elif command == "update":
    #   return "data has been updated"
    # elif command == "delete":
    #   return "data has been deleted"
    elif command == "readAll":
      return memory_datastore

@app.route('/s3', methods=['POST'])
def receive():   
  global memory_datastore

  res = request.get_json() 
  memory_datastore = res
 
  return memory_datastore

@app.route('/s3-reserve/<Command>', methods=['GET', 'POST'])
def send_back(Command):
  global memory_datastore

  res = request.get_json() 
  
  key_value_dict = {}
  key_value_dict.update(res)

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

  return memory_datastore

@app.route('/s3/<Command>', methods=['GET'])
def send(Command):   
  global memory_datastore

  res = request.get_json() 
  
  key_value_dict = {}
  key_value_dict.update(res)

  if partition_leader:

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

  return memory_datastore

def get_data(response):
  memory_datastore = response
  print(memory_datastore)
    
if __name__ == '__main__':
  app.run(debug=False, host="0.0.0.0", port=8000, use_reloader=False)
  