from celery import Celery
import os
import redis
import json
import time

# Configurar Redis
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Configurar Celery
celery = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def process_message(data_str):
    try:
        # Convertir la cadena JSON de vuelta a un objeto JSON
        data = json.loads(data_str)
        Phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        Message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        print(f"Mensaje recibido de {Phone_number}: {Message}")
        redis_client.lpush("processed_message_queue", f"{Phone_number}:{Message}")
        print("Mensaje procesado y almacenado en Redis exitosamente.")
    except Exception as e:
        print(f"Error al procesar el mensaje: {str(e)}")

def fetch_and_process_messages():
    while True:
        _, data_str = redis_client.brpop("message_queue")
        process_message.delay(data_str)
        time.sleep(1)  # Evitar sobrecargar el worker

if __name__ == "__main__":
    fetch_and_process_messages()
