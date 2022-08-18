import pika

connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
channel = connection.channel()

# 指定交换机
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# 使用RabbitMQ给自己生成一个专有的queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 将queue绑定到指定交换机
channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs.')


def callback(ch, method, properties, body):
    print(" [x] %r" % body)


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
