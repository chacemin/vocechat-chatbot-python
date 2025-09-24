import json
import requests
from requests.exceptions import RequestException
import logging 
import config
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 获取配置
config_info =config.read_config_info()

class DeepSeekChat:
    def __init__(self):
        self.api_key = config_info.deepseek.api_key
        self.api_url = f"{config_info.deepseek.base_url}/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.conversation_history = []  # 用于存储对话历史，维护上下文
        if config_info.deepseek.status == False:
           logger.info(f"系统配置为不启用deepseek服务")
    
    def send_message(self, user_message):
        if config_info.deepseek.status == False:
           return "deepseek未启用，不能回答你的问题哦"
        """发送消息并获取响应，自动维护对话上下文"""
        logger.info(f"deepseek收到用户信息 {user_message}")
        if user_message == 'clear':
            logger.info(f"系统: {chat.clear_history()}")
            return "对话历史已清除"
        # return "好的"
        # 将用户消息添加到对话历史
        self.conversation_history.append({"role": "user", "content": user_message})
        if len(self.conversation_history) > 20 : # 限制历史记录长度
           self.conversation_history.pop(0)

        
        # 准备请求数据
        payload = {
            "model": config_info.deepseek.model,  # DeepSeek聊天模型
            "messages": self.conversation_history,
            "temperature": 0.7,       # 控制输出的随机性
            "max_tokens": 1024        # 最大响应长度
        }
        
        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # 将AI响应添加到对话历史
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求错误: {e}")
            return None
        except KeyError as e:
            logger.error(f"解析响应错误: 缺少关键字段 {e}")
            return None
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        return "对话历史已清空"
    
    def get_history(self):
        """获取当前对话历史"""
        return self.conversation_history



