import pika


def main():
    # 1. 创建一个到RabbitMQ server的连接，如果连接的不是本机，
    # 则在pika.ConnectionParameters中传入具体的ip和port即可
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('124.221.105.58','5672'))
    # 2. 创建一个channel
    channel = connection.channel()
    # 3. 创建队列，queue_declare可以使用任意次数，
    # 如果指定的queue不存在，则会创建一个queue，如果已经存在，
    # 则不会做其他动作，官方推荐，每次使用时都可以加上这句
    channel.queue_declare(queue='hello')

    # 4. 定义消息处理程序
    def callback(ch, method, properties, body):
        print('[x] Received %r' % body)

    # 5. 接收来自指定queue的消息
    channel.basic_consume(
        queue='hello',  # 接收指定queue的消息
        on_message_callback=callback,  # 接收到消息后的处理程序
        auto_ack=True)  # 指定为True，表示消息接收到后自动给消息发送方回复确认，已收到消息
    print('[*] Waiting for message.')
    # 6. 开始循环等待，一直处于等待接收消息的状态
    channel.start_consuming()


if __name__ == '__main__':
    main()


