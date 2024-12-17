import sys, csv
from pathlib import Path
import paramiko
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal

class SSHThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, ip, username, password, command):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
        self.command = command

    def run(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, username=self.username, password=self.password)

            stdin, stdout, stderr = ssh.exec_command(self.command)
            output = stdout.read().decode()
            self.output_signal.emit(output)

            ssh.close()
        except Exception as e:
            self.output_signal.emit(str(e))

class NetworkTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('交换机统计信息')
        self.setWindowIcon(QIcon('.\Vswitch.ico'))
        self.setGeometry(100, 100, 500, 600)

        layout = QVBoxLayout()

        self.ip_label = QLabel('IP:')
        self.ip_input = QLineEdit()
        self.ip_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        self.username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        self.password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.command_label = QLabel('请输入需要键入的命令:')
        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")

        self.button0 = QPushButton('执行命令')
        self.button1 = QPushButton('进入交换机')
        self.button2 = QPushButton('查看模块信息(dis int transceiver verbose)')
        self.button3 = QPushButton('分析模块信息')
        self.button4 = QPushButton('清空输出')
        
        self.button0.setStyleSheet("""
            QPushButton {
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                font: bold;
                font-size: 15px;
                color: #000;
                min-width:20px;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #696969;
            }
        """)
        self.button1.setStyleSheet("""
            QPushButton {
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                font: bold;
                font-size: 15px;
                color: #000;
                min-width:20px;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #696969;
            }
        """)
        self.button2.setStyleSheet("""
            QPushButton {
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                font: bold;
                font-size: 15px;
                color: #000;
                min-width:20px;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #696969;
            }
        """)
        self.button3.setStyleSheet("""
            QPushButton {
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                font: bold;
                font-size: 15px;
                color: #000;
                min-width:20px;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #696969;
            }
        """)
        self.button4.setStyleSheet("""
            QPushButton {
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                font: bold;
                font-size: 15px;
                color: #000;
                min-width:20px;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #696969;
            }
        """)

        self.output = QTextEdit()
        self.output.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        self.output.setReadOnly(True)

        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.command_label)
        layout.addWidget(self.command_input)
        layout.addWidget(self.button0)
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)
        layout.addWidget(self.button3)
        layout.addWidget(self.button4)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.button0.clicked.connect(self.run_custom_command)
        self.button1.clicked.connect(self.enter_sys_mode)
        self.button2.clicked.connect(self.run_command)
        self.button3.clicked.connect(self.analyze_output)
        self.button4.clicked.connect(self.clear_output)

    def run_custom_command(self):
        command = self.command_input.text()
        
        if command and not (command.startswith('dis') or command.startswith('display')):
            QMessageBox.warning(self, "输入提示", "命令必须以 'dis'或'display' 开头")
            return
        ip = self.ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        self.start_ssh_thread(ip, username, password, command)
    def enter_sys_mode(self):
        ip = self.ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        command = 'dis this'  # 假设这是进入SYS模式的命令
        self.start_ssh_thread(ip, username, password, command)

    def run_command(self):
        ip = self.ip_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        command = 'dis int transceiver verbose'
        self.start_ssh_thread(ip, username, password, command)

    def start_ssh_thread(self, ip, username, password, command):
        self.ssh_thread = SSHThread(ip, username, password, command)
        self.ssh_thread.output_signal.connect(self.update_output)
        self.ssh_thread.start()

    def update_output(self, output):
        if "Error" in output or "Exception" in output:
            QMessageBox.critical(self, "错误", f"操作失败：{output}")
        else:
            QMessageBox.information(self, "成功", "操作成功")
            self.output.append(output)
            # 将输出写入文件
            ip = self.ip_input.text()
            filename = f"{ip}.txt"
            filepath = Path('output') / filename
            current_dir = Path(__file__).parent
            output_dir = current_dir / "output"
            # 确保output文件夹存在
            output_dir.mkdir(exist_ok=True)
            filepath = output_dir / filename
            #print(filepath)
            with open(filepath, 'w') as file:
                file.write(output)

    def analyze_output(self):
        port_info = {}
        ip = self.ip_input.text()
        filename = f"{ip}.txt"
        outputcsv = f"{ip}.csv"
        current_dir = Path(__file__).parent
        output_dir = current_dir / "output"
        filepath = output_dir / filename
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()

            current_port = None
            for line in lines:
                if "GE" in line:
                    transceiver_index = line.find("transceiver")
                    if transceiver_index != -1:
                        current_port = line[:transceiver_index].strip()
                        port_info[current_port] = {}
                elif current_port:
                    if "Transceiver Type" in line:
                        port_info[current_port]['Transceiver Type'] = line.split(":")[1].strip()
                    elif "Connector Type" in line:
                        port_info[current_port]['Connector Type'] = line.split(":")[1].strip()
                    elif "Wavelength (nm)" in line:
                        port_info[current_port]['Wavelength (nm)'] = line.split(":")[1].strip()
                    elif "Vendor Name" in line:
                        port_info[current_port]['Vendor Name'] = line.split(":")[1].strip()
                    elif "Part" in line:
                        port_info[current_port]['Vendor Part Number'] = line.split(":")[1].strip()
                    elif "Serial Number" in line:
                        port_info[current_port]['Serial Number'] = line.split(":")[1].strip()
                    elif "Manufacturing Date" in line:
                        port_info[current_port]['Manufacturing Date'] = line.split(":")[1].strip()
            
            
            # 写入CSV文件
            csvpath = output_dir / outputcsv
            with open(csvpath, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(["Port Name", "Transceiver Type", "Connector Type", "Wavelength (nm)", "Vendor Name", "Vendor Part Number", "Serial Number", "Manufacturing Date"])  # 写入表头
                for port, info in port_info.items():
                    transceiver_type = info.get('Transceiver Type', '')
                    connector_type = info.get('Connector Type', '')
                    wavelength = info.get('Wavelength (nm)', '')
                    vendor_name = info.get('Vendor Name', '')
                    vendor_part_number = info.get('Vendor Part Number', '')
                    manu_serial_number = info.get('Serial Number', '')
                    manufacturing_date = info.get('Manufacturing Date', '')
                    combined_info = f"{transceiver_type}-{connector_type}-{wavelength}-{vendor_name}-{vendor_part_number}-{manu_serial_number}-{manufacturing_date}"
                    csvwriter.writerow([port, transceiver_type, connector_type, wavelength, vendor_name, vendor_part_number, manu_serial_number, manufacturing_date])
                    print(f"{port}: {combined_info}")
            QMessageBox.information(self, "成功", "分析成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败：{str(e)}")

    def clear_output(self):
        self.output.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkTool()
    ex.show()
    sys.exit(app.exec())
