from flask import Flask, request
import threading

import json
import random
import time
import requests


# from ..extensions import ip_config
# from ..extensions import crud

import ip_config
import crud

app = Flask(__name__)

memory_datastore = {"msg": "hello"}
key_value_dict = {} 

partion_leader = True

def sendData(command, key="none", value='none'):
    # key = response['key']
    # value = response['value']
    
    # command = input(str("Choose the command: read, create, update, delete\n"))
    if command == "read":
      # key = input(str("enter filename "))
      crud.CRUD.read(memory_datastore, key)

    elif command == "create":
      # key = input(str("enter filename "))
      # value = input(str("enter file content "))
      crud.CRUD.create(memory_datastore, key, value)

    elif command == "update":
      # key = input(str("enter filename "))
      # value = input(str("enter new file content "))
      crud.CRUD.update(memory_datastore, key, value)

    elif command == "delete":
      # key = input(str("enter filename "))
      crud.CRUD.delete(memory_datastore, key)

    payload = memory_datastore
    print(payload, "PAYLOAD")
    post = requests.post("http://"+ ip_config.current_ip + ":10000/s2/read", json = payload)
    print(payload, "data has been sended to server_2")
    post = requests.post("http://"+ ip_config.current_ip + ":11000/s3/read", json = payload)
    print(payload, "data has been sended to server_3")
    
    if command == "read":
      return(memory_datastore.get(key))
    elif command == "create":
      return "data has been added"
    elif command == "update":
      return "data has been updated"
    elif command == "delete":
      return "data has been deleted"
    elif command == "readAll":
      return memory_datastore

@app.route('/s1/<Command>', methods=['GET'])
def send(Command):   
  res = request.get_json() 
  
  key_value_dict = {}
  key_value_dict.update(res)

  
  if partion_leader:

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

def get_data():
  return memory_datastore

    
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=6000, use_reloader=False)
    
    # flask_thread = threading.Thread(target=lambda: app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False))

    # threads = list()
    # threads.append(flask_thread)
    # for index in range(6):
    #     print("Main    : create and start thread.", index)
    #     x = threading.Thread(target=sendData, args=())
    #     threads.append(x)

    # for index, thread in enumerate(threads):
    #     print("Main    : before joining thread.", index)
    #     thread.start()
    #     print("Main    : thread done", index)