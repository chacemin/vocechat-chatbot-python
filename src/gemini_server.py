import json
import requests
from requests.exceptions import RequestException
import logging 
import config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取配置
config_info = config.read_config_info()

class GeminiChat:
    def __init__(self):
        self.api_key = config_info.gemini.api_key
        self.api_url = f"{config_info.gemini.base_url}/v1beta/models/{config_info.gemini.model}:generateContent?key={self.api_key}"
        self.headers = {
            "Content-Type": "application/json",
        }
        self.conversation_history = []  # 用于存储对话历史，维护上下文
        if config_info.gemini.status == False:
           logger.info(f"系统配置为不启用gemini服务")
    
    def send_message(self, user_message, image_path=None):
        if config_info.gemini.status == False:
           return "gemini未启用，不能回答你的问题哦"
        """发送消息并获取响应，自动维护对话上下文"""
        logger.info(f"gemini收到用户信息 {user_message}")
        if user_message == 'clear':
            logger.info(f"系统: {self.clear_history()}")
            return "对话历史已清除"
        
        # 构建parts列表，包含文本和图片
        parts = [{"text": user_message}]
        
        # 如果提供了图片路径，添加图片内容
        if image_path:
            try:
                # 判断是否为URL
                if image_path.startswith('http://') or image_path.startswith('https://'):
                    # 从URL获取图片内容
                    image_data = self._get_image_from_url(image_path)
                else:
                    # 本地文件路径
                    image_data = self._encode_image(image_path)
                
                # 添加图片内容到parts
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",  # 根据实际情况调整MIME类型
                        "data": image_data
                    }
                })
            except Exception as e:
                logger.error(f"处理图片时出错: {e}")
                # 如果图片处理失败，只发送文本
                pass
        
        # 将用户消息添加到对话历史
        self.conversation_history.append({"role": "user", "parts": parts})
        if len(self.conversation_history) > 20 : # 限制历史记录长度
           self.conversation_history.pop(0)

        
        # 准备请求数据
        payload = {
            "contents": [{
                "role": "user",
                "parts": parts
            }]
        }
        
        # 如果有历史记录，添加到请求中
        if len(self.conversation_history) > 1:
            # 构建历史记录内容
            history_contents = []
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    history_contents.append({"role": "user", "parts": msg["parts"]})
                else:  # assistant
                    history_contents.append({"role": "model", "parts": [{"text": msg["parts"][0]["text"]}]})
            
            # 重置内容，只保留最新的用户消息和历史
            payload["contents"] = history_contents
        
        try:
            # 发送请求
            response = requests.post(
                url=self.api_url,
                data=json.dumps(payload)
            )
            
            # 检查响应状态
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取AI响应内容
            ai_response = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # 将AI响应添加到对话历史
            self.conversation_history.append({"role": "model", "parts": [{"text": ai_response}]})
            
            return ai_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求错误: {e}")
            return None
        except KeyError as e:
            logger.error(f"解析响应错误: 缺少关键字段 {e}")
            return None
    
    def _encode_image(self, image_path):
        """将本地图片文件编码为base64格式"""
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def _get_image_from_url(self, image_url):
        """从URL获取图片并编码为base64格式"""
        import base64
        response = requests.get(image_url)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        return "对话历史已清空"
    
    def get_history(self):
        """获取当前对话历史"""
        return self.conversation_history
