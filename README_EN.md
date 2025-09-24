# VoceChat AI Chatbot Project Documentation

This is an AI chatbot program based on the VoceChat platform, featuring scheduled task functionality that can automatically fetch information from different AI models and send it to VoceChat channels. The program supports multiple AI models (such as DeepSeek, Gemini, Baidu Qianfan) and notification methods (email, NotifyX).

## Features

- **Scheduled Task Execution**: Can automatically execute AI message fetching tasks according to set time cycles
- **Multi AI Model Support**: Supports DeepSeek, Gemini, Baidu Qianfan and other AI models
- **Message Push**: Supports notification via email and NotifyX. This feature exists because VoceChat cannot be used for notifications in China, so email or WeChat is used for reminders
- **Web Management Interface**: Provides a web interface for configuring and managing the program
- **VoceChat Integration**: Can directly send AI messages to VoceChat channels

## Warning

- **This is very important**: This service needs to be deployed in a private network to communicate with VoceChat only, and must not be exposed to the public internet, otherwise the keys will be at risk of being stolen.

## Quick Start

### Requirements

- Python 3.7+
- uv tool
- Docker (optional)

### Installation and Running

1. Clone the project code
```bash
git clone <project URL>
cd vocechat-chatbot
```

2. Install dependencies
```bash
uv sync
```

3. Configuration file
Edit the `config.yaml` file to configure the corresponding API keys and settings

4. Run the program
```bash
uv run src/main.py
```

### Docker Running

```bash
# Build Docker image
docker build -t vocechat-chatbot .

# Run container
docker run --name vocechat-chatbot -p 4800:5000 -v /vol1/1000/docker/vocechat-ch
atbot/config.yaml:/app/config.yaml -v /etc/localtime:/etc/localtime vocechat-chatbot:latest
```

## Configuration Description

The configuration file `config.yaml` contains the following main configuration items:
- `port`: Web service port
- `web_user` and `web_password`: Web management page login credentials
- Various AI model API configurations (DeepSeek, Gemini, Baidu Qianfan)
- Email and notification configurations
- VoceChat configuration information
- Scheduled task configuration (schedulers)

## Usage Instructions

1. Access the Web management interface: http://localhost:5000/config-page
2. Log in using the default username `chace` and password `123456`
3. Configure API keys for various AI models and notification methods
4. Set the scheduled task execution time
5. Save the configuration and start the program

## Project Structure

- `src/main.py` - Program entry point
- `src/web_server.py` - Web service and management interface
- `src/cron_scheduler.py` - Scheduled task scheduler
- `src/baidu_server.py` - Baidu Qianfan AI service
- `src/deepseek_server.py` - DeepSeek AI service
- `src/gemini_server.py` - Gemini AI service
- `src/vocechat_server.py` - VoceChat integration service
- `src/sendEmail.py` - Email sending service
- `src/sendNotifyX.py` - NotifyX notification service
- `config.yaml` - Configuration file

## Packaging the Program

Use PyInstaller to package the program:
```bash
uv run pyinstaller -F --name vocechat-chatbot src/main.py
```

## Notes

- Default login username: chace
- Default login password: 123456
- API keys need to be configured to use AI models
- Scheduled tasks in the configuration file are disabled by default and need to be enabled manually