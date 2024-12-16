FROM postgres:13-alpine

COPY ./init_database.sh init_database.sh

RUN chmod +x init_database.sh

ENTRYPOINT [ "/init_database.sh" ]

# CMD [ "executable" ]
