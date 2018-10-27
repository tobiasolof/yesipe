FROM python:3.6.4

WORKDIR /

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./Backend

WORKDIR /Backend/

ENTRYPOINT python3 -m app
