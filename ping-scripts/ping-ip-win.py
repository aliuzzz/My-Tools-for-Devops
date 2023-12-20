import os
import subprocess

ping_cmd = os.path.join(os.environ['SystemRoot'], 'system32','ping.exe')

with open('./successip.txt', 'a') as success, open('./failip.txt', 'a') as fail:
    # 循环ping子网内其他IP
    for ip in range(1,255):
        ping_result = subprocess.call([ping_cmd, '-n', '1', '-w', '1000', '15.230.141.{}'.format(ip)], stdout=open(os.devnull, 'w'))
        if ping_result != 0:
            fail.write('15.230.141.{}\n'.format(ip))
        else:
            success.write('15.230.141.{}\n'.format(ip))