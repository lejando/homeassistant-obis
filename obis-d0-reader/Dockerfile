ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy data
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy application
COPY obis_reader.py /app/
COPY run.sh /
RUN chmod a+x /run.sh

WORKDIR /app

CMD [ "/run.sh" ]
