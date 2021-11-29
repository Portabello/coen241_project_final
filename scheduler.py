from pymongo import MongoClient
import pika

class scheduler:
    def __init__(self, mongoURL, rabbitURL):
        self.client = MongoClient(host=[mongoURL], serverSelectionTimeoutMS = 3000)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
        self.channel = connection.channel()
        self.channel.queue_declare(queue="hello")

    def scan(self):
        cursors = self.client.db.link.find()
        for cursor in cursors:
            if self.client.db.visited.find({'key': cursor.link}):
                self.client.db.link.delete(cursor)
                continue

            self.channel.basic_publish(exchange='', routing_key='hello', body = cursor.link)
            print(cursor.link, "added to mq")
            self.client.db.link.delete(cursor)

    def __del__(self):
        self.connection.close()
