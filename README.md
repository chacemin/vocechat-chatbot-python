# VoceChat AI Chatbot 项目说明

这是一个基于 VoceChat 平台的 AI 聊天机器人程序，具备定时任务功能，可以自动从不同 AI 模型获取信息并发送到 VoceChat 频道中。程序支持多种 AI 模型（如 DeepSeek、Gemini、百度千帆）和通知方式（邮件、NotifyX）。

## 功能特性

- **定时任务执行**：可以按照设定的时间周期自动执行 AI 消息获取任务
- **多 AI 模型支持**：支持 DeepSeek、Gemini、百度千帆等 AI 模型
- **消息推送**：支持通过邮件和 NotifyX 进行通知，这个功能是因为vocechat在国内无法使用通知消息，用邮件或者微信来提醒
- **Web 管理界面**：提供 Web 界面用于配置和管理程序
- **VoceChat 集成**：可以直接将 AI 消息发送到 VoceChat 频道

## 危险提示
- **这个很重要**：这个服务由于只和vocechat集成，所以需要在内网部署，能与vocechat通讯即可，
，不能暴露到公网，否则密钥有被盗风险


## 快速开始

### 环境要求
- Python 3.7+
- uv 工具
- Docker (可选)

### 安装和运行

1. 克隆项目代码
```bash
git clone <项目地址>
cd vocechat-chatbot
```

2. 安装依赖
```bash
uv sync
```

3. 配置文件
编辑 `config.yaml` 文件，配置相应的 API 密钥和设置

4. 运行程序
```bash
uv run src/main.py
```

### Docker 运行

```bash
# 构建 Docker 镜像
docker build -t vocechat-chatbot .

# 运行容器
docker run --name vocechat-chatbot -p 4800:5000 -v ~/config.yaml:/app/config.yaml -v /etc/localtime:/etc/localtime vocechat-chatbot:latest
```

## 配置说明

配置文件 `config.yaml` 包含以下主要配置项：
- `port`: Web 服务端口
- `web_user` 和 `web_password`: Web 管理页面登录凭据
- 各种 AI 模型的 API 配置（DeepSeek、Gemini、百度千帆）
- 邮件和通知配置
- VoceChat 配置信息
- 定时任务配置（schedulers）

## 使用方法

1. 访问 Web 管理界面：http://localhost:5000/config-page
2. 使用默认用户名 `chace` 和密码 `123456` 登录
3. 配置各个 AI 模型和通知方式的 API 密钥
4. 设置定时任务执行时间
5. 保存配置并启动程序

## 项目结构

- `src/main.py` - 程序入口点
- `src/web_server.py` - Web 服务和管理界面
- `src/cron_scheduler.py` - 定时任务调度器
- `src/baidu_server.py` - 百度千帆 AI 服务
- `src/deepseek_server.py` - DeepSeek AI 服务
- `src/gemini_server.py` - Gemini AI 服务
- `src/vocechat_server.py` - VoceChat 集成服务
- `src/sendEmail.py` - 邮件发送服务
- `src/sendNotifyX.py` - NotifyX 通知服务
- `config.yaml` - 配置文件

## 打包程序

使用 PyInstaller 打包程序：
```bash
uv run pyinstaller -F --name vocechat-chatbot src/main.py
```

## 注意事项

- 默认登录用户名：chace
- 默认登录密码：123456
- 需要配置相应的 API 密钥才能使用 AI 模型
- 配置文件中的定时任务默认是关闭的，需要手动开启
