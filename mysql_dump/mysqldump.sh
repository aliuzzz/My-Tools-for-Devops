#!/bin/bash
#用户名
username= root
#密码
password = Qingdao789
#要备份的数据库
database_name=cacti
#保存备份文件最多个数
count=31
#备份路径
backup_path=/home/cacti_back_up
#日期
date_time=`date +%Y-%m-%d-%H-%M`

#如果文件夹不存在则创建
if [ ! -d $backup_path ]; 
then     
    mkdir -p $backup_path; 
fi

#备份
mysqldump -u $username -p $password $database_name > $backup_path/$database_name-$date_time.sql
#开始压缩
cd $backup_path
tar -zcvf $database_name-$date_time.tar.gz $database_name-$date_time.sql
#删除源文件
#rm -rf $backup_path/$database_name-$date_time.sql
#更新备份日志
echo "create $backup_path/$database_name-$date_time.tar.gz" >> $backup_path/data_dump.log

#找出需要删除的备份(第九列第一行)
delfile=`ls -l -crt  $backup_path/*.tar.gz | awk '{print $9 }' | head -1`

#判断现在的备份数量是否大于阈值（第九列 行数）
number=`ls -l -crt  $backup_path/*.tar.gz | awk '{print $9 }' | wc -l`

if [ $number -gt $count ]
then
  #删除最早生成的备份，只保留count数量的备份
  rm $delfile
  #更新删除文件日志
  echo "delete $delfile" >> $backup_path/data_dump.log
fi