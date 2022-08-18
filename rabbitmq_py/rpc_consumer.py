import pika


connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
channel = connection.channel()

# 指定接收消息的queue
channel.queue_declare(queue='rpc_queue')


def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

    ch.basic_publish(exchange='',  # 使用默认交换机
                     routing_key=props.reply_to,  # response发送到该queue
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id),  # 使用correlation_id让此response与请求消息对应起来
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
# 从rpc_queue中取消息，然后使用on_request进行处理
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
