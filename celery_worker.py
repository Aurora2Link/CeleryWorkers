from celery import Celery
import os
import redis
import json
import logging

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Redis
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Configurar Celery
celery = Celery("celery_worker", broker=REDIS_URL, backend=REDIS_URL, include=['celery_worker'])

@celery.task
def process_message(data_str):
    try:
        # Convertir la cadena JSON de vuelta a un objeto JSON
        data = json.loads(data_str)
        Phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        Message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        logger.info(f"Mensaje recibido de {Phone_number}: {Message}")
        redis_client.lpush("processed_message_queue", f"{Phone_number}:{Message}")
        logger.info("Mensaje procesado y almacenado en Redis exitosamente.")
    except Exception as e:
        logger.error(f"Error al procesar el mensaje: {str(e)}")

@celery.task
def fetch_and_process_messages():
    while True:
        _, data_str = redis_client.brpop("message_queue")
        logger.info(f"Mensaje obtenido de Redis: {data_str}")
        process_message.delay(data_str)

if __name__ == "__main__":
    celery.worker_main(["worker", "--loglevel=info"])
