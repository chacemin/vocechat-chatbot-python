import requests
from requests.exceptions import RequestException
import config
from deepseek_server import DeepSeekChat
from gemini_server import GeminiChat
from baidu_server import BaiduChat
import logging 
from urllib.parse import quote
import json
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 读取配置
config_info =config.read_config_info()
chat_deepseek = DeepSeekChat()
chat_gemini = GeminiChat()
chat_baidu = BaiduChat()
img_url = None

def excute_event(event):
    """
    处理VoceChat频道发送消息
    Args:
        event: 消息内容
    
    """
    msg_content=event.get('content', {})
    msg_type = event.get('content_type', {})
    #消息类型，text/plain：纯文本消息，text/markdown：markdown消息，vocechat/file：文件类消息
    global img_url
    if msg_type == "text/plain" or msg_type == "text/markdown":
        #respose_chat(msg_content)
        respose_chat(msg_content)
        
    if msg_type == "vocechat/file":
        # 这里只处理图片类消息如果不是图片类消息就不处理
        file_type = event["properties"]["content_type"]
        if "image" in file_type:
            img_url = f"{config_info.vocechat.host}/api/resource/file?file_path={quote(msg_content)}"
            print(f"图片地址：{img_url}")
            send_to_channel(msg_content="请问你想让我如何处理图片？")
        else:
            send_to_channel(msg_content="暂不支持解析图片之外的文件")


def setSecret(secret):
    # 1. 构建请求URL（替换gid）
    api_url = f"{config_info.vocechat.host}/api/bot/secret"
    
    # 2. 配置请求头（必带x-api-key和Content-Type）
    headers = {
        "x-api-key": config_info.vocechat.bot_api_key,
        "Content-Type": "application/json; charset=utf-8"
    }
    logger.info(f"密码：{secret}")
    try:
        # 3. 发送POST请求（请求体为纯文本）
        response = requests.post(
            url=api_url,
            headers=headers,
            data=json.dumps({"secret":secret})  # 文本内容直接作为请求体
        )
        
        # 4. 校验响应状态（200为成功，其他为失败）
        response.raise_for_status()  # 若状态码非200，抛出HTTPError
        
        # 成功：返回消息ID（VoceChat会返回消息唯一标识）
        logger.info(f"设置密码成功：{response}")
    
    except RequestException as e:
        # 失败：捕获网络错误或响应错误，打印详细信息
        error_msg = f"设置密码失败：{str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f" | 响应状态码：{e.response.status_code} | 响应内容：{e.response.text}"
        logger.error(error_msg)

def send_to_channel(msg_content="欢迎加入频道！") -> None:
    """
    向VoceChat指定频道发送文本消息
    Args:
        msg_content: 文本消息内容（如"欢迎加入频道！"）
    
    Raises:
        RequestException: HTTP请求异常（网络错误、响应错误等）
    """
    deploy_domain=config_info.vocechat.host
    target_gid=config_info.vocechat.target_gid
    bot_api_key=config_info.vocechat.bot_api_key
    # 1. 构建请求URL（替换gid）
    api_url = f"{deploy_domain}/api/bot/send_to_group/{target_gid}"
    
    # 2. 配置请求头（必带x-api-key和Content-Type）
    headers = {
        "x-api-key": config_info.vocechat.bot_api_key,
        "Content-Type": "text/markdown"  # 文本消息固定Content-Type
    }
    
    try:
        # 3. 发送POST请求（请求体为纯文本）
        response = requests.post(
            url=api_url,
            headers=headers,
            data=msg_content  # 文本内容直接作为请求体
        )
        
        # 4. 校验响应状态（200为成功，其他为失败）
        response.raise_for_status()  # 若状态码非200，抛出HTTPError
        
        # 成功：返回消息ID（VoceChat会返回消息唯一标识）
        logger.info(f"文本消息发送成功！消息ID：{response.text}")
    
    except RequestException as e:
        # 失败：捕获网络错误或响应错误，打印详细信息
        error_msg = f"文本消息发送失败：{str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f" | 响应状态码：{e.response.status_code} | 响应内容：{e.response.text}"
        logger.error(error_msg)

def respose_chat(msg=""):
   
    #print(f'envent:{envent}')
    global img_url
    if "" == msg:
        send_to_channel(msg_content= "你未发送任何消息")
    response = ""
    if "联网搜索" in msg:
        if config_info.baidu.status :
            send_to_channel(msg_content= "baidu思考中请稍后....... \n\n如果要获取联网消息，请在提问时加入关键字：联网搜索")
            response = chat_baidu.send_message(msg.replace("联网搜索","")) # 替换掉联网搜索
    else:
        if config_info.deepseek.status :
            send_to_channel(msg_content= "deepseek思考中请稍后.......\n\n如果要获取联网消息，请在提问时加入关键字：联网搜索")
            if img_url:
                response = "deepseek暂时不支持图片处理"
                img_url = None
            else:
                response = chat_deepseek.send_message(user_message=msg)
        elif config_info.gemini.status :
            send_to_channel(msg_content= "gemini思考中请稍后.......\n\n如果要获取联网消息，请在提问时加入关键字：联网搜索")
            if img_url:
                response = chat_gemini.send_message(user_message=msg,image_path=img_url)
                img_url = None
            else:
                response = chat_gemini.send_message(user_message=msg)
        else:
            send_to_channel(msg_content= "AI未启用，不能回答你的问题哦")
            return
      
     # 格式化返回给VoceChat的响应
    # 1. 发送文本消息
    send_to_channel(msg_content = response)
