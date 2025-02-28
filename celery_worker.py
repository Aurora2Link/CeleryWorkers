from celery import Celery

if __name__ == "__main__":
    celery.worker_main(["worker", "--loglevel=info"])
