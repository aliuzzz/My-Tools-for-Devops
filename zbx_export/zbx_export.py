import json, requests, configparser, csv, os
from datetime import datetime

# ===== 配置读取 =====
CONFIG_PATH = r'D://0Work//Code//My-Tools-for-Devops//zbx_export//zbx_export.conf'
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')

ZBX_TOKEN = config['zbx_info']['zabbix_token']
ZBX_API = config['zbx_info']['zabbix_api']
TEMPLATE_NAME = config['export_info']['templates_name']
ITEM_NAME = config['export_info']['item_name']
TIME_FROM = int(config['export_info']['time_from'])
TIME_TILL = int(config['export_info']['time_till'])
HEADERS = {"Content-Type": "application/json"}

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
    return zbx_call("host.get", {"output": ["hostid", "host"], "templateids": template_id})

# 通过主机id和监控项名称获取监控项
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
        #"limit": 100000
    })

# ===== 分析与导出 =====
#传入values,返回cnt, mx, mn, avg
def analyze(values):
    if not values:
        return 0, None, None, None
    cnt = len(values) # 计数
    mx = max(values) # 最大
    mn = min(values) # 最小
    avg = sum(values) / cnt # 平均
    return cnt, mx, mn, avg

#导出的csv文件命名
def safe_filename(s):
    return "".join(c if c.isalnum() or c in "._- " else "_" for c in s)

#导出csv
def export_csv(host_name, item_name, rows, out_dir="zbx_exports"):
    os.makedirs(out_dir, exist_ok=True)
    cnt, mx, mn, avg = analyze([v for _, v in rows])
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{safe_filename(host_name)}__{safe_filename(item_name)}__{ts}.csv"
    fpath = os.path.join(out_dir, fname)

    with open(fpath, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        # 顶部摘要信息（开头几行）
        w.writerow(["host", host_name])
        w.writerow(["item_name", item_name])
        w.writerow(["count", cnt])
        w.writerow(["max(%)", f"{mx:.2f}%" if mx is not None else ""])
        w.writerow(["min(%)", f"{mn:.2f}%" if mn is not None else ""])
        w.writerow(["avg(%)", f"{avg:.2f}%" if avg is not None else ""])
        w.writerow([])  # 空行分隔
        # 明细两列表头
        w.writerow(["时间", "值(百分比)"])
        for clock, value in rows:
            w.writerow([
                datetime.fromtimestamp(clock).strftime("%Y-%m-%d %H:%M:%S"),
                f"{value:.2f}%"
            ])
    print(f"已导出: {fpath}")

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

    for i, host in enumerate(hosts, 1):
        print(f"\n[{i}/{len(hosts)}] 主机: {host['host']} ({host['hostid']})")
        items = get_items(host['hostid'], ITEM_NAME)
        if not items:
            print(f"  未找到监控项: {ITEM_NAME}")
            continue

        for j, item in enumerate(items, 1):
            print(f"  - 监控项 {j}/{len(items)}: {item['name']} (itemid: {item['itemid']})")
            hist = get_history(item['itemid'], item['value_type'], TIME_FROM, TIME_TILL)
            rows = []
            for h in hist:
                try:
                    rows.append((int(h['clock']), float(h['value'])))
                except:
                    pass
            cnt, mx, mn, avg = analyze([v for _, v in rows])
            print(f"    数据条数: {cnt}" + (f" | max: {mx:.2f}% min: {mn:.2f}% avg: {avg:.2f}%" if cnt else ""))
            export_csv(host['host'], item['name'], rows)

    print("\n所有主机处理完成！")

if __name__ == '__main__':
    main()