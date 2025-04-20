import paho.mqtt.client as mqtt
import argparse
import time
import ctypes
import os

# Configuración fija del broker y topic
MQTT_BROKER = "192.168.50.141"
MQTT_PORT = 1883
MQTT_TOPIC = "casa/marcos/ordenador/apagar"

# Argumentos por línea de comandos
parser = argparse.ArgumentParser(description="Cliente MQTT con reconexión y autenticación.")
parser.add_argument("--usuario", required=True, help="Usuario MQTT")
parser.add_argument("--password", required=True, help="Contraseña MQTT")
args = parser.parse_args()

# Variables de estado
ultimo_estado = None
mensaje_inicial_recibido = False




def show_alert(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Alerta", 0x40 | 0x1)

def manejar_cambio_estado(nuevo_estado):
    print(f"Estado cambiado a: {nuevo_estado}")

    if (nuevo_estado=="on"):
        show_alert("El sistema se apagará en 2 minutos. Guarda tu trabajo.")
        time.sleep(120)
        os.system("shutdown /s /t 0")        

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado correctamente al broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Fallo al conectar. Código de error: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"Desconectado del broker. Código: {rc}. Intentando reconectar...")
    while True:
        try:
            client.reconnect()
            break
        except:
            print("Reintento de conexión fallido. Esperando 5 segundos...")
            time.sleep(5)

def on_message(client, userdata, msg):
    global ultimo_estado, mensaje_inicial_recibido
    nuevo_estado = msg.payload.decode()

    if not mensaje_inicial_recibido:
        manejar_cambio_estado(nuevo_estado)
        ultimo_estado = nuevo_estado
        mensaje_inicial_recibido = True
    elif nuevo_estado != ultimo_estado:
        manejar_cambio_estado(nuevo_estado)
        ultimo_estado = nuevo_estado

# Cliente MQTT
client = mqtt.Client()
client.username_pw_set(args.usuario, args.password)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"No se pudo conectar inicialmente: {e}")
    exit(1)

print(f"Escuchando el topic '{MQTT_TOPIC}' en {MQTT_BROKER}:{MQTT_PORT}...")

client.loop_forever()
