import sys
from ipaddress import IPv4Network
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QRadioButton

class TextConverter(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        # 左边的文本编辑器和标签
        self.left_label = QLabel("ip地址段/子网掩码，每行一个:")
        self.left_text_edit = QTextEdit()
        self.left_text_edit.setText('举例：\n192.168.1.0/24')
        
        # 反掩码按钮
        self.towildcardmask_button = QPushButton("计算反掩码>>")
        self.towildcardmask_button.clicked.connect(self.toWildcardMask)  #转换为反掩码
        
        # acl标签
        self.acl_top_label = QLabel("需要在acl里添加的源地址和反掩码")
        self.acl_top_text_edit = QTextEdit()
        self.acl_top_text_edit.setText('举例：\n172.16.1.0 255.255.255.0')
        self.acl_bottom_label = QLabel("生成acl:")
        self.acl_bottom_text_edit = QTextEdit()
        
        # 右边的按钮
        self.copy_button = QPushButton("生成acl>>")
        self.copy_button.clicked.connect(self.toacl)
        
        mode_layout = QHBoxLayout()
        self.mode_generate_acl_permit = QRadioButton("模式为permit")
        self.mode_generate_acl_deny = QRadioButton("模式为deny")
        self.mode_generate_acl_permit.setChecked(True) 
        mode_layout.addWidget(self.mode_generate_acl_permit)
        mode_layout.addWidget(self.mode_generate_acl_deny)
        # 连接信号与槽
        self.mode_generate_acl_permit.toggled.connect(self.on_mode_change)
        self.mode_generate_acl_deny.toggled.connect(self.on_mode_change)
        
        # 中间区域的文本编辑器和标签
        self.middle_label = QLabel("ip 反掩码:")
        self.middle_text_edit = QTextEdit()
        
        # 左侧布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.left_label)
        left_layout.addWidget(self.left_text_edit)
        
        # 右侧区域布局
        acl_layout = QVBoxLayout()
        acl_layout.addWidget(self.acl_top_label)
        acl_layout.addWidget(self.acl_top_text_edit, stretch=1)
        acl_layout.addLayout(mode_layout)
        

        acl_layout.addWidget(self.acl_bottom_label)
        acl_layout.addWidget(self.acl_bottom_text_edit, stretch=10)
        
        # 中间布局
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(self.middle_label)
        middle_layout.addWidget(self.middle_text_edit)
        
        # 主布局 - 水平布局
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.towildcardmask_button)
        main_layout.addLayout(middle_layout)
        main_layout.addWidget(self.copy_button)
        main_layout.addLayout(acl_layout)
        
        self.setLayout(main_layout)
        
        self.setWindowTitle('反掩码ACL批量转换工具')
        self.show()
    
    def toWildcardMask(self):
        def calculate_netmask_complement(ip_with_subnet):
            try:
                # 分割IP地址和子网掩码
                ip_address, _ = ip_with_subnet.split('/')
                
                # 创建IPv4Network对象，使用原始的ip_with_subnet字符串
                network = IPv4Network(ip_with_subnet)
                # 将子网掩码转换为点分十进制字符串
                netmask_str = str(network.netmask)
                # 将点分十进制字符串转换为整数
                netmask_int = sum([256 ** (3-i) * int(b) for i, b in enumerate(netmask_str.split('.'))])
                # 计算32位全1的二进制表示
                all_ones = (1 << 32) - 1
                # 反掩码是所有位为1的值与子网掩码做按位异或运算的结果
                complement = all_ones ^ netmask_int
                # 将结果转换回点分十进制格式
                return '.'.join(str((complement >> (8 * i)) & 0xFF) for i in range(4)[::-1])
            except ValueError as e:
                ouptput_line = f"{ip_with_subnet} 不是该ip段中首位"
                self.middle_text_edit.append(ouptput_line)
                return None
        
        self.middle_text_edit.clear()
        ip_list_text=self.left_text_edit.toPlainText()
        
        for line in ip_list_text.splitlines():
            ip_with_subnet = line.strip()
            print(ip_with_subnet)
            complement = calculate_netmask_complement(ip_with_subnet)
            if complement is not None:
                ip_address, _ = ip_with_subnet.split('/')
                ouptput_line = f"{ip_address}  {complement}"
                self.middle_text_edit.append(ouptput_line)

    def toacl(self):        
        self.acl_bottom_text_edit.clear()
        ip_list_text=self.left_text_edit.toPlainText()
        origin_ip =self.acl_top_text_edit.toPlainText()
        
        def calculate_netmask_complement(ip_with_subnet):
            try:
                # 分割IP地址和子网掩码
                ip_address, _ = ip_with_subnet.split('/')
                
                # 创建IPv4Network对象，使用原始的ip_with_subnet字符串
                network = IPv4Network(ip_with_subnet)
                # 将子网掩码转换为点分十进制字符串
                netmask_str = str(network.netmask)
                # 将点分十进制字符串转换为整数
                netmask_int = sum([256 ** (3-i) * int(b) for i, b in enumerate(netmask_str.split('.'))])
                # 计算32位全1的二进制表示
                all_ones = (1 << 32) - 1
                # 反掩码是所有位为1的值与子网掩码做按位异或运算的结果
                complement = all_ones ^ netmask_int
                # 将结果转换回点分十进制格式
                return '.'.join(str((complement >> (8 * i)) & 0xFF) for i in range(4)[::-1])
            except ValueError as e:
                ouptput_line = f"{ip_with_subnet} 不是该ip段中首位"
                self.middle_text_edit.append(ouptput_line)
                return None
        
        for line in ip_list_text.splitlines():
            ip_with_subnet = line.strip()
            complement = calculate_netmask_complement(ip_with_subnet)
            if complement is not None:
                ip_address, _ = ip_with_subnet.split('/')
                print(self.on_mode_change())
                mode = self.on_mode_change()
                ouptput_line = f"rule {mode} ip source {origin_ip} destination {ip_address} {complement}"
                self.acl_bottom_text_edit.append(ouptput_line)
    
    def on_mode_change(self):
        # 槽函数用于响应单选按钮状态的改变
        if self.mode_generate_acl_permit.isChecked():
            mode = f"permit"
            return mode
            #pass
        elif self.mode_generate_acl_deny.isChecked():
            mode = f"deny"
            # 当“复制到剪贴板”被选中时的操作
            return mode
            #pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextConverter()
    sys.exit(app.exec())