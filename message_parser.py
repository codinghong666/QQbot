#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQ机器人消息解析器
用于解析QQ机器人API返回的消息数据，只提取文本内容，忽略文件、图片等其他信息
"""

import json
from typing import List, Dict, Any


class QQMessageParser:
    """QQ消息解析器类"""
    
    def __init__(self):
        pass
    
    def parse_messages(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        解析QQ机器人API返回的消息数据
        
        Args:
            api_response: API返回的JSON数据
            
        Returns:
            解析后的消息列表，只包含文本内容
        """
        if not api_response or api_response.get('status') != 'ok':
            return []
        
        messages = api_response.get('data', {}).get('messages', [])
        parsed_messages = []
        
        for message in messages:
            parsed_message = self._parse_single_message(message)
            if parsed_message:  # 只添加包含文本内容的消息
                parsed_messages.append(parsed_message)
        
        return parsed_messages
    
    def _parse_single_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析单条消息
        
        Args:
            message: 单条消息数据
            
        Returns:
            解析后的消息数据，如果没有文本内容则返回None
        """
        # 提取基本信息
        parsed = {
            'message_id': message.get('message_id'),
            'time': message.get('time'),
            'message_type': message.get('message_type'),
            'group_id': message.get('group_id'),
            'group_name': message.get('group_name'),
            'sender': {
                'user_id': message.get('sender', {}).get('user_id'),
                'nickname': message.get('sender', {}).get('nickname'),
                'card': message.get('sender', {}).get('card'),
                'role': message.get('sender', {}).get('role')
            },
            'text_content': ''
        }
        
        # 解析消息内容，只提取文本
        message_list = message.get('message', [])
        text_parts = []
        
        for msg_part in message_list:
            if msg_part.get('type') == 'text':
                text_content = msg_part.get('data', {}).get('text', '')
                if text_content.strip():
                    text_parts.append(text_content.strip())
        
        # 如果没有文本内容，返回None
        if not text_parts:
            return None
        
        # 合并所有文本内容
        parsed['text_content'] = '\n'.join(text_parts)
        
        return parsed
    
    def extract_text_only(self, api_response: Dict[str, Any]) -> List[str]:
        """
        只提取文本内容，返回纯文本列表
        
        Args:
            api_response: API返回的JSON数据
            
        Returns:
            文本内容列表
        """
        parsed_messages = self.parse_messages(api_response)
        return [msg['text_content'] for msg in parsed_messages]
    
    def print_messages(self, api_response: Dict[str, Any]):
        """
        打印解析后的消息（用于调试）
        
        Args:
            api_response: API返回的JSON数据
        """
        parsed_messages = self.parse_messages(api_response)
        
        print(f"共解析到 {len(parsed_messages)} 条文本消息：")
        print("=" * 50)
        
        for i, msg in enumerate(parsed_messages, 1):
            print(f"消息 {i}:")
            print(f"  发送者: {msg['sender']['nickname']} ({msg['sender']['card']})")
            print(f"  时间: {msg['time']}")
            print(f"  群组: {msg['group_name']}")
            print(f"  内容: {msg['text_content']}")
            print("-" * 30)


def main():
    """主函数，演示如何使用解析器"""
    
    # 示例API响应数据（您提供的实际数据）
    sample_response = {
        "status": "ok",
        "retcode": 0,
        "data": {
            "messages": [
                {
                    "self_id": 2372124330,
                    "user_id": 1227514267,
                    "time": 1758166949,
                    "message_id": 980931767,
                    "message_seq": 980931767,
                    "real_id": 980931767,
                    "real_seq": "806",
                    "message_type": "group",
                    "sender": {
                        "user_id": 1227514267,
                        "nickname": "匿名",
                        "card": "22 物理 张跃扬",
                        "role": "admin"
                    },
                    "raw_message": "[CQ:file,file=泰山学堂2025年度奖（助）学金评审工作小组成员公示.pdf,file_id=/bb2c419c-1a40-41f2-9e97-6ec5e45fae10,file_size=297714]",
                    "font": 14,
                    "sub_type": "normal",
                    "message": [
                        {
                            "type": "file",
                            "data": {
                                "file": "泰山学堂2025年度奖（助）学金评审工作小组成员公示.pdf",
                                "file_id": "/bb2c419c-1a40-41f2-9e97-6ec5e45fae10",
                                "file_size": "297714"
                            }
                        }
                    ],
                    "message_format": "array",
                    "post_type": "message",
                    "group_id": 914404708,
                    "group_name": "泰山学堂2024级通知群"
                },
                {
                    "self_id": 2372124330,
                    "user_id": 2835229528,
                    "time": 1758194141,
                    "message_id": 288383095,
                    "message_seq": 288383095,
                    "real_id": 288383095,
                    "real_seq": "807",
                    "message_type": "group",
                    "sender": {
                        "user_id": 2835229528,
                        "nickname": "唐圜",
                        "card": "23化学隽召鹏",
                        "role": "member"
                    },
                    "raw_message": "各位同学好，《关于发展刘睿宇等16位同志为入党积极分子的公示》已在中心校区数学楼三楼公告栏公布，请及时查阅。祝好！@全体成员",
                    "font": 14,
                    "sub_type": "normal",
                    "message": [
                        {
                            "type": "text",
                            "data": {
                                "text": "各位同学好，《关于发展刘睿宇等16位同志为入党积极分子的公示》已在中心校区数学楼三楼公告栏公布，请及时查阅。祝好！@全体成员 "
                            }
                        }
                    ],
                    "message_format": "array",
                    "post_type": "message",
                    "group_id": 914404708,
                    "group_name": "泰山学堂2024级通知群"
                }
            ]
        },
        "message": "",
        "wording": "",
        "echo": "zin3nx3zka",
        "stream": "normal-action"
    }
    
    # 创建解析器实例
    parser = QQMessageParser()
    
    # 解析消息
    print("=== 解析消息 ===")
    parsed_messages = parser.parse_messages(sample_response)
    
    # 打印解析结果
    parser.print_messages(sample_response)
    
    # 只提取文本内容
    print("\n=== 只提取文本内容 ===")
    text_only = parser.extract_text_only(sample_response)
    for i, text in enumerate(text_only, 1):
        print(f"文本 {i}: {text}")


if __name__ == "__main__":
    main()
