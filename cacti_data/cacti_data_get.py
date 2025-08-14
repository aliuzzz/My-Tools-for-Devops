###############
# cacti_data_get.py
# 用于获取cacti数据,通过接口，获取数据写入csv文件
###############

import base64
import csv
import json
import os
import time
from typing import Dict, Any
from datetime import datetime, timedelta
import requests
from gmssl import sm2, sm3, func
import calendar
class CactiData:
    # 替换成你的私钥和公钥
    _private_key = "**"
    _public_key = "**"
    def __init__(self):
        pass
    def run(self):
        data = []
        # 读取custom.csv文件
        custom_data = self.read_custom_csv()
        for item in custom_data:
            graph_id = item['id']
            m_room = item['m_room']
            description = item['description']
            # 获取当前时间
            now = datetime.now()
            # 计算昨日0点和今日0点
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = today_start - timedelta(days=1)
            # 计算当月1号0点
            current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # 计算上月同期时间区间（从1号到上月同一天）
            if now.month == 1:
                # 如果是1月，则上个月是去年的12月
                last_month_year = now.year - 1
                last_month_month = 12
            else:
                last_month_year = now.year
                last_month_month = now.month - 1
            # 获取上个月的天数
            _, last_month_days = calendar.monthrange(last_month_year, last_month_month)
            # 取上个月同一天，如果上个月天数不够，取最后一天
            last_month_day = min(now.day, last_month_days)
            print(last_month_day)
            # 上月同期的开始时间：上个月1号的0点
            last_month_start = datetime(last_month_year, last_month_month, 1, 0, 0, 0)
            print(last_month_start)
            # 上月同期的结束时间：上个月同一天的下一天0点
            last_month_end = datetime(last_month_year, last_month_month, last_month_day, 0, 0, 0)
            print(last_month_end)
            # 格式化时间
            yesterday_start_str = yesterday_start.strftime('%Y-%m-%d %H:%M:%S')
            print(yesterday_start_str)
            today_start_str = today_start.strftime('%Y-%m-%d %H:%M:%S')
            print(today_start_str)
            current_month_start_str = current_month_start.strftime('%Y-%m-%d %H:%M:%S')
            last_month_start_str = last_month_start.strftime('%Y-%m-%d %H:%M:%S')
            last_month_end_str = last_month_end.strftime('%Y-%m-%d %H:%M:%S')
            # 获取昨日数据（用于计算昨日峰值和是否打峰）
            yesterday_data = self.get_data(graph_id, yesterday_start_str, today_start_str)
            # 获取当月1号至今的数据（用于计算1号至今95值）
            current_month_data = self.get_data(graph_id, current_month_start_str, today_start_str)
            # 获取上月同期数据（用于计算上月同期95值）
            last_month_data = self.get_data(graph_id, last_month_start_str, last_month_end_str)
            # 判断昨日是否打峰
            in_max_value = float(yesterday_data.get('inMaxValue', 0))
            in_average_value = float(yesterday_data.get('inAverageValue', 0))
            is_peak = "是" if in_average_value > 0 and in_max_value > 2 * in_average_value else "否"
            # 构建数据行
            row = {
                '机房': m_room,
                '客户名': description,
                '聚合图ID': graph_id,
                '昨日峰值(M)': yesterday_data.get('inMaxValue'),
                '昨日是否打峰': is_peak,
                '1号至今95值(M)': current_month_data.get('nfValue'),
                '上月同期95值(M)': last_month_data.get('nfValue')
            }
            data.append(row)
        self.write_to_csv(data)
    def read_custom_csv(self):
        custom_data = []
        with open('custom.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                custom_data.append({
                    'id': row['id'],
                    'm_room': row['m_room'],
                    'description': row['description']
                })
        return custom_data
    def get_data(self, graph_id: str, start_time:str, end_time:str):
        timestamp = str(round(time.time() * 1000))
        request_headers = {
            'version': '1.0',
            'appid': '1911799485',
            'serial': timestamp,
            'signtype': 'sm2'
        }
        request_body = {
            'trafficId': graph_id,
            'sequenceNo': 'sequenceNo',
            'startTime': start_time,
            'endTime': end_time
        }
        signature = self.create_sign(request_headers, request_body)
        request_headers['signature'] = signature
        url = 'http://10.105.1.253/cacti/plugins/api/v5/api.php'
        response = requests.post(url, headers=request_headers, json=request_body)
        result = response.json()
        if result.get('code') != 0:
            print(f"错误信息: {result.get('message')}, {result.get('subMsg')}")
            exit(-1)
        result_data = result.get('data')
        result_data.pop('picUrl', None)  # 添加默认值None，避免KeyError
        return result_data
    @staticmethod
    def write_to_csv(data: list):
        headers = ['机房','客户名','聚合图ID', '昨日峰值(M)', '昨日是否打峰','1号至今95值(M)','上月同期95值(M)']
        rows = []
        for item in data:
            row = [
                item.get('机房'),
                item.get('客户名'),
                item.get('聚合图ID'),
                item.get('昨日峰值(M)'),
                item.get('昨日是否打峰'),
                item.get('1号至今95值(M)'),
                item.get('上月同期95值(M)')
            ]
            rows.append(row)
        #current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        output_dir = 'output_custom'
        file_name = f'daily_cacti_data.csv'
        file_path = os.path.join(output_dir, file_name)
        os.makedirs(output_dir, exist_ok=True)
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"数据已成功写入 {file_path} 文件")
    def create_sign(self, headers: Dict[str, str], params: Dict[str, Any]) -> str:
        plain_text = self._get_sign_string(headers, params)
        print(f"签名原文: {plain_text}")
        plain_text_bytes = plain_text.encode('utf-8')
        sm2_signer = sm2.CryptSM2(
            public_key=self._public_key,
            private_key=self._private_key
        )
        signature_sm3 = sm3.sm3_hash(func.bytes_to_list(plain_text_bytes)).encode('utf-8')
        sign_rs_hex = sm2_signer.sign_with_sm3(signature_sm3)
        print("sign_rs_hex: ", sign_rs_hex)
        signature = base64.b64encode(sign_rs_hex.encode('utf-8')).decode('utf-8')
        print(f"签名结果: {signature}")
        return signature
    def _get_sign_string(self, headers: Dict[str, str], params: Dict[str, Any]) -> str:
        sign_data = {}
        for k, v in params.items():
            if v is None:
                continue
            sign_data[k] = v
        sign_data = dict(sorted(sign_data.items()))
        sign_arr = {
            'version': headers['version'],
            'appId': headers['appid'],
            'serial': headers['serial'],
            'body': None,
        }
        if sign_data:
            sign_arr['body'] = json.dumps(sign_data, ensure_ascii=False, separators=(',', ':'))
        return self._to_url_params(sign_arr)
    def _to_url_params(self, params: Dict[str, Any]) -> str:
        buff = []
        for k, v in params.items():
            if k == 'signature' or v is None or isinstance(v, (list, dict)):
                continue
            buff.append(f"{k}={v}")
        return "&".join(buff)
if __name__ == '__main__':
    cacti_data = CactiData()
    cacti_data.run()