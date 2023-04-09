import threading
import time
from datetime import datetime
import logging

import paho.mqtt.client as mqtt


class MQTTListener(threading.Thread):
    def __init__(self, host, port, topics, mailboxes):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.client = None
        self._host = host
        self._port = port
        self._topics = topics
        self._mailboxes = mailboxes

    @property
    def host(self):
        """The MQTT broker host"""
        return self._host

    @property
    def port(self):
        """The MQTT broker port"""
        return self._port

    @property
    def topics(self):
        """
        The list of MQTT topics to subscribe to. Should be a list of strings
        """
        return self._topics

    @property
    def mailboxes(self):
        """
        A dictionary of topics to mailboxes. Each key in mailboxes should be in topics
        """
        return self._mailboxes

    def match_topic(self, topic):
        """
        The main handler function.
        Matches a topic and returns a mailbox
        """
        pass


    def on_connect(self, client, userdata, flags, rc):
        """
        callback for the MQTT client to execute on connect
        """
        topics = userdata['topics']
        for topic in topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        """
        callback for the MQTT client on message
        The main message handler.
        """
        topic = str(msg.topic)
        self.log.debug(f"{__name__}: [on_message] Topic: {topic}")
        match topic:
            case "toy/exit":
                self.log.info(f"{__name__}: [on_message] Shutting down MQTT client.")
                self.stop()
            case "toy/log":
                self.log_message(msg)
            case "toy/synth/test/command":
                if topic in self.mailboxes:
                    self.mailboxes[topic].put(MQTTListener.decode_payload(msg))
            case _:
                self.log.debug(f"{__name__}: [on_message] Matched default case.")
                self.log_message(msg)

    @staticmethod
    def decode_payload(msg):
        return str(msg.payload.decode("utf-8"))

    def log_message(self, msg):
        """
        message should have topic and payload
        """
        decoded_message = str(msg.payload.decode("utf-8"))
        ts = time.time()
        time_str = datetime.fromtimestamp(ts)
        self.log.info(f"{__name__} - {time_str}:\nTopic: {msg.topic}\nPayload: {decoded_message}")

    def stop(self):
        """
        Close the MQTT client and exit the program
        """
        self.client.disconnect()
        self.client.loop_stop()

    def run(self):
        """
        Overrides threading.Thread.run
        """
        self.log.info(f"{__name__}: [run] Initiating MQTT listener with host: {self.host}, port: {self.port}")

        self.client = mqtt.Client()
        self.client.user_data_set({'topics': self.topics})
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.host, self.port, 60)

        self.client.loop_start()
