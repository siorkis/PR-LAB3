from flask import Flask, request
import requests
from pythonping import ping 
import threading
import ftplib

# from ..extensions import ip_config
# from ..extensions import crud

import ip_config
import crud

app = Flask(__name__)

memory_datastore = {"msg": "hello"}
key_value_dict = {} 


partition_leader = True

# avoid data corruption
# avoid data duplicate  
def sync_call():
  payload = {"sync" : "sync"}
  post = requests.post("http://"+ ip_config.current_ip + ":10000/s2-sync", json = payload)
  post = requests.post("http://"+ ip_config.current_ip + ":11000/s3-sync", json = payload)


# sync route
@app.route('/s1-sync', methods=['GET', 'POST'])
def answer():   
  global memory_datastore
  
  res = request.get_json() 

  compare_list = {k: memory_datastore[k] for k in memory_datastore if k in res and memory_datastore[k] == res[k]} 
  if len(compare_list) != (len(memory_datastore) / 2) or len(compare_list) != ((len(memory_datastore)+1) / 2):
    sendData()
    return "data has been restored"
  else:
    return "data has been synced"


def sendData(command, key="none", value='none'):
  global memory_datastore

  if command == "read":
    crud.CRUD.read(memory_datastore, key)
  elif command == "create":
    crud.CRUD.create(memory_datastore, key, value)
  elif command == "update":
    crud.CRUD.update(memory_datastore, key, value)
  elif command == "delete":
    crud.CRUD.delete(memory_datastore, key)

  data_amount = len(memory_datastore)

  bound = data_amount // 2 

  first_part_data  = {}
  second_part_data = {}
  
  count = 0

  for _key, _value in memory_datastore.items():
    if data_amount == 1:
      first_part_data = memory_datastore
      second_part_data = memory_datastore
    elif count < bound:
      first_part_data[_key] = _value
    else:
      second_part_data[_key] = _value
    count += 1

  post = requests.post("http://"+ ip_config.current_ip + ":10000/s2", json = first_part_data)
  print(first_part_data, "data has been sended to server_2")
  post = requests.post("http://"+ ip_config.current_ip + ":11000/s3", json = second_part_data)
  print(second_part_data, "data has been sended to server_3")
  
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
  elif command == "read2":
    return first_part_data
  elif command == "read3":
    return second_part_data
  elif command == "create-txt":
    
    # https://dlptest.com/ftp-test/
    HOSTNAME = "ftp.dlptest.com"
    USERNAME = "dlpuser"
    PASSWORD = "rNrKYTX9g7z3RgJRmxWuGHbeu"
    
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
    ftp_server.encoding = "utf-8"

    f = open(key+".txt", "w")
    f.write(str(value))
    f.close()
    filename = key+".txt"

    with open(filename, "rb") as file:
        # Command for Uploading the file "STOR filename"
        ftp_server.storbinary(f"STOR {filename}", file)

    # Get list of files
    ftp_server.dir()
    # Close the Connection
    ftp_server.quit()
  
  elif command == "read-txt":
    
    # https://dlptest.com/ftp-test/
    HOSTNAME = "ftp.dlptest.com"
    USERNAME = "dlpuser"
    PASSWORD = "rNrKYTX9g7z3RgJRmxWuGHbeu"

    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
    ftp_server.encoding = "utf-8"

    filename = key+".txt"

    with open(filename, "wb") as file:
      ftp_server.retrbinary(f"RETR {filename}", file.write)

    ftp_server.dir()
    file = open(filename, "r")
    print('File Content:', file.read())
    ftp_server.quit()



@app.route('/s1/', methods=['POST'])
def receive():
  global memory_datastore
 
  return memory_datastore

@app.route('/s1/<Command>', methods=['GET'])
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
  else:
     memory_datastore = res

  return memory_datastore

def get_data():
  return memory_datastore

    
if __name__ == '__main__':
  app.run(debug=False, host="0.0.0.0", port=6000, use_reloader=False)
  threading.Timer(60, sync_call).start()
