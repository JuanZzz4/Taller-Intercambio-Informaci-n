import paho.mqtt.client as mqtt

# Configuración del servidor HiveMQ
host = "broker.hivemq.com"  # Puedes cambiarlo si es necesario
topic = "rendimiento_topic"

def on_connect(client, userdata, flags, rc):
    print(f"Conectado con resultado: {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"Mensaje recibido: {msg.payload.decode()}")

if __name__ == "__main__":
    # Inicializar el cliente MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Conectar al servidor MQTT
    client.connect(host, 1883, 60)

    # Iniciar el bucle para mantener la conexión activa
    client.loop_forever()