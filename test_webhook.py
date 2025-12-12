#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Webhook 服务器
用于接收并打印从 Telegram Monitor 发送的消息

运行方式：
    python test_webhook.py [端口号]

默认端口：8080
"""

import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class WebhookHandler(BaseHTTPRequestHandler):
    """处理 Webhook POST 请求"""
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # 解析 JSON
            data = json.loads(body.decode('utf-8'))
            
            # 打印收到的消息
            print("\n" + "=" * 60)
            print(f"收到消息 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 60)
            print(f"群组: {data.get('chat_name')} (ID: {data.get('chat_id')})")
            print(f"发送者: {data.get('sender_name')} (ID: {data.get('sender_id')})")
            print(f"消息ID: {data.get('message_id')}")
            print(f"时间: {data.get('date')}")
            print(f"媒体: {'是' if data.get('media') else '否'}")
            print(f"内容: {data.get('text', '(无文本)')}")
            print("-" * 60)
            print(f"完整 JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")
            print("=" * 60 + "\n")
            
            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析错误: {e}")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            
        except Exception as e:
            print(f"❌ 处理请求时出错: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """禁用默认的访问日志"""
        pass


def main():
    """启动测试 Webhook 服务器"""
    # 获取端口号
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"错误: 无效的端口号 '{sys.argv[1]}'")
            sys.exit(1)
    
    # 创建服务器
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    
    print("=" * 60)
    print("测试 Webhook 服务器")
    print("=" * 60)
    print(f"监听地址: http://0.0.0.0:{port}")
    print(f"本地访问: http://localhost:{port}")
    print(f"Webhook URL: http://localhost:{port}/webhook")
    print("-" * 60)
    print("按 Ctrl+C 停止服务器")
    print("=" * 60 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        server.shutdown()


if __name__ == '__main__':
    main()
