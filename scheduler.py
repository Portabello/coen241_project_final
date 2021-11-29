from pymongo import MongoClient
import pika
from urllib.parse import urlparse

class scheduler:
    def __init__(self, mongoURL, rabbitURL):
        self.client = MongoClient(host=[mongoURL], serverSelectionTimeoutMS = 3000)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
        self.channel = connection.channel()
        self.domains = set(["www.cnn.com"])
        for domain in self.domains:
            self.channel.queue_declare(queue=domain)
    def scan(self):
        cursors = self.client.links.links.find()
        for cursor in cursors:
            if self.client.links.visited.find_one({'_id': cursor.link}):
                self.client.links.links.delete(cursor)
                continue
            self.client.links.visited.insertOne({'_id': cursor.link})
            domain = urlparse(cursor.link).netloc
            if domain not in self.domains:
                continue
            self.channel.basic_publish(exchange='', routing_key=domain, body = cursor.link)
            print(cursor.link, "added to mq")
            self.client.links.links.delete(cursor)

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    s = scheduler("172.17.0.2", "172.17.0.3")
    while(True):
        s.scan()
        sleep(20)
