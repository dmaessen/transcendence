FROM python:3.11-bookworm

WORKDIR /app

COPY ./requirements.txt /app/
COPY ./entrypoint.sh /app/

RUN ls -l /app

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

RUN pip install -r requirements.txt

#ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# The host machine makes a request to localhost:8000.
# Docker intercepts that request and forwards it to the container on port 8000.
    #because we mapped host machine's port 8000 to container's 8000 in docker-compose
# The container is listening on 0.0.0.0:8000, so it handles the request and serves the response.