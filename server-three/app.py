from this import d
from flask import Flask, request
import threading

import json
import random
import time
import requests

import ip_config
import crud

app = Flask(__name__)


global memory_datastore 
memory_datastore = {"msg": "hello"}

partion_leader = False

def sendData(command, response):
    key = response['key']
    value = response['value']
    
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
    post = requests.post("http://"+ ip_config.current_ip + ":9000/s1/read", json = payload)
    print(payload, "data has been sended to server_1")

    if command == "read":
      return(memory_datastore.get(key))
    elif command == "create":
      return "data has been added"
    elif command == "update":
      return "data has been updated"
    elif command == "delete":
      return "data has been deleted"

@app.route('/s3/<Command>', methods=['POST'])
def send(Command):    
    res = request.get_json()
    if partion_leader:
      sendData(Command, res)
    else:
      get_data(res)
    return "data has been received from PL"

def get_data(response):
  memory_datastore = response
  print(memory_datastore)
    
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8000, use_reloader=False)
    
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