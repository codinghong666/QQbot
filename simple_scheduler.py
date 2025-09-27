#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple QQ Bot Scheduler
简单的定时任务调度器，使用线程和sleep实现
"""

import time
import threading
from datetime import datetime, time as dt_time
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
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

class SimpleScheduler:
    """简单定时任务调度器"""
    
    def __init__(self):
        self.running = False
        self.config = None
        self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            self.config = load_config()
            if self.config is None:
                logging.error("Failed to load configuration")
                return False
            logging.info("Configuration loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return False
    
    def run_work_task(self):
        """执行work任务"""
        try:
            logging.info("Work task started")
            work()
            logging.info("Work task completed")
        except Exception as e:
            logging.error(f"Work task failed: {e}")
    
    def run_send_task(self):
        """执行send任务"""
        try:
            if self.config is None:
                logging.error("Config not loaded, skipping send")
                return
            
            logging.info("Send task started")
            
            # 从数据库获取数据
            data = iter_data()
            
            if not data:
                message_content = "今日暂无时间信息数据"
                logging.info("No data found")
            else:
                # 构建消息内容
                message_content = "今日时间信息汇总：\n\n"
                for i, record in enumerate(data[-5:], 1):  # 只发送最近5条记录
                    message_content += f"{i}. 时间: {record[4]}\n   消息: {record[3][:50]}...\n\n"
            
            # 发送消息
            result = send(message_content, self.config)
            if result:
                logging.info("Send task completed")
            else:
                logging.error("Send task failed")
                
        except Exception as e:
            logging.error(f"Send task error: {e}")
    
    def check_and_run_tasks(self):
        """检查并执行任务"""
        if self.config is None:
            return
            
        now = datetime.now()
        current_time = now.time()
        
        # 从配置中获取work任务时间
        work_time_str = self.config.get('work_time', '02:00')
        work_hour, work_minute = map(int, work_time_str.split(':'))
        work_time = dt_time(work_hour, work_minute)
        
        if current_time.hour == work_time.hour and current_time.minute == work_time.minute:
            self.run_work_task()
            time.sleep(60)  # 避免重复执行
        
        # 从配置中获取send任务时间
        send_time_str = self.config.get('send_time', '08:50')
        send_hour, send_minute = map(int, send_time_str.split(':'))
        send_time = dt_time(send_hour, send_minute)
        
        if current_time.hour == send_time.hour and current_time.minute == send_time.minute:
            self.run_send_task()
            time.sleep(60)  # 避免重复执行
    
    def start(self):
        """启动调度器"""
        if not self.load_config():
            logging.error("Config error, cannot start")
            return
        
        self.running = True
        work_time = self.config.get('work_time', '02:00')
        send_time = self.config.get('send_time', '08:50')
        logging.info(f"Scheduler started - Work: {work_time}, Send: {send_time}")
        
        try:
            while self.running:
                self.check_and_run_tasks()
                time.sleep(30)  # 每30秒检查一次
        except KeyboardInterrupt:
            logging.info("Scheduler stopped")
        except Exception as e:
            logging.error(f"Scheduler error: {e}")
        finally:
            self.running = False
            logging.info("Scheduler stopped")
    
    def stop(self):
        """停止调度器"""
        self.running = False

def main():
    """主函数"""
    print("QQ Bot Scheduler")
    print("Press Ctrl+C to stop")
    print()
    
    scheduler = SimpleScheduler()
    scheduler.start()

if __name__ == "__main__":
    main()
