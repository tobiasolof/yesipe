FROM python:3.6.4

WORKDIR /

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . ./Backend

ENTRYPOINT python3 -m Backend.backend
