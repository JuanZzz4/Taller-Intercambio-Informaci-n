import paho.mqtt.client as mqtt

# Configuración del servidor MQTT
broker_address = "broker.hivemq.com"
port = 1883
topic = "Taller MQTT en grupo"  # Reemplazar con el tema que deseas usar

# Crear un cliente MQTT
client = mqtt.Client()

# Conectar al broker MQTT
client.connect(broker_address, port, 60)

# Publicar mensajes en el tema
while True:
    message = input("Ingresa el mensaje a enviar: ")
    client.publish(topic, message)