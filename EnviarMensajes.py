import psutil
import speedtest
import paho.mqtt.publish as publish
import time

# Configuración del servidor HiveMQ
host = "broker.hivemq.com"  # Puedes cambiarlo si es necesario
topic = "rendimiento_topic"

# Funciones para obtener el rendimiento del sistema
def obtener_rendimiento_cpu():
    return psutil.cpu_percent()

def obtener_rendimiento_memoria():
    memory = psutil.virtual_memory()
    memory_available = memory.available / (1024 * 1024)  # Convertir a MB
    memory_used = memory.used / (1024 * 1024)  # Convertir a MB
    return memory_available, memory_used

def obtener_rendimiento_red():
    speed_test = speedtest.Speedtest()
    download_speed = speed_test.download() / 1e6  # Convertir a Mbps
    upload_speed = speed_test.upload() / 1e6  # Convertir a Mbps
    return download_speed, upload_speed

if __name__ == "__main__":
    while True:
        # Obtener el rendimiento del sistema
        cpu_percent = obtener_rendimiento_cpu()
        memory_available, memory_used = obtener_rendimiento_memoria()
        download_speed, upload_speed = obtener_rendimiento_red()

        # Crear un mensaje con los datos
        mensaje = f"CPU: {cpu_percent}% | Memoria disponible: {memory_available:.2f} MB | Memoria en uso: {memory_used:.2f} MB | Descarga: {download_speed:.2f} Mbps | Subida: {upload_speed:.2f} Mbps"

        # Publicar el mensaje en el tema MQTT
        publish.single(topic, mensaje, hostname=host)

        # Esperar antes de recopilar nuevamente
        time.sleep(60)  # Espera 60 segundos (puedes ajustar según tus necesidades)
