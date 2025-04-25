import json,requests
import pandas as pd


zabbix_api = "http://ip/api_jsonrpc.php"
zabbix_user = "Admin"
zabbix_pass =  "xxxxxxxxxx"


header = {
    "Content-Type": "application/json"
}

requests_token_data = {
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "username": zabbix_user,
        "password": zabbix_pass
    },
    "id": 1,
    "auth": None
}
#获取token
def Get_token():
    try:
        res = requests.post(zabbix_api, headers=header, data=json.dumps(requests_token_data))
        token = json.loads(res.text)["result"]
        return token

    except Exception:
        return "get token error"

#导出聚合端口报表
def Export_port_report():
    host_data = {
        "jsonrpc": "2.0",
        "method": "history.get",
        "params": {
            "output": "extend",
            #"history": 0,
            "itemids": ["48962"],
            #"sortfield": "clock",
            #"sortorder": "DESC",
            "time_from": "1739030400", #转为时间戳
            "time_till": "1739116800"
            #"limit": 10
        },
        "auth": Get_token(),
        "id": 1
    }
    try:
        res = requests.post(zabbix_api,headers=header,data=json.dumps(host_data))
        hosts_ip= json.loads(res.text)["result"]
        return hosts_ip
    except Exception:
        return "get host info error !"

if __name__ == '__main__':
    mes = Export_port_report()
    df = pd.DataFrame(mes)
    df['clock'] = pd.to_datetime(df['clock'].astype(int), unit='s')
    df = df[['clock', 'value']]
    df.columns = ['时间', '值']
    df.to_csv('output.csv', index=False)