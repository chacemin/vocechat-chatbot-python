import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, current_app
import config
import jwt

# 从配置中获取密钥，如果没有则使用默认密钥
SECRET_KEY = getattr(config.read_config_info(), 'auth_secret_key', 'default_secret_key_for_dev')

def generate_token(user_id):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # token过期时间24小时
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查请求头中是否有token
        token = request.headers.get('Authorization')
        
        # 如果没有token，检查是否是不需要认证的路由
        if not token:
            # 对于/webhook和/health接口，不需要认证
            if request.endpoint in ['webhook', 'health_check']:
                return f(*args, **kwargs)
            return jsonify({'error': 'you must be login'}), 401
        
        # 解析token
        try:
            # 去除 "Bearer " 前缀
            if token.startswith('Bearer '):
                token = token[7:]
            
            user_id = verify_token(token)
            if not user_id:
                return jsonify({'error': 'Token无效'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Token验证失败'}), 401
            
        # 将user_id添加到请求上下文中
        request.current_user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function
