from ipaddress import IPv4Network

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
        print(f"处理 {ip_with_subnet} 时发生错误: {e}")
        return None

# 读取文件
try:
    with open('sdip.txt', 'r') as file:
        for line in file:
            ip_with_subnet = line.strip()
            complement = calculate_netmask_complement(ip_with_subnet)
            if complement is not None:
                ip_address, _ = ip_with_subnet.split('/')
                print(f"IP: {ip_address} 的反掩码是: {complement}")
                print(f"rule permit ip source 27.222.10.0 0.0.0.127 destination {ip_address} {complement}")
except FileNotFoundError:
    print("文件未找到，请检查文件路径和名称是否正确。")
except IOError as e:
    print(f"读取文件时发生IO错误: {e}")