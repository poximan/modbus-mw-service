import os


def _req(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None or not str(value).strip():
        raise EnvironmentError(f"Falta variable obligatoria: {name}")
    return str(value).strip()


# ------------------ Modbus middleware ------------------
MB_HOST = _req("MODBUS_MW_MB_HOST")
MB_PORT = int(_req("MODBUS_MW_MB_PORT"))
MB_ID = int(_req("MODBUS_MW_MB_ID"))
MB_COUNT = int(_req("MODBUS_MW_MB_COUNT"))
MB_INTERVAL_SECONDS = int(_req("MODBUS_MW_MB_INTERVAL_SECONDS"))

GRD_DESCRIPTIONS: dict[int, str] = {
    1: "SS - presuriz doradillo",
    2: "SS - pluvial prefectura",
    3: "SS - presuriz agro",
    4: "SE - CD45 Murchison",
    5: "SS - bypass EE4",
    6: "SS - pluvial lugones",
    7: "reserva",
    8: "SE - et doradillo",
    9: "reserva",
    10: "SE - rec2(O) doradillo",
    11: "SE - rec3(N) doradillo",
    12: "reserva",
    13: "SE - et soc.rural",
    14: "SS - edif estivariz GE",
    15: "SE - et juan XXIII",
    16: "reserva",
    17: "SS - pque pesquero",
}

ESCLAVOS_MB: dict[int, str] = {
    1: "NO APLICA - (SE)et soc.rural - plc",
    2: "NO APLICA - (SE)et doradillo - proteccion (no esta?)",
    3: "(SE)et doradillo - proteccion MiCOM CDA03 33KV",
    4: "NO APLICA - (SE)et doradillo - proteccion MiCOM rele cuba",
    5: "(SE)et doradillo - proteccion MiCOM CDA02 33KV",
    6: "(SE)et doradillo - proteccion MiCOM CDA03 13,2KV",
    7: "NO APLICA - (SS)presuriz doradillo - plc",
    8: "NO APLICA - (SE)et juan XXIII - proteccion janitza umg 96s",
    9: "NO APLICA - (SE)et juan XXIII - proteccion janitza umg 96s",
    10: "NO APLICA - (SE)et juan XXIII - proteccion janitza umg 96s",
    11: "NO APLICA - (SE)et juan XXIII - proteccion MiCOM p12x",
    12: "NO APLICA - (SE)et juan XXIII - proteccion MiCOM p12x",
    13: "NO APLICA - (SE)et juan XXIII - proteccion MiCOM p12x",
    14: "NO APLICA - (SE)et juan XXIII - proteccion MiCOM p12x",
}

# ------------------ Data paths ------------------
DATABASE_DIR = os.getenv("MODBUS_MW_DATA_DIR", "/app/data")
DATABASE_NAME = os.getenv("MODBUS_MW_DATABASE_NAME", "grdconectados.db")
OBS_STATE_FILE = os.path.join(DATABASE_DIR, "modbus-mw-state.json")

# ------------------ MQTT ------------------
MQTT_BROKER_HOST = _req("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(_req("MQTT_BROKER_PORT"))
MQTT_BROKER_USERNAME = _req("MQTT_BROKER_USERNAME")
MQTT_BROKER_PASSWORD = _req("MQTT_BROKER_PASSWORD")
MQTT_BROKER_USE_TLS = _req("MQTT_BROKER_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
MQTT_TLS_INSECURE = _req("MQTT_TLS_INSECURE", "false").lower() in {"1", "true", "yes", "on"}
MQTT_KEEPALIVE = int(os.getenv("MQTT_BROKER_KEEPALIVE", "60"))

MQTT_TOPIC_MODEM_CONEXION = "exemys/estado/conexion_modem"
MQTT_TOPIC_GRADO = "exemys/estado/grado"
MQTT_TOPIC_GRDS = "exemys/estado/grds"
MQTT_TOPIC_EMAIL_ESTADO = "exemys/estado/email"
MQTT_TOPIC_EMAIL_EVENT = "exemys/eventos/email"
MQTT_TOPIC_PROXMOX_ESTADO = "exemys/estado/proxmox"

MQTT_PUBLISH_QOS_STATE = 1
MQTT_PUBLISH_RETAIN_STATE = True
MQTT_PUBLISH_QOS_EVENT = 1
MQTT_PUBLISH_RETAIN_EVENT = False

HTTP_POLL_SECONDS = int(os.getenv("MODBUS_HTTP_POLL_SECONDS", "20"))
MQTT_REFRESH_FACTOR = int(os.getenv("MODBUS_MQTT_REFRESH_FACTOR", "5"))
