FROM postgres:13-alpine

#install python 
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN pip3 install --no-cache --upgrade pip setuptools

# Copy the initialization script and wait-for-it
COPY ./init_database.sh /init_database.sh
# COPY ./wait_for.sh /wait_for.sh

# Set the entrypoint to wait for PostgreSQL and then run the init script
ENTRYPOINT ["sh", "/init_database.sh"]
