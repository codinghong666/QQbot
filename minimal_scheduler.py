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
from send import check_all
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
        logging.info("Send task started")
        check_all()
        logging.info("Send task completed")
    except Exception as e:
        logging.error(f"Send task failed: {e}")

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

# MSqDLmgDizGlhYCMZJv9UtNlJMxZzfst