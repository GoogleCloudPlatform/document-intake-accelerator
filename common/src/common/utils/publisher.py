""" Publishes the messages to pubsub """

import json
from google.cloud import pubsub_v1
from common.config import PROJECT_ID, TOPIC_ID

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def publish_document(message_dict):
  # print("inside publisher")
  message_json = json.dumps(message_dict)
  message_json = message_json.encode("utf-8")
  future = publisher.publish(topic_path, message_json)
  return future.result()

