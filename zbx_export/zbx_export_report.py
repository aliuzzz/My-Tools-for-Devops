import json, requests, configparser, csv, os
from datetime import datetime

# ===== 配置读取 =====
CONFIG_PATH = r'./zbx_export.conf'
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')

ZBX_TOKEN = config['zbx_info']['zabbix_token']
ZBX_API = config['zbx_info']['zabbix_api']
TEMPLATE_NAME = config['export_info']['templates_name']
ITEM_NAME_RAW = config['export_info']['item_name']  # 可能包含多个，用逗号分隔
TIME_FROM = int(config['export_info']['time_from'])
TIME_TILL = int(config['export_info']['time_till'])
HEADERS = {"Content-Type": "application/json"}

# 将配置中的多个 item 名解析为列表，去除空项和首尾空格
ITEM_NAMES = [s.strip() for s in ITEM_NAME_RAW.split(',') if s.strip()]

# ===== 封装，通用 Zabbix 调用 =====
def zbx_call(method, params):
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "auth": ZBX_TOKEN, "id": 1}
    try:
        res = requests.post(ZBX_API, headers=HEADERS, data=json.dumps(payload), timeout=30)
        res.raise_for_status()
        data = res.json()
        if 'error' in data:
            raise RuntimeError(data['error'])
        return data.get('result', [])
    except Exception as e:
        print(f"[{method}] failed: {e}")
        return []

# ===== 数据获取 =====

# 通过模板名称获取模板id
def get_template_id(name):
    r = zbx_call("template.get", {"output": ["templateid"], "filter": {"host": name}})
    return r[0]['templateid'] if r else None

# 通过模板id获取主机
def get_hosts(template_id):
    return zbx_call("host.get", {"output": ["hostid", "host","name"], "templateids": template_id})

# 通过主机id和监控项名称（子串搜索）获取监控项
def get_items(hostid, name_substr):
    return zbx_call("item.get", {
        "output": ["itemid", "name", "value_type"],
        "hostids": hostid,
        "search": {"name": name_substr},
        "sortfield": "name"
    })

# 通过监控项id获取历史数据，限制时间开始和结束
def get_history(itemid, value_type, t_from, t_till):
    return zbx_call("history.get", {
        "output": ["clock", "value"],
        "history": value_type,
        "itemids": itemid,
        "time_from": t_from,
        "time_till": t_till,
        "sortfield": "clock",
        "sortorder": "ASC",
        # "limit": 10000000
    })

# ===== 分析与导出 =====
# 传入values,返回cnt, mx, mn, avg
def analyze(values):
    if not values:
        return 0, None, None, None
    cnt = len(values) # 计数
    mx = max(values) # 最大
    mn = min(values) # 最小
    avg = sum(values) / cnt # 平均
    return cnt, mx, mn, avg

# 导出的csv文件命名安全
def safe_filename(s):
    return "".join(c if c.isalnum() or c in "._- " else "_" for c in s)

# 初始化CSV文件（创建表头）
def init_csv(out_file):
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    # 如果文件不存在或为空，创建表头
    if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
        with open(out_file, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            # 写入表头
            w.writerow(["host", "name", "item_name", "count", "max(%)", "min(%)", "avg(%)"])

# 追加数据到CSV文件
def append_to_csv(out_file, host_name, host_display_name, item_name, cnt, mx, mn, avg):
    with open(out_file, 'a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # 写入数据行
        w.writerow([
            host_name,
            host_display_name,
            item_name,
            cnt,
            f"{mx:.2f}%" if mx is not None else "",
            f"{mn:.2f}%" if mn is not None else "",
            f"{avg:.2f}%" if avg is not None else ""
        ])

# ===== 主流程 =====
def main():
    print("=== Zabbix 数据导出工具 ===")
    if TIME_FROM > TIME_TILL:
        print("time_from > time_till，请检查配置")
        return

    tpl_id = get_template_id(TEMPLATE_NAME)
    if not tpl_id:
        print(f"未找到模板: {TEMPLATE_NAME}")
        return

    hosts = get_hosts(tpl_id)
    if not hosts:
        print("没有找到任何主机")
        return
    print(f"找到 {len(hosts)} 个主机")

    # 输出目录
    out_dir = "zbx_exports"
    os.makedirs(out_dir, exist_ok=True)

    # 日期戳（只到日）
    date_str = datetime.now().strftime("%Y%m%d")

    # 为每个指标分别生成一个 CSV
    for idx_name in ITEM_NAMES:
        print(f"\n=== 处理指标: {idx_name} ===")
        # 指标名用于文件名的安全化
        idx_name_for_file = safe_filename(idx_name)
        out_file = os.path.join(out_dir, f"zbx_summary_{idx_name_for_file}_{date_str}.csv")
        init_csv(out_file)
        print(f"输出文件: {out_file}")

        total_hosts_with_item = 0

        for i, host in enumerate(hosts, 1):
            print(f"\n[{i}/{len(hosts)}] 主机: {host['host']} ({host['name']})")
            items = get_items(host['hostid'], idx_name)
            # 调试输出可按需注释
            # print(items)
            if not items:
                print(f"  未找到监控项包含: {idx_name}")
                continue

            total_hosts_with_item += 1

            for j, item in enumerate(items, 1):
                print(f"  - 监控项 {j}/{len(items)}: {item['name']} (itemid: {item['itemid']})")
                hist = get_history(item['itemid'], item['value_type'], TIME_FROM, TIME_TILL)

                # 处理历史数据
                values = []
                for h in hist:
                    try:
                        values.append(float(h['value']))
                    except:
                        pass

                # 分析数据
                cnt, mx, mn, avg = analyze(values)
                if cnt:
                    print(f"    数据条数: {cnt} | max: {mx:.2f}% min: {mn:.2f}% avg: {avg:.2f}%")
                else:
                    print(f"    数据条数: {cnt}")

                # 追加到CSV文件
                append_to_csv(out_file, host['host'], host['name'], item['name'], cnt, mx, mn, avg)

        print(f"\n指标 '{idx_name}' 处理完成，匹配到监控项的主机数: {total_hosts_with_item}。文件: {out_file}")

    print("\n所有指标处理完成！")

if __name__ == '__main__':
    main()