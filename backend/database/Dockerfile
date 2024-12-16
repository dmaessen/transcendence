FROM postgres:13-alpine

# Copy the initialization script into the container
COPY ./init_database.sh /init_database.sh

# Make the script executable
RUN chmod +x /init_database.sh

# Set the entrypoint to the init script
ENTRYPOINT [ "/init_database.sh" ]

# Default CMD to run the Django server after DB initialization
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
