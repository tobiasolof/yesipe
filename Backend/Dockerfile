FROM python:3.6.4

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./data/blacklist.txt ./data/
COPY ./data/master_df.pkl ./data/
COPY ./data/freq_df.pkl ./data/
COPY ./models/ingr2vec.pkl ./models/

COPY ./nn_utils.py ./
COPY ./app.py ./

ENTRYPOINT python3 -m app
