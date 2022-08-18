import pika
import time

connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
channel = connection.channel()

# 声明durable=True可以保证RabbitMQ服务挂掉之后队列中的消息也不丢失，原理是因为
# RabbitMQ会将queue中的消息保存到磁盘中
channel.queue_declare(queue='task_queue')
print(' [*] Waiting for messages.')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body.decode())
    # 此处以消息中的“.”的数量作为sleep的值，是为了模拟不同消息处理的耗时
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    # 手动标记消息已接收并处理完毕，RabbitMQ可以从queue中移除该条消息
    ch.basic_ack(delivery_tag=method.delivery_tag)


# prefetch_count表示接收的消息数量，当我接收的消息没有处理完（用basic_ack
# 标记消息已处理完毕）之前不会再接收新的消息了
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()
