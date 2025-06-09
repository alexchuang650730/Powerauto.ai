#!/bin/bash
# 清理腳本
sed -i 's/sk-ant-api03-[A-Za-z0-9_-]\{95\}/your_claude_api_key_here/g' "$1"
sed -i 's/github_pat_[A-Za-z0-9_-]\{82\}/your_github_token_here/g' "$1"
sed -i 's/AIzaSy[A-Za-z0-9_-]\{33\}/your_gemini_api_key_here/g' "$1"
