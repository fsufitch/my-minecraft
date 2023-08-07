FROM fedora:38 AS minecraft

RUN dnf install -y git java-latest-openjdk

# Build Spigot
WORKDIR /opt/spigot-build

RUN curl -o BuildTools.jar "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar" 
RUN java -jar BuildTools.jar

# Put Spigot in the right place, and clean up the build dir
WORKDIR /opt/minecraft
RUN mv -v /opt/spigot-build/spigot-*.jar . && \
    rm -rf /opt/spigot-build

# Copy and configure the remaining files
COPY container_entrypoint.sh server.properties ./
RUN chmod +x container_entrypoint.sh

# Configure runtime options
VOLUME [ "/opt/minecraft-runtime" ]
CMD [ "./container_entrypoint.sh", "nogui" ]
