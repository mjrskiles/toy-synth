import paho.mqtt.client as mqtt
import threading

class MQTTListener(threading.Thread):
    def __init__(self, host, port, topics, mailboxes):
        super().__init__()
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
        decoded_message = str(msg.payload.decode("utf-8"))
        print(f"{__name__}: {msg.topic}\n{decoded_message}")

    def run(self):
        """
        Overrides threading.Thread.run
        """
        print(f"{__name__}: [run] Initiating MQTT listener with host: {self.host}, port: {self.port}")

        client = mqtt.Client()
        client.user_data_set({'topics': self.topics})
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.host, self.port, 60)

        client.loop_forever()
