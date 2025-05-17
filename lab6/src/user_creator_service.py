import asyncio
from confluent_kafka import Consumer, KafkaError
from config import User
import time
import db
import json

# Конфигурация Kafka Consumer
conf = {
    "bootstrap.servers": "kafka1:9092,kafka2:9092",  # Адрес Kafka брокера
    "group.id": "user_group",  # ID группы потребителей
    "auto.offset.reset": "earliest",  # Начинать с самого раннего сообщения
}

# Цикл для получения сообщений
while True:
    try:
        time.sleep(1)
        # Создание Consumer
        consumer = Consumer(conf)

        # Подписка на топик
        consumer.subscribe(["user_topic"])

        print("We started consuming kafka queue!")

        # Цикл для получения сообщений
        try:
            while True:
                msg = consumer.poll(1.0)  # Ожидание сообщения в течение 1 секунды

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(msg.error())
                        break

                # Десериализация JSON и вывод на экран
                user = User.model_validate(json.loads(msg.value().decode("utf-8")))
                asyncio.run(
                    db.add_new_user(
                        user.login, user.hashed_password, user.name, user.surname
                    )
                )
                print(f"Received user data: {user}")

        except KeyboardInterrupt:
            pass

        finally:
            # Закрытие Consumer
            consumer.close()

    except:
        print("Try AGAIN!")
