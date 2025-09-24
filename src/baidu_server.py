from openai import OpenAI
import logging 
import config
import json
from typing import Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取配置
config_info = config.read_config_info()
client = None
class BaiduChat:
    def __init__(self):
        global client
        client = OpenAI(api_key=config_info.baidu.api_key, # 千帆AppBuilder平台的ApiKey      
        base_url=config_info.baidu.base_url) # 智能搜索生成V2版本接口
        self.conversation_history = []  # 用于存储对话历史，维护上下文
        if config_info.baidu.status == False:
           logger.info(f"系统配置为不启用baidu服务")
    
    def send_message(self, user_message):
        if config_info.baidu.status == False:
           return "baiduAI未启用，不能回答你的问题哦"
        """发送消息并获取响应，自动维护对话上下文"""
        logger.info(f"baidu收到用户信息 {user_message}")
        if user_message == 'clear':
            logger.info(f"系统: {self.clear_history()}")
            return "对话历史已清除"
        
        # 将用户消息添加到对话历史
        self.conversation_history.append({"role": "user", "content": user_message})
        if len(self.conversation_history) > 20 : # 限制历史记录长度
           self.conversation_history.pop(0)

        
        # 准备请求数据
        payload = {
            "messages": [{
                "role": "user",
                "content": user_message
            }]
        }
        
        # 如果有历史记录，添加到请求中
        if len(self.conversation_history) > 1:
            # 构建历史记录内容
            history_contents = []
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    history_contents.append({"role": "user", "content": msg["content"]})
                else:  # assistant
                    history_contents.append({"role": "user", "content": msg["content"]})
            
            # 重置内容，只保留最新的用户消息和历史
            payload["messages"] = history_contents
        
        try:
            # 发送请求
            response = client.chat.completions.create(
                model="deepseek-r1",
                messages=[
                    {"role": "user", "content": user_message}
                ],
                stream=False
            )

            # logger.info(f"百度回复：\n {response}")
            
            # 解析响应
            result = generate_markdown_with_citations(response)
            
            # 提取AI响应内容
            ai_response = result
            
            # 将AI响应添加到对话历史
            self.conversation_history.append({"role": "model", "content":  ai_response})
            
            return ai_response
            
        except Exception as e:
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


def generate_markdown_with_citations(json_data: Dict) -> str:
    """
    将解析后的JSON数据转换为带有引用链接的Markdown文档
    
    Args:
        json_data: 包含choices和references的字典
        
    Returns:
        格式化后的Markdown字符串
    """
    
    # 提取主要内容
    content = ""
    try:
        content = json_data.choices[0].message.content
    except AttributeError:
        # 捕获属性不存在的异常，设置默认值
        content = ""
    # 提取参考文献
    references = []
    # 检查 json_data 是否有 'references' 属性
    if hasattr(json_data, 'references'):
        references = json_data.references
    
    
    # 构建参考文献字典，便于替换
    ref_dict = {}
    for ref in references:
        ref_id = ref.get("id",{})
        ref_url = ref.get("url",{})
        ref_title = ref.get("title",{})
        ref_date = ref.get("date",{})
        
        # 创建引用标记，例如 [^1]: 标题 - 日期 {url}
        citation = f"[{ref_id}].{ref_title} - {ref_date} ([链接]({ref_url}))"
        ref_dict[ref_id] = citation
    
    # 在内容末尾添加参考文献部分
    full_content = content.strip()
    full_content += "\n\n## 参考来源\n\n"
    
    # 按ID顺序添加所有引用
    for ref_id in sorted(ref_dict.keys()):
        full_content += ref_dict[ref_id] + "\n\n"
    
    return full_content
