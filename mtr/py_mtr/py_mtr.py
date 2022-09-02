import threading
import time
import os
 
 
def run(ip):
    result=os.popen('mtr -r -c 56 -n  %s'%ip).read()
    print(result)
t1=threading.Thread(target=run,args=("27.221.49.45",))#创建线程1
t2=threading.Thread(target=run,args=("27.221.49.43",))#创建线程2
t3=threading.Thread(target=run,args=("124.236.115.34",))
t4=threading.Thread(target=run,args=("27.195.146.33",))
t5=threading.Thread(target=run,args=("124.132.135.244",))
t6=threading.Thread(target=run,args=("61.179.104.67",))
t7=threading.Thread(target=run,args=("61.179.104.147",))
t8=threading.Thread(target=run,args=("61.156.16.65",))
t9=threading.Thread(target=run,args=("61.133.50.21",))
t10=threading.Thread(target=run,args=("61.156.16.44",))
t11=threading.Thread(target=run,args=("27.221.53.4",))
t12=threading.Thread(target=run,args=("27.221.5.27",))
t13=threading.Thread(target=run,args=("150.138.148.226",))
#并发执行一共只等2秒
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()
t8.start()
t9.start()
t10.start()
t11.start()
t12.start()
t13.start()
