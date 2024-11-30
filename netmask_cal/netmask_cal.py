import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDialog, QTextEdit, QRadioButton, QHBoxLayout
from ipaddress import IPv4Network, IPv6Network, AddressValueError
from PyQt6.QtCore import Qt

class SubnetCalculator(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('子网掩码计算器-支持ipv4和ipv6')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        ip_label = QLabel('ip地址(标准IPv4或IPv6地址):')
        ip_label.setStyleSheet("font-size: 15px")
        self.ip_input = QLineEdit()
        self.ip_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        layout.addWidget(ip_label)
        layout.addWidget(self.ip_input)

        subnet_label = QLabel('掩码(掩码位或掩码前缀):')
        subnet_label.setStyleSheet("font-size: 15px")
        self.subnet_input = QLineEdit()
        self.subnet_input.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        layout.addWidget(subnet_label)
        layout.addWidget(self.subnet_input)

        ip_version_layout = QHBoxLayout()
        self.ipv4_radio = QRadioButton('IPv4')
        self.ipv6_radio = QRadioButton('IPv6')
        self.ipv4_radio.setStyleSheet("""
            QRadioButton{
                spacing:12px;
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                border-radius:8px;
                padding:4px;
                }
        """)
        self.ipv6_radio.setStyleSheet("""
            QRadioButton{
                spacing:12px;
                background-color: rgba(192, 192, 192,125);
                border:1px outset rgb(255, 255, 255);
                border-radius:8px;
                padding:4px;
                }
        """)
        self.ipv4_radio.setChecked(True)
        ip_version_layout.addWidget(self.ipv4_radio)
        ip_version_layout.addWidget(self.ipv6_radio)
        layout.addLayout(ip_version_layout)

        calculate_button = QPushButton('计算')
        calculate_button.clicked.connect(self.calculate)
        layout.addWidget(calculate_button)
        calculate_button.setStyleSheet("""
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
        show_ips_button = QPushButton('可用IPs')
        show_ips_button.clicked.connect(self.show_usable_ips)
        layout.addWidget(show_ips_button)
        show_ips_button.setStyleSheet("""
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
        self.network_label = QLabel('网络地址:')
        self.broadcast_label = QLabel('广播地址:')
        self.hosts_label = QLabel('可用IP数:')
        self.first_usable_label = QLabel('第一个可用IP:')
        self.last_usable_label = QLabel('最后一个可用IP:')
        
        self.network_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.broadcast_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.hosts_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.first_usable_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.last_usable_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(self.network_label)
        layout.addWidget(self.broadcast_label)
        layout.addWidget(self.hosts_label)
        layout.addWidget(self.first_usable_label)
        layout.addWidget(self.last_usable_label)
        
        self.network_label.setStyleSheet("font-size: 15px")
        self.broadcast_label.setStyleSheet("font-size: 15px")
        self.hosts_label.setStyleSheet("font-size: 15px")
        self.first_usable_label.setStyleSheet("font-size: 15px")
        self.last_usable_label.setStyleSheet("font-size: 15px")

        self.setLayout(layout)

    def calculate(self):
        ip_address = self.ip_input.text()
        subnet_mask = self.subnet_input.text()
        try:
            if self.ipv4_radio.isChecked():
                network = IPv4Network(f'{ip_address}/{subnet_mask}', strict=False)
            else:
                network = IPv6Network(f'{ip_address}/{subnet_mask}', strict=False)

            network_address = network.network_address
            broadcast_address = network.broadcast_address if isinstance(network, IPv4Network) else None
            num_hosts = network.num_addresses - 2 if isinstance(network, IPv4Network) else network.num_addresses - 1

            # 计算第一个和最后一个可用ip
            first_usable_ip = network_address + 1
            last_usable_ip = broadcast_address - 1 if isinstance(network, IPv4Network) else network.broadcast_address

            self.network_label.setText(f'网络地址: {network_address}')
            if broadcast_address:
                self.broadcast_label.setText(f'广播地址: {broadcast_address}')
            else:
                self.broadcast_label.setText('广播地址: N/A')
            self.hosts_label.setText(f'可用IP数: {num_hosts}')
            self.first_usable_label.setText(f'第一个可用IP: {first_usable_ip}')
            self.last_usable_label.setText(f'最后一个可用IP: {last_usable_ip}')

            # 存下来可用ip
            self.network = network
        except (ValueError, AddressValueError) as e:
            QMessageBox.critical(self, 'Error', str(e))

    def show_usable_ips(self):
        if not hasattr(self, 'network'):
            QMessageBox.warning(self, 'Warning', '请先计算子网')
            return
        usable_ips = []
        if isinstance(self.network, IPv4Network):
            usable_ips = [str(ip) for ip in self.network.hosts()]
        elif isinstance(self.network, IPv6Network):
            # 针对ipv6优化，限制最多显示255个
            QMessageBox.warning(self, 'Warning', '可用数量过多，只显示前255个')
            usable_ips = [str(self.network.network_address + i) for i in range(1, min(256, self.network.num_addresses - 1))]
            #return
        
        dialog = QDialog(self)
        dialog.setWindowTitle('可用的IPs')
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText('\n'.join(usable_ips))
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                font-size: 15px;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = SubnetCalculator()
    calculator.show()
    sys.exit(app.exec())