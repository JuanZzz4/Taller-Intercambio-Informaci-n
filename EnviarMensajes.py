import psutil
import json
import paho.mqtt.client as mqtt
import time
from datetime import datetime
import mysql.connector

# Configuración de MQTT
mqtt_broker = "broker.hivemq.com"
mqtt_port = 1883
mqtt_topic = "Taller arquitectura"

# Configuración de MySQL
mysql_host = "localhost"
mysql_user = "root"
mysql_password = "mi_contraseña"
mysql_database = "mi_base_de_datos"

def insertar_en_mysql(datos):
    connection = None  # Inicializar la variable connection
    try:
        connection = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )

        cursor = connection.cursor()

        consulta = """
            INSERT INTO mediciones (cpu, memory, bytes_enviados, bytes_recibidos, mac_address, temperature, fecha_hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(consulta, (
            datos["cpu"],
            datos["memory"],
            datos["net"]["bytes_enviados"],
            datos["net"]["bytes_recibidos"],
            datos["mac_address"],
            datos["temperature"],
            datos["date"]
        ))

        connection.commit()
        print("Datos insertados en MySQL:", datos)
    except Exception as e:
        print("Error al insertar en MySQL:", str(e))
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def enviar_metricas(client):
    cpu_percent = psutil.cpu_percent()
    mem_percent = psutil.virtual_memory().percent
    network_info = psutil.net_io_counters()
    temperatura = obtener_temperatura()

    fecha_hora_actual = datetime.now().isoformat()

    datos_json = {
        "cpu": cpu_percent,
        "memory": mem_percent,
        "net": {
            "bytes_enviados": network_info.bytes_sent,
            "bytes_recibidos": network_info.bytes_recv
        },
        "mac_address": obtener_mac_address(),
        "temperature": temperatura,
        "date": fecha_hora_actual
    }

    # Envío de datos a MQTT
    client.publish(mqtt_topic, json.dumps(datos_json))
    print("Datos enviados:", datos_json)

    # Inserción de datos en MySQL
    insertar_en_mysql(datos_json)

def obtener_temperatura():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as file:
            temperatura_raw = float(file.read()) / 1000.0
        return temperatura_raw
    except Exception as e:
        return 0

def obtener_mac_address():
    interfaz_activa = psutil.net_if_addrs().get('Ethernet', None)

    if interfaz_activa is not None:
        mac_address = interfaz_activa[0].address
        return mac_address
    else:
        return None

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código de resultado: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

client.connect(mqtt_broker, mqtt_port, 60)

client.loop_start()

try:
    while True:
        enviar_metricas(client)
        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
    print("Conexión cerrada.")
