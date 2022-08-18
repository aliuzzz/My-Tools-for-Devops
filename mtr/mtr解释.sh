#!/bin/bash/
region=$1 #传入的第一个参数
zone=$2   #传入的第二个参数
name=$3
IP=$4
number=$5
mail=$6

if
  [ "$number" -eq 0 ]
then
#建一个文件夹，把标准输出重定向到“黑洞”，把错误输出夜重定向到标准输出1，即也导出到“黑洞”
mkdir /update/idc/$region >/dev/null 2>&1
#给下面路径的.sh文件加入下半部分的脚本，并以eof结束
#node
#mtr -r -c 显示报告并存到/data/mtr/
cat >/update/idc/$region/$zone-$IP-$name.sh<<EOF
#!/bin/sh
node=\$(awk '{if(\$0~"node") print\$2}' /root/mtr.conf)
Y=\`date   +%Y\`
m=\`date   +%m\`
d=\`date   +%d\`
H=\`date   +%H\`
File=\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/\`date +%H\`-$zone-$IP-$name[\$node].txt
date >>/data/mtr/\$File
/usr/sbin/mtr -r -c 56 -n $IP >>/data/mtr/\$File
echo "---------------------------------------------------------------------------------------" >>/data/mtr/\$File
EOF
#授权
chmod +x /update/idc/$region/$zone-$IP-$name.sh
#执行 创建递归目录，并输出到/update/idc/yuan.sh
#
echo "mkdir -p /data/mtr/\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/" >>/update/idc/yuan.sh
echo "/bin/sh /mtr/$region/$zone-$IP-$name.sh  &" >>/update/idc/yuan.sh
chmod +x /update/idc/yuan.sh
fi

if
  [ "$number" -eq 1 ]
then
#建文件夹idc和ali
mkdir /update/idc/$region >/dev/null 2>&1
mkdir /update/ali/$region >/dev/null 2>&1
mkdir /update/ali/state/ >/dev/null 2>&1

touch /update/ali/state/${IP}.cfg >/dev/null 2>&1

echo 0 > /update/ali/state/${IP}.cfg

cat >/update/ali/$region/$zone-$IP-${name}.sh<<EOF
#!/bin/sh
Y=\`date   +%Y\`
m=\`date   +%m\`
d=\`date   +%d\`
H=\`date   +%H\`

http=\$(awk '{if(\$0~"http") print\$2}' /root/mtr.conf)
waring=\$(awk '{if(\$0~"waring") print\$2}' /root/mtr.conf)
node=\$(awk '{if(\$0~"node") print\$2}' /root/mtr.conf)

name=$name
cfg_dir=/mtr/state/${IP}.cfg
cfg=\$(cat /mtr/state/${IP}.cfg)

File=\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/\`date +%H\`-$zone-$IP-$name[\$node].txt
touch /data/mtr/\$File >/dev/null 2>&1

lost=\$(awk -v RS="" '{if(\$0~'$IP');gsub(/%/,"");}{print \$(NF-7)}' /data/mtr/\$File)  

date >>/data/mtr/\$File
/usr/sbin/mtr -r -c 56 -n $IP >>/data/mtr/\$File
echo "---------------------------------------------------------------------------------------" >>/data/mtr/\$File

sleep 1

if
  [[ \$(echo "\$lost > \$waring" | bc) = 1 ]];   
then
  if
    [[ \$cfg -ge 1 ]]  大于等于1
  then
    echo 1 > \$cfg_dir
  else:
  echo 

    echo -e "节点：\$node，客户名称：\$name\\n\\n故障时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，大于阈
值\$waring%请立   即检查！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障发生通知
【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】 it@wxdata.cn,$mail
    sleep 1
    echo 1 > \$cfg_dir
  fi
else
  if
    [[ "\$cfg" -ge 1 ]]
  then
    echo -e "节点：\$node，客户名称：\$name\\n\\n恢复时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，小于阈
值\$waring%故障已恢复！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障恢复通知
【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】 it@wxdata.cn,$mail
    sleep 1
    echo 0 > \$cfg_dir
  else
    echo 0 > \$cfg_dir
  fi
fi
EOF

chmod +x /update/ali/$region/$zone-$IP-$name.sh
echo "mkdir -p /data/mtr/\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/" >>/update/ali/yuan.sh
echo "/bin/sh /mtr/$region/$zone-$IP-$name.sh  &" >>/update/ali/yuan.sh
cat >/update/idc/$region/$zone-$IP-$name.sh<<EOF
#!/bin/sh
node=\$(awk '{if(\$0~"node") print\$2}' /root/mtr.conf)
Y=\`date   +%Y\`
m=\`date   +%m\`
d=\`date   +%d\`
H=\`date   +%H\`
File=\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/\`date +%H\`-$zone-$IP-$name[\$node].txt
date >>/data/mtr/\$File
/usr/sbin/mtr -r -c 56 -n $IP >>/data/mtr/\$File
echo "---------------------------------------------------------------------------------------" >>/data/mtr/\$File
EOF
chmod +x /update/idc/$region/$zone-$IP-$name.sh
echo "mkdir -p /data/mtr/\`date +%Y年%m月\`/\`date +%Y年%m月%d日\`/$region/" >>/update/idc/yuan.sh
echo "/bin/sh /mtr/$region/$zone-$IP-$name.sh  &" >>/update/idc/yuan.sh
chmod +x /update/idc/yuan.sh
chmod +x /update/ali/yuan.sh
fi
