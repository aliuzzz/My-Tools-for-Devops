import paramiko
import datetime
import subprocess
#
#交换机文件路径
file_path = "flash:/startup.cfg"
destination_path = "/tmp/startup.cfg"
file_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname='', port=22, username='wxadmin', password='123456')
sftp = client.open_sftp()
sftp.get(source=file_path, remote_path=destination_path)
sftp.close()
client.close()
#--------------------------------
#移动文件备份
subprocess.run(['mv','/tmp/startup.cfg','/data/startup.cfg'])
#-------------------------------------
#上传
#new_file_path = 'flash:/startup.cfg'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='', port=22, username='wxadmin', password='123456')
sftp = ssh.open_sftp()
sftp.put(source=destination_path, remote_path=file_path)
command = ssh.invoke_shell()
command.send('save\n')
command.send('y\n')
sftp.close()
ssh.close()


