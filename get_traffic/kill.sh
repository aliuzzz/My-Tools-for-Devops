#!/bin/bash
ps -eo pid,cmd | grep xg | awk '{print $1}' | xargs kill -9
ps -eo pid,cmd | grep dakota | awk '{print $1}' | xargs kill -9
pkill -9 wget
sleep 2

# 清理 /root/xg_download/ 目录下所有的 wget-log 文件
rm -f /root/xg_download/wget-log*

