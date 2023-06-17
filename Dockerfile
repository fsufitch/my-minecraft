FROM fedora:38 AS minecraft

WORKDIR /opt/minecraft

RUN dnf install -y java-latest-openjdk

ADD https://piston-data.mojang.com/v1/objects/84194a2f286ef7c14ed7ce0090dba59902951553/server.jar minecraft-server.jar

COPY start.sh server.properties ./
RUN chmod +x start.sh

VOLUME [ "/opt/minecraft-runtime" ]

ENTRYPOINT [ "./start.sh" ]
CMD [ "nogui" ]