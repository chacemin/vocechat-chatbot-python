import web_server
import cron_scheduler
import threading
import signal
import sys
import baidu_server
import sendEmail
import sendNotifyX

# 全局变量来控制线程
scheduler_thread = None
server_thread = None

def signal_handler(sig, frame):
    print('Received interrupt signal. Shutting down...')
    # 如果有线程在运行，可以在这里添加清理逻辑
    sys.exit(0)

def test():
    # 测试代码
    chat = baidu_server.BaiduChat()
    promte = f"我最爱的人是你"
    res =chat.send_message(promte )
    # vocechat_server.send_to_channel(text_content=res)
    #sendNotifyX.send(msg_content="昨夜鱼束风骤",msg_title="AI访问dfndjsfsdhfbdsjkfb.....",msg_description="其他信息")
    #vocechat_server.send_to_channel(text_content=f"## 参考文献 [1]: 百家号 - 2025-9-16 ([链接](https://baijiahao.baidu.com/s?id=1843373588517452610&wfr=spider&for=pc))")
    #sendEmail.send_md(msg_content_md=res,msg_title=promte)
    print(res)


def run():
   # 注册信号处理函数
   signal.signal(signal.SIGINT, signal_handler)
   signal.signal(signal.SIGTERM, signal_handler)
   
   # 创建线程来启动调度器
   scheduler_thread = threading.Thread(target=cron_scheduler.init)
   # 创建线程来启动服务器
   server_thread = threading.Thread(target=web_server.init)
   
   # 设置线程为守护线程，这样当主线程退出时它们也会退出
   scheduler_thread.daemon = True
   server_thread.daemon = True
   
   # 启动线程
   scheduler_thread.start()
   server_thread.start()
   
   # 主线程保持运行
   try:
       while True:
           # 检查线程是否还在运行
           if scheduler_thread.is_alive() or server_thread.is_alive():
               # 短暂休眠以避免过度占用CPU
               threading.Event().wait(1)
           else:
               # 如果所有线程都已结束，则退出
               break
   except KeyboardInterrupt:
       print("KeyboardInterrupt received")
       sys.exit(0)

if __name__ == '__main__':
   run()
   #test()
