import configparser
import random
import subprocess


# 创建配置解析器
config = configparser.ConfigParser()

try:
    config.read('/root/xg_download/xg_config.conf')

    # 获取 [dns] 部分的 ctcc 选项的值
    ctcc_dns = config.get('dnsv6', 'cucc')
    dns_list = ctcc_dns.split(',')
    # 随机选择 2 个 DNS
    selected_dns = random.sample(dns_list, 2)

    dns_str = ' '.join(selected_dns)
    commands = [
        f'nmcli con modify ens18 ipv6.dns "{dns_str}"',
        'nmcli con reload',
        'nmcli con up ens18'
    ]

    for command in commands:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"命令 {command} 执行成功。")
        else:
            print(f"命令 {command} 执行失败，错误信息: {result.stderr}")
            break

except configparser.NoSectionError:
    print("错误: 配置文件中没有 [dns] 部分。")
except configparser.NoOptionError:
    print("错误: [dns] 部分中没有 ctcc 选项。")
except FileNotFoundError:
    print("错误: 未找到配置文件。")
except ValueError:
    print("错误: ctcc 选项中的 DNS 数量少于 2 个。")
except Exception as e:
    print(f"发生未知错误: {e}")
    
