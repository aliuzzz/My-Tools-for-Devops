#!/bin/bash
# 备份原配置文件
echo "正在备份原配置文件..."
bak = ls -1 /etc/netplan/ | head -n 1

mv /etc/netplan/$bak /etc/netplan/$bak.bak

# 首先确认网络是否联通
ping -c 2 ispip.clang.cn
if [ $? -ne 0 ]; then
    echo "网络不通，请检查网络连接或URL是否正确。"
    exit 1
fi
echo "网络通畅，开始配置网络"
sleep 1

echo "请输入要配置的IP地址数量:"
read ip_count

# 验证输入是否为数字
if ! [[ "$ip_count" =~ ^[0-9]+$ ]]; then
    echo "错误: 请输入一个有效的数字"
    exit 1
fi

# 创建临时存储IP的数组和网关的数组
declare -a ip_addresses
declare -a gateways

# 获取所有IP地址和对应的网关
for ((i=1; i<=$ip_count; i++)); do
    echo "请输入第 $i 个IP地址(格式如: 192.168.1.100/24):"
    read ip
    
    # 验证IP地址格式
    if ! [[ $ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$ ]]; then
        echo "错误: IP地址格式不正确"
        exit 1
    fi
    
    echo "请输入第 $i 个IP地址对应的网关地址(格式如: 192.168.1.1):"
    read gateway
    
    # 验证网关地址格式
    if ! [[ $gateway =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "错误: 网关地址格式不正确"
        exit 1
    fi
    
    ip_addresses+=("$ip")
    gateways+=("$gateway")
done

# 用户输入网卡名称
read -p "请输入您的网卡名称 (默认为 eno1): " interface_name
interface_name=${interface_name:-eno1}

# 临时文件
TEMP_FILE_1="/tmp/temp_file_1.txt"
TEMP_FILE_2="/tmp/temp_file_2.txt"
TEMP_FILE_3="/tmp/temp_file_3.txt"

# 为每个网关配置运营商路由表
for ((i=1; i<=$ip_count; i++)); do
    echo "为第 $i 个网关 (${gateways[$i-1]}) 配置运营商路由表:"
    echo "1) 移动"
    echo "2) 联通"
    echo "3) 电信"
    echo "4) 跳过此网关的运营商路由配置"
    read -p "请输入选项 (1, 2, 3 或 4): " choice

    case $choice in
        1)
            curl -s https://ispip.clang.cn/cmcc.txt > "TEMP_FILE_$i"
            ;;
        2)
            curl -s https://ispip.clang.cn/unicom_cnc.txt > "TEMP_FILE_$i"
            ;;
        3)
            curl -s https://ispip.clang.cn/chinatelecom.txt > "TEMP_FILE_$i"
            ;;
        4)
            echo "跳过第 $i 个网关的运营商路由配置"
            ;;
        *)
            echo "无效的选项，跳过此网关的运营商路由配置"
            ;;
    esac
done

# 生成yaml文件的开始部分
cat > /etc/netplan/00-installer-config.yaml << EOF
network:
    version: 2
    renderer: networkd
    ethernets:
        $interface_name:
            dhcp4: no
            dhcp6: no
            addresses: 
EOF

# 添加IP地址
for ip in "${ip_addresses[@]}"; do
    echo "            - $ip" >> /etc/netplan/00-installer-config.yaml
done

# 添加nameservers
cat >> /etc/netplan/00-installer-config.yaml << EOF
            nameservers:
                addresses: [223.5.5.5]
            routes:
EOF

# 添加默认路由（使用第一个网关）
echo "            - to: default" >> /etc/netplan/00-installer-config.yaml
echo "              via: ${gateways[0]}" >> /etc/netplan/00-installer-config.yaml
echo "              on-link: true" >> /etc/netplan/00-installer-config.yaml

# 添加运营商路由表
for ((i=1; i<=$ip_count; i++)); do
    if [ -f "TEMP_FILE_$i" ]; then
        while IFS= read -r line; do
            if [ ! -z "$line" ]; then  # 确保行不为空
                ip=$(echo "$line" | sed 's/\ //g')
                echo "            - to: $ip" >> /etc/netplan/00-installer-config.yaml
                echo "              via: ${gateways[$i-1]}" >> /etc/netplan/00-installer-config.yaml
            fi
        done < "TEMP_FILE_$i"
        rm "TEMP_FILE_$i"
    fi
done

echo "配置文件已生成为 /etc/netplan/00-installer-config.yaml"
