import psutil
import speedtest
import mysql.connector

# Obtener el rendimiento del CPU
cpu_percent = psutil.cpu_percent()

# Obtener el rendimiento de la memoria
memory = psutil.virtual_memory()
memory_available = memory.available
memory_used = memory.used

# Obtener el rendimiento de la red
speed_test = speedtest.Speedtest()
download_speed = speed_test.download()
upload_speed = speed_test.upload()

# Establecer la conexión a la base de datos
connection = mysql.connector.connect(
    host="tu_host",
    user="tu_usuario",
    password="tu_contraseña",
    database="tu_base_de_datos"
)

# Crear un cursor para ejecutar las consultas
cursor = connection.cursor()

# Insertar los datos en la base de datos
insert_query = "INSERT INTO rendimiento (cpu_percent, memory_available, memory_used, download_speed, upload_speed) VALUES (%s, %s, %s, %s, %s)"
data = (cpu_percent, memory_available, memory_used, download_speed, upload_speed)

cursor.execute(insert_query, data)

# Confirmar los cambios en la base de datos
connection.commit()

# Cerrar el cursor y la conexión
cursor.close()
connection.close()

print("Datos insertados en la base de datos.")