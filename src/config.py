from ruamel.yaml import YAML
import os
from types import SimpleNamespace
import logging 
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def read_config_info(yaml_file_path="config.yaml"):
    """
    读取YAML文件中的邮件配置信息和消息内容，返回一个可通过点符号访问的对象
    
    参数:
        yaml_file_path: YAML文件的路径，默认值为"config.yaml"
        
    返回:
        包含邮件信息和消息内容的SimpleNamespace对象，如果出错则返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(yaml_file_path):
            logger.error(f"错误: 文件 '{yaml_file_path}' 不存在")
            return None
            
        yaml = YAML(typ='safe')  # 创建安全的YAML解析器
        # 打开并读取YAML文件
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            # 解析YAML内容
            config = yaml.load(file)
            
            # 将字典转换为可通过点符号访问的对象
            # 使用递归转换，确保嵌套结构也能通过点符号访问
            def dict_to_obj(d):
                if isinstance(d, dict):
                    return SimpleNamespace(**{k: dict_to_obj(v) for k, v in d.items()})
                return d
            
            return dict_to_obj(config)

    except Exception as e:
        logger.error(f"读取文件时发生错误: {e}")
    return None