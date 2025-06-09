#!/usr/bin/env python3
"""
驗證API調用是否為真實調用
"""

import os
import asyncio
import google.generativeai as genai
import anthropic

async def test_real_api_calls():
    print("🔍 驗證API調用是否為真實調用...")
    
    # 測試Gemini API
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            test_prompt = "請回答：2+2等於多少？只回答數字。"
            response = model.generate_content(test_prompt)
            
            print(f"✅ Gemini API真實調用成功")
            print(f"   測試問題: {test_prompt}")
            print(f"   API回答: {response.text.strip()}")
            
        except Exception as e:
            print(f"❌ Gemini API調用失敗: {e}")
    
    # 測試Claude API
    claude_api_key = os.environ.get('CLAUDE_API_KEY')
    if claude_api_key:
        try:
            client = anthropic.Anthropic(api_key=claude_api_key)
            
            test_prompt = "請回答：3+3等於多少？只回答數字。"
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=10,
                temperature=0,
                messages=[{"role": "user", "content": test_prompt}]
            )
            
            print(f"✅ Claude API真實調用成功")
            print(f"   測試問題: {test_prompt}")
            print(f"   API回答: {message.content[0].text.strip()}")
            
        except Exception as e:
            print(f"❌ Claude API調用失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_real_api_calls())

