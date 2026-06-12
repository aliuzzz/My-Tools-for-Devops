"""
CDN推送接口连通性测试脚本

用法：
    python test_push_api.py                    # 测试第一个客户的推送接口
    python test_push_api.py --customer "淮北移动"  # 测试指定客户
    python test_push_api.py -c config.yaml     # 指定配置文件

功能：构造1条mock采样数据，快速验证推送接口连通性和认证是否正常
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests
import yaml


def load_config(config_path, customer_name=None):
    """加载YAML配置（简化版）"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)

    if 'customers' not in raw:
        return [raw]

    defaults = raw.get('defaults', {})
    customers = raw.get('customers', [])
    result = []
    for cust in customers:
        merged = dict(defaults)
        merged.update(cust)
        result.append(merged)

    if customer_name:
        matched = [c for c in result if c.get('name') == customer_name]
        if not matched:
            available = [c.get('name', 'unnamed') for c in result]
            raise ValueError(f"未找到客户 '{customer_name}'，可用客户: {available}")
        return matched

    return result


def test_push(cfg):
    """测试推送接口"""
    push_api = cfg.get('push_api', {})
    url = push_api.get('url')
    customer_id = push_api.get('customer_id')
    customer_name = push_api.get('customer_name')
    extra_headers = push_api.get('headers', {})

    if not url:
        print(f"❌ [{cfg.get('name', 'unknown')}] push_api.url 未配置")
        return False

    stat_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    batch_no = f"cdn-test-{stat_date.replace('-', '')}-{datetime.now().strftime('%H%M%S')}"

    # 构造1条mock采样数据
    payload = {
        "customerId": customer_id,
        "customerName": customer_name,
        "statDate": stat_date,
        "sourceType": "api",
        "batchNo": batch_no,
        "remark": f"接口连通性测试，域名: {','.join(cfg.get('target_domains', []))}",
        "samples": [
            {
                "sampleTime": f"{stat_date} 00:00:00",
                "trafficValue": 123.456,
                "trafficUnit": "Mbps"
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        **extra_headers
    }

    print(f"\n{'='*50}")
    print(f"[客户] {cfg.get('name', 'unknown')}")
    print(f"[接口] {url}")
    print(f"[认证头] {json.dumps(extra_headers, ensure_ascii=False) if extra_headers else '(无)'}")
    print(f"[请求体] {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print('='*50)

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"\n[响应] HTTP {resp.status_code}")
        try:
            body = resp.json()
            print(f"[响应体] {json.dumps(body, ensure_ascii=False, indent=2)}")
        except:
            print(f"[响应体] {resp.text[:500]}")

        if resp.status_code == 200:
            print("\n✅ 接口连通，HTTP 200")
            return True
        elif resp.status_code == 401:
            print("\n⚠️ HTTP 401 — 认证失败，请检查 push_api.headers 配置")
            return False
        else:
            print(f"\n⚠️ HTTP {resp.status_code} — 请检查接口状态")
            return False

    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("   请检查：1) 接口服务是否启动  2) IP/端口是否正确")
        return False
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='CDN推送接口连通性测试')
    parser.add_argument('-c', '--config', default='config.yaml', help='YAML配置文件路径 (默认: config.yaml)')
    parser.add_argument('--customer', help='指定客户名称（如"淮北移动"）')
    args = parser.parse_args()

    try:
        customers = load_config(args.config, args.customer)
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)

    results = []
    for cust in customers:
        ok = test_push(cust)
        results.append((cust.get('name', 'unknown'), ok))

    print(f"\n{'='*50}")
    print("测试汇总:")
    for name, ok in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"  {status} — {name}")

    if not all(ok for _, ok in results):
        sys.exit(1)


if __name__ == '__main__':
    main()
