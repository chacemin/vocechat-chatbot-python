from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import config
import vocechat_server
import sendEmail
import sendNotifyX
from deepseek_server import DeepSeekChat
from gemini_server import GeminiChat
from baidu_server import BaiduChat
# 创建调度器
scheduler = BlockingScheduler()
config_info =config.read_config_info()
chat_deepseek = DeepSeekChat()
chat_gemini = GeminiChat()
chat_baidu = BaiduChat()
# 配置日志，方便查看任务执行情况
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def shutdown(signum, frame, scheduler):
    """处理终止信号，确保程序立即退出"""
    logger.info(f"接收到信号 {signum}，正在关闭调度器...")
    scheduler.shutdown(wait=False)  # 不等待当前任务完成，立即关闭
    logger.info("调度器已关闭，程序退出")

def job_to_execute(*args, **kwargs):
    """
    这里是你需要定时执行的方法
    请在此处补充具体实现逻辑
    """
    
    # 打印可变参数（如果有的话）
    if args:
        logger.info(f"可变参数: {args}")
    if kwargs:
        logger.info(f"关键字参数: {kwargs}")
        res = ""
        if config_info.baidu.status :
            vocechat_server.send_to_channel(msg_content= f"baidu正在思考问题：{kwargs['prompt']} \n\n请稍后.......")
            res = chat_baidu.send_message(user_message=kwargs['prompt']) 
            vocechat_server.send_to_channel(res)
            sendNotifyX.send(msg_content=f"{kwargs['prompt']},具体回答请打开VoceChat查看",msg_title=f"{kwargs['prompt'][:15]}...",msg_description="数据来自baidu")
            sendEmail.send(msg_content=res)
    # 以下为预留的空实现，你可以根据需要修改
    pass

def init():
    # 添加定时任务，使用crontab格式
    # 格式说明：分 时 日 月 周
    # 例如：'0 8 * * *' 表示每天早上8点执行
    #      '0 */2 * * *' 表示每2小时执行一次
    #      '30 12 * * 1' 表示每周一中午12:30执行
    for item in config_info.schedulers:
        if item['status'] == False:
           logger.info(f"不执行任务： {item}")
           continue
        cron_expression = item['cron']  # 每小时执行一次，可根据需要修改
        scheduler.add_job(
            job_to_execute,
            'cron',
            minute=cron_expression.split()[0],
            hour=cron_expression.split()[1],
            day=cron_expression.split()[2],
            month=cron_expression.split()[3],
            day_of_week=cron_expression.split()[4],
            name='带参数的定时任务',
            kwargs=item  # 传递关键字参数
        )
        logger.info(f"调度器已启动，定时任务将按照 {cron_expression} 执行")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器已停止")
