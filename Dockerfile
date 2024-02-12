ARG BUILD_FROM
FROM $BUILD_FROM
ENV VIRTUAL_ENV=/opt/venv
# Install requirements for add-on
RUN apk add python3 py3-pip
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH=$VIRTUAL_ENV/bin:$PATH
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
RUN python -m pip install enviroplus
RUN python -m pip install psutil
COPY enviro2mqtt.py .
CMD ["python", "enviro2mqtt.py"]

