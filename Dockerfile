FROM fedora:38 AS minecraft

RUN dnf install -y git java-latest-openjdk

RUN curl -o paper.jar "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/462/downloads/paper-1.20.4-462.jar"

# Copy and configure the remaining files
COPY container_entrypoint.sh server.properties ./
RUN chmod +x container_entrypoint.sh

# Configure runtime options
VOLUME [ "/opt/minecraft-runtime" ]
CMD [ "./container_entrypoint.sh", "nogui" ]
