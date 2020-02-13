import requests
import json
import concurrent.futures
from time import sleep

executor = concurrent.futures.ThreadPoolExecutor()
tasks = []

def start():
    count = 0
    API_ENDPOINT = "" #project endpoint
    api_login = ""
    api_password = ""
    session = requests.Session()
    session.auth = (api_login, api_password)
    for x in range(1, 24000):
        future = executor.submit(threaded_create, x, API_ENDPOINT, session)
        tasks.append(future)
        if len(tasks) > 8:
            concurrent.futures.wait(tasks)

def threaded_create(x, API_ENDPOINT, session):
    # Create
    #print("Creating repo "+""+str(x))
    #data = {'name': x}
    #session.post(API_ENDPOINT, json=data)
    # Delete
    print("Deleting repo "+""+str(x))
    session.delete(API_ENDPOINT+"/"+str(x))

    start()
if __name__ == '__main__':