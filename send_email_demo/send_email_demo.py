
import pandas as pd
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

#login
mail_host = "smtp.163.com"
mail_send = "roy6152@163.com"
mail_license = "邮箱授权码 16位"
mail_receivers = ["收件箱地址"]
mm = MIMEMultipart('related')

#theme
subject_content = "python测试"
mm["From"] = "sender_name<*****@qq.com>" #发送者邮箱
mm["To"] = "receiver_1_name<******@qq.com>"#接收者邮箱
mm["Subject"] = Header(subject_content,'urf-8')

#插入正文

