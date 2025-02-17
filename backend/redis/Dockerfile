FROM redis:latest

RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

# Set memory overcommit to 1
# RUN echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf && \
#     sysctl -p

EXPOSE 6379

CMD ["redis-server"]
