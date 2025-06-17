FROM postgres:latest

# Install Python and psycopg2
RUN apt update && apt install -y python3-pip

WORKDIR /usr/src/app

# COPY files
COPY /gen_s_data /usr/src/app/

# If you have requirements
RUN pip3 install --break-system-packages -r requirements.txt

# Make wrapper script executable
RUN chmod +x /usr/src/app/docker-entrypoint-wrapper.sh


ENTRYPOINT ["/usr/src/app/docker-entrypoint-wrapper.sh"]

