FROM adoptopenjdk/openjdk11:debian-jre
VOLUME /tmp
ARG JAR_FILE=build/libs/MA_environment-0.0.1-SNAPSHOT.jar
COPY ${JAR_FILE} app.jar
# COPY additional/jolokia-jvm-1.7.2.jar jolokia-jvm-agent.jar
# ENTRYPOINT ["java", "-javaagent:jolokia-jvm-agent.jar=host=0.0.0.0", "-jar", "/app.jar"]
ENTRYPOINT sh -c "sleep 30; java -jar /app.jar"
