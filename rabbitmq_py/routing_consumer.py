import pika

connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
channel = connection.channel()

# 指定交换机名称和类型
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# 使用RabbitMQ给自己生成一个专属于自己的queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 绑定queue到交换机，并指定自己只接受哪些routing_key
# 可以都接收，也可以只接收一种
# for severity in ['error', 'warning', 'info']:
for severity in ['error']:
    channel.queue_bind(
        exchange='direct_logs', queue=queue_name, routing_key=severity)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
