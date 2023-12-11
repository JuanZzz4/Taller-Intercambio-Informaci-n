import paho.mqtt.client as mqtt
import threading
import time
import psutil
import platform
import smtplib
from email.mime.text import MIMEText

# Crear un bloqueo para la sincronización de la salida
print_lock = threading.Lock()

# Configuración para enviar el correo
correo_emisor = 'estadocpu@gmail.com'
contrasena_emisor = 'dcxz bpqx nrms lcig'
correo_destino = 'juanman042023@gmail.com'

def enviar_correo(asunto, mensaje):
    mensaje_correo = MIMEText(mensaje)
    mensaje_correo['Subject'] = asunto
    mensaje_correo['From'] = correo_emisor
    mensaje_correo['To'] = correo_destino

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor_smtp:
            servidor_smtp.login(correo_emisor, contrasena_emisor)
            servidor_smtp.sendmail(correo_emisor, correo_destino, mensaje_correo.as_string())

        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")


def on_connect(client, userdata, flags, rc):
    with print_lock:
        print(f"Conectado con código de resultado {rc}")
    client.subscribe("metadatos")

def on_message(client, userdata, msg):
    with print_lock:
        print(f"Mensaje recibido: {msg.payload.decode()}")

def recibir_mensajes(client):
    while True:
        time.sleep(1)  # Añade un pequeño retardo para evitar que bloquee completamente el programa
        client.loop()

def obtener_rendimiento_cpu():
    return psutil.cpu_percent(interval=1)

def obtener_rendimiento_memoria():
    return psutil.virtual_memory().percent

def obtener_rendimiento_red():
    sent_before, recv_before = psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv
    psutil.cpu_percent(interval=1)  # Actualiza las métricas mientras esperamos
    sent_after, recv_after = psutil.net_io_counters().bytes_sent, psutil.net_io_counters().bytes_recv

    # Calcular la tasa de transferencia en bytes por segundo
    tasa_envio = sent_after - sent_before
    tasa_recibo = recv_after - recv_before

    return tasa_envio, tasa_recibo

def obtener_sistema_operativo():
    return platform.system()

def monitorear_uso_cpu():
    while True:
        porcentaje_cpu = obtener_rendimiento_cpu()
        with print_lock:
            print(f'Uso actual de CPU: {porcentaje_cpu}%')

        if porcentaje_cpu > 10:
            enviar_correo('Alerta de Uso de CPU', f'El uso del CPU ha excedido el 40% ({porcentaje_cpu}%)')

        time.sleep(60)  # Verificar cada 1 minuto

if __name__ == "__main__":
    # Configuración del cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)  # Cambia por tu broker o utiliza un broker local

    # Inicia un hilo para la recepción de mensajes MQTT
    mqtt_thread = threading.Thread(target=recibir_mensajes, args=(client,))
    mqtt_thread.start()

    # Inicia un hilo para monitorear el uso de la CPU
    cpu_monitor_thread = threading.Thread(target=monitorear_uso_cpu)
    cpu_monitor_thread.start()

    try:
        while True:
            input("Presiona Enter para obtener información del sistema:")
            porcentaje_memoria = obtener_rendimiento_cpu()
            rendimiento_memoria = obtener_rendimiento_memoria()
            tasa_envio_local, tasa_recibo_local = obtener_rendimiento_red()
            sistema_operativo = obtener_sistema_operativo()

            mensaje = f"Rendimiento CPU (%): {porcentaje_memoria}%\n" \
                      f"Rendimiento de memoria: {rendimiento_memoria}%\n" \
                      f"Tasa de Transferencia - Enviados (bytes/segundo): {tasa_envio_local}\n"\
                      f"Tasa de Transferencia - Recibidos (bytes/segundo): {tasa_recibo_local}\n" \
                      f"Sistema Operativo: {sistema_operativo}"

            client.publish("metadatos", mensaje)
    except KeyboardInterrupt:
        # Desconectar al recibir una interrupción del teclado (Ctrl+C)
        client.disconnect()
        client.loop_stop()
        mqtt_thread.join()  # Espera a que el hilo de MQTT termine
        cpu_monitor_thread.join()  # Espera a que el hilo de monitoreo
