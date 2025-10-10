import os
import sys
from openai import OpenAI
from dotenv import load_dotenv


def get_deepseek_client():
    """获取DeepSeek API客户端"""
    # 加载 .env 文件
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误：未找到DEEPSEEK_API_KEY环境变量")
        print("请在.env文件中设置您的DeepSeek API密钥")
        sys.exit(1)

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
