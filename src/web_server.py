import json
import requests
from requests.exceptions import RequestException
from flask import Flask, request, jsonify, render_template, appcontext_popped
import config
import vocechat_server
import logging 
import os
import auth

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 初始化Flask应用
app = Flask(__name__)
# 读取配置
config_info =config.read_config_info()



@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """处理VoceChat的Webhook请求"""
    # 处理验证请求
    if request.method == 'GET':
        logger.info(request.args)
        return '', 200
    # 处理消息请求
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.info(f"收到Webhook数据: {json.dumps(data, ensure_ascii=False)}")
            
            # 检查事件类型
            event = data.get('detail', {})
            event_type = event.get('type')
            
            if event_type == 'normal':
                # 处理新消息
                #response = vocechat_server.respose_chat(event.get('content', {}))
                response = vocechat_server.excute_event(event)
                if response:
                    return jsonify(response), 200
                else:
                    return "", 204  # 无响应
            else:
                logger.info(f"忽略事件类型: {event_type}")
                return "", 204  # 无响应
                
        except Exception as e:
            logger.error(f"处理Webhook时出错: {str(e)}", exc_info=True)
            return "服务器错误", 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({"status": "healthy"}), 200

@app.route('/config', methods=['GET'])
@auth.token_required
def get_config():
    """获取配置信息"""
    try:
        config_data = config.read_config_info()
        # 将SimpleNamespace对象转换为字典以便JSON序列化
        config_dict = {
            'port': config_data.port,
            'web_user': config_data.web_user,
            'web_password': config_data.web_password,
            'email': {
                'status': config_data.email.status,
                'receiver': config_data.email.receiver,
                'user': config_data.email.user,
                'password': config_data.email.password,
                'sender': config_data.email.sender,
                'message': {
                    'title': config_data.email.message.title,
                    'summary': config_data.email.message.summary,
                    'content': config_data.email.message.content
                }
            },
            'notifyX': {
                'status': config_data.notifyX.status,
                'key': config_data.notifyX.key,
                'message': {
                    'title': config_data.notifyX.message.title,
                    'description': config_data.notifyX.message.description,
                    'content': config_data.notifyX.message.content
                }
            },
            'deepseek': {
                'status': config_data.deepseek.status,
                'base_url': config_data.deepseek.base_url,
                'api_key': config_data.deepseek.api_key,
                'model': config_data.deepseek.model
            },
            'gemini': {
                'status': config_data.gemini.status,
                'base_url': config_data.gemini.base_url,
                'api_key': config_data.gemini.api_key,
                'model': config_data.gemini.model
            },
            'baidu': {
                'status': config_data.baidu.status,
                'base_url': config_data.baidu.base_url,
                'api_key': config_data.baidu.api_key,
                'model': config_data.baidu.model
            },
            'vocechat': {
                'bot_api_key': config_data.vocechat.bot_api_key,
                'bot_user_id': config_data.vocechat.bot_user_id,
                'host': config_data.vocechat.host,
                'target_gid': config_data.vocechat.target_gid
            },
            'schedulers': config_data.schedulers
        }
        return jsonify(config_dict), 200
    except Exception as e:
        logger.error(f"获取配置时出错: {str(e)}", exc_info=True)
        return jsonify({"error": "获取配置失败"}), 500

@app.route('/config', methods=['POST'])
@auth.token_required
def save_config():
    """保存配置信息"""
    try:
        data = request.get_json()
        # 保存配置逻辑
        # 这里我们使用ruamel.yaml库来更新配置文件
        from ruamel.yaml import YAML
        yaml = YAML()
        yaml.preserve_empty_lines = True
        yaml.width = 4096  # 防止自动换行
        
        # 读取现有配置文件
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config_data = yaml.load(file)
        
        # 更新配置数据
        config_data['port'] = data['port']
        config_data['web_user'] = data['web_user']
        config_data['web_password'] = data['web_password']
        config_data['email']['status'] = data['email']['status']
        config_data['email']['receiver'] = data['email']['receiver']
        config_data['email']['user'] = data['email']['user']
        config_data['email']['password'] = data['email']['password']
        config_data['email']['sender'] = data['email']['sender']
        config_data['email']['message']['title'] = data['email']['message']['title']
        config_data['email']['message']['summary'] = data['email']['message']['summary']
        config_data['email']['message']['content'] = data['email']['message']['content']
        config_data['notifyX']['status'] = data['notifyX']['status']
        config_data['notifyX']['key'] = data['notifyX']['key']
        config_data['notifyX']['message']['title'] = data['notifyX']['message']['title']
        config_data['notifyX']['message']['description'] = data['notifyX']['message']['description']
        config_data['notifyX']['message']['content'] = data['notifyX']['message']['content']
        config_data['deepseek']['status'] = data['deepseek']['status']
        config_data['deepseek']['base_url'] = data['deepseek']['base_url']
        config_data['deepseek']['api_key'] = data['deepseek']['api_key']
        config_data['deepseek']['model'] = data['deepseek']['model']
        config_data['gemini']['status'] = data['gemini']['status']
        config_data['gemini']['base_url'] = data['gemini']['base_url']
        config_data['gemini']['api_key'] = data['gemini']['api_key']
        config_data['gemini']['model'] = data['gemini']['model']
        config_data['baidu']['status'] = data['baidu']['status']
        config_data['baidu']['base_url'] = data['baidu']['base_url']
        config_data['baidu']['api_key'] = data['baidu']['api_key']
        config_data['baidu']['model'] = data['baidu']['model']
        config_data['vocechat']['bot_api_key'] = data['vocechat']['bot_api_key']
        config_data['vocechat']['bot_user_id'] = data['vocechat']['bot_user_id']
        config_data['vocechat']['host'] = data['vocechat']['host']
        config_data['vocechat']['target_gid'] = data['vocechat']['target_gid']
        config_data['schedulers'] = data['schedulers']
        
        # 写回配置文件
        with open('config.yaml', 'w', encoding='utf-8') as file:
            yaml.dump(config_data, file)
        
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error(f"保存配置时出错: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": "保存配置失败"}), 500

@app.route('/logins', methods=['POST'])
def login():
    """用户登录接口"""
    print("用户登录1")
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        print("用户登录2")
        # 从配置文件获取用户名和密码
        config_data = config.read_config_info()
        if not config_data:
            return jsonify({"error": "配置读取失败"}), 500
        print("用户登录3")    
        # 验证用户名和密码
        if username == config_data.web_user and password == config_data.web_password:
            # 生成token
            token = auth.generate_token(1)  # 使用固定的用户ID 1
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "用户名或密码错误"}), 401
    except Exception as e:
        logger.error(f"登录时出错: {str(e)}", exc_info=True)
        return jsonify({"error": "登录失败"}), 500

@app.route('/config-page', methods=['GET'])
def config_page():
    """配置页面路由"""
    return render_template('config.html')

def init():
     # 给vocechat返回的数据设置密码,后端接口有问题
    #vocechat_server.setSecret(config_info.vocechat.secret)
    # 从环境变量获取端口，默认为5000
    port = int(config_info.port)
    # 允许外部访问，debug模式仅用于开发
    app.run(host='0.0.0.0', port=port, debug=False)
    app.jinja_env.auto_reload = True  # 开启模板自动重载
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # 配置自动重载
   
