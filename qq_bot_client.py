#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人客户端
用于获取群消息历史并解析文本内容
"""

import requests
import json
from typing import List, Dict, Any, Optional


class QQBotClient:
    """QQ机器人客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:3000", token: str = "1145141919810"):
        """
        初始化客户端
        
        Args:
            base_url: API基础URL
            token: 认证令牌
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
            'User-Agent': 'QQBotClient/1.0'
        }
    
    def get_group_msg_history(self, group_id: str, message_seq: str = "", 
                            count: int = 10, reverse_order: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取群消息历史
        
        Args:
            group_id: 群组ID
            message_seq: 消息序列号（可选）
            count: 获取消息数量
            reverse_order: 是否逆序获取
            
        Returns:
            API响应数据，如果请求失败返回None
        """
        url = f"{self.base_url}/get_group_msg_history"
        
        payload = {
            "group_id": group_id,
            "message_seq": message_seq,
            "count": count,
            "reverseOrder": reverse_order
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def parse_text_messages(self, api_response: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        解析消息，只提取文本内容和发送者昵称
        
        Args:
            api_response: API响应数据
            
        Returns:
            包含文本内容和发送者昵称的列表
        """
        if not api_response or api_response.get('status') != 'ok':
            return []
        
        messages = api_response.get('data', {}).get('messages', [])
        text_messages = []
        
        for message in messages:
            # 提取发送者昵称
            sender_info = message.get('sender', {})
            nickname = sender_info.get('nickname', '未知用户')
            
            # 提取文本内容
            message_list = message.get('message', [])
            text_parts = []
            
            for msg_part in message_list:
                if msg_part.get('type') == 'text':
                    text_content = msg_part.get('data', {}).get('text', '')
                    if text_content.strip():
                        text_parts.append(text_content.strip())
            
            # 如果有文本内容，添加到结果中
            if text_parts:
                text_content = '\n'.join(text_parts)
                text_messages.append({
                    'nickname': nickname,
                    'text': text_content
                })
        
        return text_messages
    
    def get_and_parse_messages(self, group_id: str, count: int = 10) -> List[Dict[str, str]]:
        """
        获取并解析群消息，返回文本内容
        
        Args:
            group_id: 群组ID
            count: 获取消息数量
            
        Returns:
            解析后的文本消息列表
        """
        # 获取消息历史
        response = self.get_group_msg_history(group_id, count=count)
        
        if not response:
            print("获取消息失败")
            return []
        
        # 解析消息
        return self.parse_text_messages(response)
    
    def print_text_messages(self, group_id: str, count: int = 10):
        """
        获取并打印群消息的文本内容
        
        Args:
            group_id: 群组ID
            count: 获取消息数量
        """
        text_messages = self.get_and_parse_messages(group_id, count)
        
        if not text_messages:
            print("没有找到文本消息")
            return
        
        print(f"=== 群 {group_id} 的文本消息 (共 {len(text_messages)} 条) ===")
        print()
        
        for i, msg in enumerate(text_messages, 1):
            print(f"【{i}】{msg['nickname']}:")
            print(f"    {msg['text']}")
            print()


def main():
    """主函数"""
    # 创建客户端
    client = QQBotClient()
    
    # 群组ID
    group_id = "914404708"
    
    # 获取并打印消息
    print("正在获取群消息...")
    client.print_text_messages(group_id, count=10)


if __name__ == "__main__":
    main()
