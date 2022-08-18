import pika
connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
channel = connection.channel()

# 指定交换机名称和类型
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# 使用RabbitMQ给自己生成一个专属于自己的queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# 可以绑定多个routing_key，routing_key以点号分隔每个单词
# *可匹配一个单词，#可以匹配0个或多个单词
for binding_key in ['anonymous.*']:
    channel.queue_bind(
        exchange='topic_logs', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(
    queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
