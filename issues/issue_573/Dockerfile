FROM postgres:11.17-bullseye

# Move PGDATA to new location so it is not cached on volume
# Allows modification during build.
ENV PGDATA /var/lib/postgresql/novolume/data

# Install wal2json for replication stream consumer
RUN apt-get update && apt-get install git build-essential postgresql-server-dev-11 -y
RUN git clone https://github.com/eulerto/wal2json.git
WORKDIR wal2json
USER root
RUN PATH=/usr/bin/pg_config:$PATH
RUN USE_PGXS=1 make && USE_PGXS=1 make install

COPY schema.sql /docker-entrypoint-initdb.d/schema.sql

# This is only for testing use!
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=issue_573_db

WORKDIR /usr/local/bin
# Load schema at build time rather than image start time
# Remove the lines that start the DB from the script so build does not hang
RUN cp docker-entrypoint.sh docker-entrypoint.sh.old && \
    sed -i '/exec gosu postgres "$@"/ d' docker-entrypoint.sh && \
    sed -i '/exec "$@"/ d' docker-entrypoint.sh && \
    ./docker-entrypoint.sh postgres && \
    mv docker-entrypoint.sh.old docker-entrypoint.sh

# Configuration enables replication
ADD docker_db_configuration/* ${PGDATA}/
