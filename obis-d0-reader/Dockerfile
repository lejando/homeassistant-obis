ARG BUILD_FROM
FROM $BUILD_FROM

# Python ist bereits im base-python image vorhanden

# Copy und install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

# Copy application
COPY obis_reader.py /app/obis_reader.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

WORKDIR /app

CMD [ "/run.sh" ]
