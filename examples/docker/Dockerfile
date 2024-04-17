# Use the official Docker Hub Postgres 10.6 image
# FROM postgres:10.6
FROM postgres:12

# Set environment variables
ENV POSTGRES_USER ""
ENV POSTGRES_PASSWORD ""
ENV POSTGRES_DB ""

# Install the necessary packages for building the extension
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    zlib1g-dev \
    postgresql-server-dev-12

# Clone the q3c extension from GitHub
RUN git clone https://github.com/segasai/q3c.git

# Build and install the q3c extension
WORKDIR /q3c
RUN make && make install

# Add a script to enable the q3c extension
RUN echo "CREATE EXTENSION q3c;" > /docker-entrypoint-initdb.d/init-q3c.sql

# Expose the PostgreSQL port
EXPOSE 5432

# Add a VOLUME to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Set the default command to run when starting the container
CMD ["postgres"]