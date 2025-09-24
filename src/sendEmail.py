import smtplib
from email.mime.text import MIMEText
from email.header import Header
from types import SimpleNamespace
import config
import markdown
config_info = config.read_config_info()

def send_md(msg_content_md="", msg_title="",  msg_summary=""):
    send(msg_content=markdown.markdown(msg_content_md), msg_title=msg_title,  msg_summary=msg_summary)

def send(msg_content="", msg_title="",  msg_summary=""):
    if config_info.email.status==False:
        return
    if msg_content != "":
        config_info.email.message.content  = msg_content
    if msg_content != "":
        config_info.email.message.title  = msg_title
    if msg_content != "":
        config_info.email.message.summary  = msg_summary

    # 发送邮箱服务器
    smtpserver = 'smtp.163.com'
    # 编写HTML类型的邮件正文
    full_content = f"【摘要】{config_info.email.message.summary}\n\n{config_info.email.message.content}"
    msg = MIMEText(full_content, "html", 'utf-8')  # 显式指定编码
    msg['Subject'] = Header(config_info.email.message.title, 'utf-8')
    # 连接发送邮件
    try:
        # 163邮箱推荐使用465端口和SMTP_SSL
        with smtplib.SMTP_SSL(smtpserver, 465) as smtp:
            smtp.login(config_info.email.user, config_info.email.password)
            smtp.sendmail(config_info.email.user, config_info.email.receiver, msg.as_string())
            smtp.quit()
            print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败：{e}")
