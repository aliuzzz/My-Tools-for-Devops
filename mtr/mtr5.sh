#!/bin/bash/
region=$1
zone=$2
name=$3
IP=$4
number=$5
mail=$6
if
  [ "$number" -eq 0 ]
then
mkdir /update/idc/$region >/dev/null 2>&1
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
fi

if
  [ "$number" -eq 1 ]
then
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
if
  ! [[ -f /data/mtr/${IP}.state ]]
then
  echo '0' > /data/mtr/${IP}.state
  echo 'false' > /data/mtr/${IP}.state
fi
sleep 1

if
  [[ \$(echo "\$lost > \$waring" | bc) = 1 ]];
then
  if
    [[ \$cfg -ge 1 ]]
  then
    initial_failure_time=\$(sed -n '1p' /data/mtr/${IP}.state)
    restore_flag=\$(sed -n '2p' /data/mtr/${IP}.state)
    rv_t=\$((\$(date +%s)-initial_failure_time))
    if
      (((rv_t>=295)&&(rv_t<=305)))
    then
      if
        [[ \${restore_flag} = true ]]
      then
        echo -e "节点：\$node，客户名称：\$name\\n\\n恢复时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，小于阈值\$waring%故障已恢复！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障恢复通知 【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】 roy6152@163.com,$mail
      fi
    fi
    echo 1 > \$cfg_dir
  else
    sed -i '2c\false' /data/mtr/${IP}.state
    if
      [[ \$(sed -n '1p' /data/mtr/${IP}.state) = 0 ]]
    then
      sed -i "1c\\\\\$(date +%s)" /data/mtr/${IP}.state
      echo -e "节点：\$node，客户名称：\$name\\n\\n故障时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，大于阈值\$waring%请立   即检查！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障发生通知 【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】  roy6152@163.com,$mail
    fi
    sleep 1
    
    echo 1 > \$cfg_dir
  fi

else
  
  if
    [[ "\$cfg" -ge 1 ]]
  then
    sed -i '2c\true' /data/mtr/${IP}.state
    if
      (((\$(date +%s)-\$(sed -n '1p' /data/mtr/${IP}.state))>=295))
    then
      sed -i '1c\0' /data/mtr/${IP}.state
      echo -e "节点：\$node，客户名称：\$name\\n\\n恢复时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，小于阈值\$waring%故障已恢复！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障恢复通知 【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】  roy6152@163.com,$mail
    fi
    sleep 1
    echo 0 > \$cfg_dir
  else
    initial_failure_time=\$(sed -n '1p' /data/mtr/${IP}.state)
    restore_flag=\$(sed -n '2p' /data/mtr/${IP}.state)
    rv_t=\$((\$(date +%s)-initial_failure_time))
    if
      (((rv_t>=295)&&(rv_t<=305)))
    then
      if
        [[ \${restore_flag} = true ]]
      then
        echo -e "节点：\$node，客户名称：\$name\\n\\n恢复时间：\`date -d "-1 minute" +%Y年%m月%d日%H时%M分\`\\n\\n事件:\$node to $IP,最后一跳丢包率为\$lost%，小于阈值\$waring%故障已恢复！\\n\\n 事件地址:\$http/mtr/\$File" | mail -s 故障恢复通知 【监测点:\$node,客户名称：\$name,IP:$IP,丢包率:\$lost%】  roy6152@163.com,$mail
      fi
    fi
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
