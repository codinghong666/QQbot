#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal Resource QQ Bot Scheduler
占用资源最少的定时任务调度器
需要安装: pip install apscheduler
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from work import work
from send import send
from loadconfig import load_config
from datebase import iter_data
import logging


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('minimal_scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_work_task():
    """执行work任务"""
    try:
        logging.info("Work task started")
        work()
        logging.info("Work task completed")
    except Exception as e:
        logging.error(f"Work task failed: {e}")

def run_send_task():
    """执行send任务"""
    try:
        config = load_config()
        if config is None:
            logging.error("Config not loaded, skipping send")
            return
        
        logging.info("Send task started")
        
        # 从数据库获取数据
        data = iter_data()
        
        if not data:
            message_content = "datebase is empty"
            logging.info("datebase is empty")
        else:
            # 获取当前日期和前一天日期
            from datetime import datetime, timedelta
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            
            # 构建消息内容
            message_content = "今日时间信息汇总：\n\n"
            filtered_messages = []
            
            for record in data:
                message_time_str = record[4]  # 时间字段
                if message_time_str:
                    try:
                        # 解析时间字符串 (格式: MM:DD:HH:MM)
                        time_parts = message_time_str.split(':')
                        if len(time_parts) >= 2:
                            month = int(time_parts[0])
                            day = int(time_parts[1])
                            
                            # 构造日期 (假设是当前年份)
                            current_year = datetime.now().year
                            message_date = datetime(current_year, month, day).date()
                            
                            # 检查是否是昨天或今天
                            if message_date >= today and message_date <= tomorrow:
                                filtered_messages.append(record)
                    except (ValueError, IndexError) as e:
                        logging.warning(f"Invalid time format: {message_time_str}")
                        continue
            
            if filtered_messages:
                for i, record in enumerate(filtered_messages, 1):  # 只发送最近5条记录
                    message_content += f"{i}. 时间: {record[4]}\n   消息: {record[3]}...\n\n"
            else:
                message_content = "今日暂无符合条件的时间信息数据"
                logging.info("No messages found for today or yesterday")
        
        # 发送消息
        result = send(message_content, config)
        if result:
            logging.info("Send task completed")
        else:
            logging.error("Send task failed")
            
    except Exception as e:
        logging.error(f"Send task error: {e}")

def main():
    """主函数"""
    config = load_config()
    if config is None:
        logging.error("Config error, cannot start")
        return
    
    work_time = config.get('work_time', '02:00')
    send_time = config.get('send_time', '08:50')
    
    # 解析时间
    work_hour, work_minute = map(int, work_time.split(':'))
    send_hour, send_minute = map(int, send_time.split(':'))
    
    # 创建调度器
    scheduler = BlockingScheduler()
    
    # 添加任务
    scheduler.add_job(
        run_work_task,
        CronTrigger(hour=work_hour, minute=work_minute),
        id='work_task',
        name='Work Task'
    )
    
    scheduler.add_job(
        run_send_task,
        CronTrigger(hour=send_hour, minute=send_minute),
        id='send_task',
        name='Send Task'
    )
    
    logging.info(f"Minimal Scheduler started - Work: {work_time}, Send: {send_time}")
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped")
    except Exception as e:
        logging.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()
