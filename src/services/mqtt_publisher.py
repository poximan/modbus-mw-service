import json
import threading
from typing import Any

import paho.mqtt.client as mqtt

from src import config
from src.logger import Logosaurio


class ModbusMqttPublisher:
    """
    Publicador MQTT dedicado para snapshots de GRDs/modem.
    Mantiene una unica instancia de paho-mqtt con reconexion automatica.
    """

    def __init__(self, logger: Logosaurio):
        self.log = logger
        self._lock = threading.RLock()
        self._client: mqtt.Client | None = None
        self._connect()

    def _connect(self) -> None:
        with self._lock:
            if self._client is not None:
                return
            client = mqtt.Client(clean_session=True)
            client.username_pw_set(config.MQTT_BROKER_USERNAME, config.MQTT_BROKER_PASSWORD)
            if config.MQTT_BROKER_USE_TLS:
                client.tls_set()
                client.tls_insecure_set(config.MQTT_TLS_INSECURE)
            client.connect(
                config.MQTT_BROKER_HOST,
                config.MQTT_BROKER_PORT,
                keepalive=config.MQTT_KEEPALIVE,
            )
            client.loop_start()
            self._client = client
            self.log.log("MQTT publisher conectado.", origen="MW/MQTT")

    def _publish(self, topic: str, payload: Any, qos: int, retain: bool) -> None:
        body = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        with self._lock:
            if self._client is None:
                self._connect()
            client = self._client
        try:
            info = client.publish(topic, payload=body, qos=qos, retain=retain)
            info.wait_for_publish()
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT rc={info.rc}")
        except Exception as exc:
            self.log.log(f"Error publicando en {topic}: {exc}", origen="MW/MQTT")
            with self._lock:
                try:
                    client.loop_stop()
                except Exception:
                    pass
                try:
                    client.disconnect()
                except Exception:
                    pass
                self._client = None

    def publish_grado(self, payload: dict) -> None:
        self._publish(
            config.MQTT_TOPIC_GRADO,
            payload,
            qos=config.MQTT_PUBLISH_QOS_STATE,
            retain=config.MQTT_PUBLISH_RETAIN_STATE,
        )

    def publish_grds(self, payload: dict) -> None:
        self._publish(
            config.MQTT_TOPIC_GRDS,
            payload,
            qos=config.MQTT_PUBLISH_QOS_STATE,
            retain=config.MQTT_PUBLISH_RETAIN_STATE,
        )
