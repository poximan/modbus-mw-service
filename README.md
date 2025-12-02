# Modbus MW Service

Servicio FastAPI que actúa como middleware entre los observadores de GRDs, la base de datos SQLite embebida y el broker MQTT normalizado. Su objetivo es centralizar la captura de telemetría (estado connected/disconnected y fallas de relés), persistir historiales y publicar snapshots de disponibilidad para los demás componentes de `monimonitor`.

## Componentes principales

| Carpeta / Archivo | Descripción |
| --- | --- |
| `src/app.py` | Define la API REST (healthcheck, descripciones de GRD, historiales semanales/mensuales, fallas de relés y toggles de observer). En `startup` inicializa el esquema, arranca el `ModbusOrchestrator` y prepara el `ModbusMqttPublisher`. |
| `src/config.py` | Variables de entorno requeridas: parámetros Modbus (host, unit id, interval), rutas de datos (`DATABASE_DIR`, archivos configurables) y credenciales MQTT. Cada despliegue debe proporcionar estos valores antes de iniciar el servicio. |
| `src/persistencia` | DAO y helpers de SQLite. Gestionan tablas `grd`, `historicos`, `reles`, `fallas_reles` y `mensajes_enviados`. La clase `HistoricosDAO` expone métodos para insertar lecturas, obtener estados más recientes y calcular series semanales/mensuales. |
| `src/modbus` | Cliente orientado a GRDs (`server_mb_middleware.py`) que lee registros mediante `pymodbus`, compara contra lo persistido y dispara publicaciones MQTT cuando detecta cambios. |
| `src/services` | Lógica de alto nivel: `ModbusOrchestrator` controla los loops de sondeo, `ModbusMqttPublisher` normaliza las cargas útiles (`grado`, `grds`, estados de email/Proxmox) y `state_store` maneja flags como la activación del observer de relés. |
| `src/utils` | Utilidades compartidas. Destaca `timebox.py`, que centraliza el manejo de fechas (UTC/local) mediante `timeauthority`. |
| `Dockerfile` | Imagen ligera basada en Python 3.12. Copia `src/`, instala `requirements.txt` y expone el servicio en `8084`. |

## Flujo general
1. **Arranque**: `app.py` crea/valida el esquema SQLite, asegura catálogos y lanza los hilos de orquestación + publicación.
2. **Lectura Modbus**: `ModbusOrchestrator` usa `server_mb_middleware` para barrer cada GRD, comparar con el último estado en DB y persistir solo cuando hay cambios.
3. **Persistencia e historiales**: Los DAOs guardan timestamps normalizados y exponen consultas agregadas (últimos estados, semanas disponibles, meses disponibles) para los endpoints `GET /api/grd/history` y `GET /api/grd/summary`.
4. **Publicaciones MQTT**: `ModbusMqttPublisher` publica `exemys/estado/grado`, `exemys/estado/grds`, `exemys/eventos/email`, etc., siguiendo los topicos normalizados consumidos por Panelexemys y Panelito.
5. **API REST**: FastAPI sirve a `charito-service`/otros clientes internos con historiales y toggles de observer de relés, sin exponer datos sensibles (las credenciales y endpoints se toman siempre de variables de entorno).

> Nota: asegúrate de montar el volumen de `DATABASE_DIR` y de inyectar correctamente las credenciales MQTT/Modbus en producción. Sin esos valores el servicio fallará al iniciar (contrato estricto). También es recomendable rotar el archivo `charito-state.json` (persistido por `charito-service`) cuando se agregan nuevos hosts para evitar mostrar alias obsoletos.
