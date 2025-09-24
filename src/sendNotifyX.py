import requests
import json
from types import SimpleNamespace
import config

config_info = config.read_config_info()


def send(msg_content="", msg_title="",  msg_description=""):
    if config_info.notifyX.status==False:
        return
    
    if msg_content != "":
        config_info.notifyX.message.content  = msg_content
    if msg_content != "":
        config_info.notifyX.message.title  = msg_title
    if msg_content != "":
        config_info.notifyX.message.description  = msg_description
    if config_info.notifyX.status==False:
        return
    url = "https://www.notifyx.cn/api/v1/send/"+config_info.notifyX.key
    payload = {
        "title": config_info.notifyX.message.title,
        "content": config_info.notifyX.message.content,
        "description": config_info.notifyX.message.description
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(response.json())