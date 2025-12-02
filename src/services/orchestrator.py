import threading

from src import config
from src.logger import Logosaurio
from src.modbus.modbus_driver import ModbusTcpDriver
from src.modbus.server_mb_middleware import GrdMiddlewareClient
from src.modbus.server_mb_reles import ProtectionRelayClient
from src.services.mqtt_publisher import ModbusMqttPublisher
from src.services.state_store import ObserverStateStore


class ModbusOrchestrator:
    """
    Arranca y coordina los hilos de monitoreo de GRDs y relés.
    """

    def __init__(
        self,
        logger: Logosaurio,
        mqtt_publisher: ModbusMqttPublisher,
        observer_store: ObserverStateStore,
    ):
        self.logger = logger
        self.mqtt_publisher = mqtt_publisher
        self.observer_store = observer_store
        self._threads: list[threading.Thread] = []
        self._driver: ModbusTcpDriver | None = None

    def start(self) -> None:
        self.logger.log("Instanciando driver Modbus...", origen="MW/START")
        self._driver = ModbusTcpDriver(
            host=config.MB_HOST,
            port=config.MB_PORT,
            timeout=10,
            logger=self.logger,
        )

        grd_client = GrdMiddlewareClient(
            modbus_driver=self._driver,
            default_unit_id=config.MB_ID,
            register_count=config.MB_COUNT,
            refresh_interval=config.MB_INTERVAL_SECONDS,
            logger=self.logger,
            mqtt_publisher=self.mqtt_publisher,
        )
        relay_client = ProtectionRelayClient(
            modbus_driver=self._driver,
            refresh_interval=config.MB_INTERVAL_SECONDS,
            logger=self.logger,
            observer_store=self.observer_store,
        )

        grd_thread = threading.Thread(target=grd_client.start_observer_loop, name="grd-monitor", daemon=True)
        rele_thread = threading.Thread(target=relay_client.start_monitoring_loop, name="rele-monitor", daemon=True)
        grd_thread.start()
        rele_thread.start()
        self._threads.extend([grd_thread, rele_thread])
        self.logger.log("Orquestador Modbus iniciado.", origen="MW/START")
