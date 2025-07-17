from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from qfluentwidgets import RoundMenu,MessageBox
from Ui_zbx_insert import Ui_Form
import sys, json, requests, configparser

config = configparser.ConfigParser()
config.read('D://0Work//Code//My-Tools-for-Devops//zbx_insert//zbx_insert.conf')
zbx_token = config['zbx_info']['zabbix_token']
zbx_api = config['zbx_info']['zabbix_api']
header = { "Content-Type": "application/json" }

def Get_hostgrp():
    hostgrp_data = {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": "extend",
            "filter": {
                "name": "交换机监控"
            }
        },
        "auth": zbx_token,
        "id": 1
    }
    res = requests.post(zbx_api,headers=header,data=json.dumps(hostgrp_data))
    groupid = json.loads(res.text)["result"][0]["groupid"]
    return groupid
#获取主机列表
def Get_hosts():
        host_data = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "name","host"],
                "filter": {
                    "groupids": Get_hostgrp()
                }
            },
            "auth": zbx_token,
            "id": 1
        }
        try:
            res = requests.post(zbx_api, headers=header, data=json.dumps(host_data))
            hosts = json.loads(res.text)["result"]
            return hosts
        except Exception as e:
            print(f"Get host info error: {e}")
            return []

def Get_tag():
    tag = ui.tag_lineEdit.text()
    return tag
def Get_hostid_label():
    hostid=int(ui.hostid_label.text())
    return hostid
def Get_item_name():
    item_name = ui.monitor_name_lineEdit.text()
    return item_name
def Get_key():
    key = ui.monitor_key_lineedit.text()
    return key
def get_selected_monitor_type_number():
    selected_text =  ui.monitor_type_comboBox.currentText()
    number = int(selected_text.split(' - ')[0])
    return number
def Get_value_type():
    value_type_text = ui.info_type_comboBox.currentText()
    value_type = int(value_type_text.split(' - ')[0])
    return value_type

def Get_formula():
    formula = ui.param_textEdit.toPlainText()
    return formula
def insert_items():
        host_data = {
            "jsonrpc": "2.0",
            "method": "item.create",
            "params": {
                "name": Get_item_name(),
                "key_": Get_key(),
                "hostid": Get_hostid_label(),
                "type": get_selected_monitor_type_number(),
                "value_type": Get_value_type(),
                "params":Get_formula(),
                "tags": [
                    {
                        "tag": Get_tag()
                    }
                ],
                "delay": "30s"
            },
            "auth": zbx_token,
            "id": 1
        }
        res = requests.post(zbx_api, headers=header, data=json.dumps(host_data))
        response_data = json.loads(res.text)
        try:
            if "error" in response_data:
                showDialog(False)
            else:
                showDialog(True)
        except Exception as e:
            print(f"Insert item error: {e}")

#获取端口信息
def Get_hosts_metric():
        hosts_metric = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["itemid", "hostid", "name", "key_"],
                "hostids": ui.hostid_label.text(),
                "search": {
                    "name": "Interface"
                },
                "sortfield": "name"
            },
            "auth": zbx_token,
            "id": 1
        }
        try:
            res = requests.post(zbx_api, headers=header, data=json.dumps(hosts_metric))
            port_info = json.loads(res.text)["result"]
            return port_info
        except Exception as e:
            print(f"Get host metric error: {e}")
            return []

def update_combobox():
    ui.traffic_comboBox.clear()
    hosts = Get_hosts()
    for host in hosts:
    # 封装 hostid 和 host 到一个字典中
        user_data = {
            'hostid': host['hostid'],
            'host': host['host']
        }
        ui.traffic_comboBox.addItem(host['name'], userData=user_data)
        ui.traffic_comboBox.setCurrentIndex(-1)

def update_hostid():
    user_data = ui.traffic_comboBox.currentData()
    if user_data: 
        hostid = user_data.get('hostid')
        if hostid:
            ui.hostid_label.setText(str(hostid))
    update_port_info()
def update_hostname():
    user_data = ui.traffic_comboBox.currentData()
    if user_data:
        host = user_data.get('host')
        if host:
            ui.hostname_label.setText(str(host))
def update_port_info():
    ui.monitor_listWidget.clear()
    try:
        port_info = Get_hosts_metric()
        if isinstance(port_info, list):
            # 过滤出包含"Bits"的条目
            filtered_ports = [port for port in port_info if 'Bits' in port['name']]
            for port in filtered_ports:
                ui.monitor_listWidget.addItem(f"{port['name']}-(ItemID: {port['itemid']})-(key:{port['key_']})")
    except Exception as e:
        ui.monitor_listWidget.addItem(str(e))

def transfer_items():
    # 获取左侧 QListWidget 中所有选中的项目
    selected_items = ui.monitor_listWidget.selectedItems()
    for item in selected_items:
        # 复制选中项目的文本到右侧 QListWidget
        ui.monitor_listWidget_in.addItem(item.text())

def delete_selected_items():
    # 获取右侧 QListWidget 中所有选中的项目
    selected_items = ui.monitor_listWidget_in.selectedItems()
    for item in selected_items:
        # 获取选中项目的行号
        row = ui.monitor_listWidget_in.row(item)
        # 从右侧 QListWidget 中删除该项目
        ui.monitor_listWidget_in.takeItem(row)

def on_combo_selected(index):
    host_name = ui.traffic_comboBox.currentText()
    host_id = ui.traffic_comboBox.currentData()
    print(f"选择的主机: {host_name}, ID: {host_id}")

def show_context_menu(pos):
    # 根据鼠标点击位置获取项目
    item = ui.monitor_listWidget_in.itemAt(pos)
    if item:
        # 以 list widget 作为菜单 parent
        menu = RoundMenu("",ui.monitor_listWidget_in)
        # 创建删除 action
        delete_action = QAction("Delete", menu)
        # 将触发信号连接到删除回调函数，通过lambda传递当前item
        delete_action.triggered.connect(lambda: delete_item(item))
        menu.addAction(delete_action)
        # 弹出菜单
        menu.exec(ui.monitor_listWidget_in.mapToGlobal(pos))

def delete_item(item):
    # 根据 item 找到所在行，然后删除该项
    row = ui.monitor_listWidget_in.row(item)
    ui.monitor_listWidget_in.takeItem(row)

def showDialog(success=True):
    if success:
        title = '操作成功'
        content = "监控项创建成功。"
    else:
        title = '操作失败'
        content = "监控项创建失败，请检查各项问题。"
    
    w = MessageBox(title, content, Form)
    w.setClosableOnMaskClicked(True)
    if w.exec():
        print('确认按钮已按下')
    else:
        print('取消按钮已按下')

if __name__ == '__main__':  
    Get_hostgrp()
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    update_combobox()
    update_hostid()
    update_hostname()
    ui.traffic_comboBox.currentIndexChanged.connect(on_combo_selected)
    ui.traffic_comboBox.currentIndexChanged.connect(update_hostid)
    ui.traffic_comboBox.currentIndexChanged.connect(update_hostname)
    ui.insert_pushButton.clicked.connect(transfer_items)
    ui.create_pushButton.clicked.connect(insert_items)
    ui.monitor_listWidget_in.customContextMenuRequested.connect(show_context_menu)
    ui.monitor_listWidget_in.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    Form.show()
    sys.exit(app.exec())
    
    
    
    