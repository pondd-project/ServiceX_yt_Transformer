FROM ubuntu:18.04

WORKDIR /tmp/servicex/

RUN apt-get update && \
    apt-get install --reinstall -y build-essential \
    -y mpich \
    -y python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Turn this on so that stdout isn't buffered - otherwise logs in kubectl don't
# show up until much later!
ENV PYTHONUNBUFFERED=1

# Copy over the source
COPY transform_data.py .

ENV PYTHONPATH "${PYTHONPATH}:/tmp/servicex"
