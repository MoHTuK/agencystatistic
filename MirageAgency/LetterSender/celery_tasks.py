from MirageAgency.celery import app


@app.task
def get_online_id(a, b):
    return a+b
