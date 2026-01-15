#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版MTR监控系统
- 改进并发控制
- 增强错误处理
- 优化资源管理
- 提升安全性
"""

import pymysql
import os
import time
import subprocess
import re
import logging
import signal
import sys
from dbutils.pooled_db import PooledDB
from datetime import datetime
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mtr_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('mtr_monitor')

# 配置常量
TIME_INTERVAL = 60
MAX_WORKERS = 110
#数据库链接信息
DB_CONFIG = {
    'host': 'ip',
    'port': 3306,
    'user': '',
    'password': '',
    'database': 'mtr',
    'charset': 'utf8'
}

class MTRMonitor:
    def __init__(self):
        self.pool = None
        self.local_isps = set()
        self.running = True
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """设置信号处理器"""
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """信号处理函数"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def create_connection_pool(self):
        """创建数据库连接池"""
        try:
            self.pool = PooledDB(
                creator=pymysql,
                maxconnections=20,  # 减少最大连接数
                mincached=2,
                maxcached=5,
                maxshared=3,
                blocking=True,
                maxusage=1000,  # 限制每个连接的最大使用次数
                setsession=[],
                ping=0,
                **DB_CONFIG
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    def get_local_public_ipv4s(self):
        """获取本机所有公网IPv4地址"""
        public_ips = []
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            for line in result.stdout.splitlines():
                if 'inet ' in line and 'scope global' in line:
                    match = re.search(r'inet\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/', line)
                    if match:
                        ip_str = match.group(1)
                        try:
                            ip_obj = ipaddress.IPv4Address(ip_str)
                            if ip_obj.is_global:
                                public_ips.append(str(ip_obj))
                        except Exception:
                            continue
        except subprocess.TimeoutExpired:
            logger.error("Timeout when getting local IPs")
        except Exception as e:
            logger.error(f"Failed to get local IPv4 addresses: {e}")
        return list(set(public_ips))
    
    def detect_local_isps_once(self):
        """启动时一次性检测本机支持的运营商集合"""
        ips = self.get_local_public_ipv4s()
        logger.info(f"Detected public IPv4s at startup: {ips}")
        isps = set()
        
        for ip in ips:
            try:
                # 使用更安全的subprocess调用方式
                res = subprocess.run(
                    ['nali-nt', ip], 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    check=False
                )
                
                if res.returncode != 0:
                    logger.warning(f"nali-nt failed for IP {ip}, return code: {res.returncode}")
                    continue
                
                out = res.stdout.lower()
                
                # 更精确的ISP识别
                if any(kw in out for kw in ["移动", "cmcc", "中国移动"]):
                    isps.add("移动")
                elif any(kw in out for kw in ["电信", "china telecom", "中国电信"]):
                    isps.add("电信")
                elif any(kw in out for kw in ["联通", "china unicom", "中国联通"]):
                    isps.add("联通")
                else:
                    logger.debug(f"Unknown ISP for IP {ip}: {res.stdout.strip()}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"ISP detection timeout for {ip}")
            except Exception as e:
                logger.error(f"Failed to query ISP for {ip}: {e}")
        
        if not isps:
            isps.add("未知")
        logger.info(f"Local ISPs (fixed for this run): {isps}")
        return isps
    
    def validate_ip(self, ip):
        """验证IP地址格式"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    def run_mtr(self, ip, date, region, company, custom, description):
        """执行 mtr 并写入文件"""
        if not self.validate_ip(ip):
            logger.error(f"Invalid IP address: {ip}")
            return
        
        try:
            # 构建安全的文件路径
            file_path = os.path.join(
                "/data/mtr",
                f"{date.year}年{date.month}月",
                f"{date.year}年{date.month}月{date.day}日",
                region,
                company,
                custom,
                f"{date.hour}-{description}.txt"
            )
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 使用更安全的命令构造方式
            cmd_parts = [
                'echo', '"------------------------------------------------------------------------------"',
                '>>', f'"{file_path}"',
                '&&', '/usr/local/sbin/mtr', '-r', '-i', '0.4', '-c', '59', '-n', ip,
                '>>', f'"{file_path}"'
            ]
            
            full_cmd = ' '.join(cmd_parts)
            result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                logger.error(f"MTR command failed for {ip}: {result.stderr}")
            else:
                logger.debug(f"MTR completed for {ip}, output saved to {file_path}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"MTR timeout for {ip}")
        except Exception as e:
            logger.error(f"Failed to run mtr for {ip}: {e}")
    
    def get_monitoring_targets(self):
        """从数据库获取监控目标"""
        if not self.pool:
            raise Exception("Connection pool not initialized")
        
        conn = None
        cursor = None
        try:
            conn = self.pool.connection()
            cursor = conn.cursor()
            
            query = """
            SELECT c.ip, c.region, c.room, c.custom, c.description, c.type_id, o.o_name, o.id AS operator_id
            FROM mtr_company c
            JOIN mtr_operator o ON c.operator_id = o.id
        """
            cursor.execute(query)
            records = cursor.fetchall()
            
            targets = []
            for record in records:
                ip, region, room, custom, description, type_id, op_name, operator_id = record
                
                ip = ip.strip() if ip else ""
                region = region.strip() if region else "未分类"
                room = room.strip() if room else "未分类"
                custom = custom.strip() if custom and custom.strip() else "未分类"
                description = description.strip() if description else "default"
                
                if not self.validate_ip(ip):
                    logger.warning(f"Skipping invalid IP: {ip}")
                    continue
                    
                # 注意：现在多返回一个 operator_id
                targets.append((ip, region, room, custom, description, type_id, op_name, operator_id))
            
            logger.info(f"Fetched {len(targets)} monitoring targets")
            return targets
            
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def filter_targets_by_isp(self, targets):
        """根据ISP类型过滤目标"""
        filtered_targets = []
        
        for item in targets:
            ip, region, room, custom, description, type_id, op_name, operator_id = item
            
            # 新增规则：operator_id == 4 的目标不受 ISP 限制
            if operator_id == 4:
                filtered_targets.append((ip, region, room, custom, description))
                continue  # 直接放行
            
            # 原有逻辑
            if type_id == 2:  # 全部执行
                filtered_targets.append((ip, region, room, custom, description))
            elif type_id == 1:  # 仅本地 ISP
                if op_name in self.local_isps:
                    filtered_targets.append((ip, region, room, custom, description))
                else:
                    logger.debug(f"Skipping {ip} - ISP {op_name} not in local ISPs {self.local_isps}")
            # 可选：如果存在其他 type_id（如 3、99），可选择忽略或报错
        
        logger.info(f"Filtered targets: {len(filtered_targets)} after ISP filtering")
        return filtered_targets
    
    def execute_monitoring_cycle(self):
        """执行一次完整的监控周期"""
        start_time = time.time()
        date = datetime.now()
        
        try:
            # 获取监控目标
            all_targets = self.get_monitoring_targets()
            filtered_targets = self.filter_targets_by_isp(all_targets)
            
            if not filtered_targets:
                logger.info("No targets to monitor this cycle")
                return
            
            target_count = len(filtered_targets)
            # 动态计算最大工作线程数
            max_workers = min(MAX_WORKERS, target_count) if target_count > 0 else 1
            logger.info(f"Starting monitoring cycle for {target_count} targets with {max_workers} workers")
            
            # 使用动态线程池
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for ip, region, room, custom, description in filtered_targets:
                    future = executor.submit(
                        self.run_mtr,
                        ip, date, region, room, custom, description
                    )
                    futures.append(future)
                
                # 等待完成（可选：加超时）
                for i, future in enumerate(as_completed(futures)):
                    try:
                        future.result(timeout=63)  # 60秒MTR + 3秒缓冲
                    except Exception as e:
                        logger.error(f"Task failed: {e}")
            
            elapsed = time.time() - start_time
            logger.info(f"Monitoring cycle completed in {elapsed:.2f}s with {max_workers} workers")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
    
    def run(self):
        """主运行循环"""
        logger.info("Starting MTR monitoring service...")
        
        try:
            self.create_connection_pool()
            self.local_isps = self.detect_local_isps_once()
            logger.info(f"Using fixed ISP set: {self.local_isps}")
            
            cycle_count = 0
            while self.running:
                cycle_start = time.time()
                
                try:
                    self.execute_monitoring_cycle()
                    cycle_count += 1
                    logger.info(f"Completed cycle #{cycle_count}")
                except Exception as e:
                    logger.error(f"Error in cycle #{cycle_count}: {e}")
                
                # 计算剩余等待时间
                elapsed = time.time() - cycle_start
                sleep_time = max(0, TIME_INTERVAL - elapsed)
                
                if self.running:
                    logger.debug(f"Waiting {sleep_time:.2f}s until next cycle")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        except Exception as e:
            logger.critical(f"Critical error in main loop: {e}")
        finally:
            logger.info("Service shutdown complete")

def main():
    monitor = MTRMonitor()
    monitor.run()

if __name__ == '__main__':
    main()