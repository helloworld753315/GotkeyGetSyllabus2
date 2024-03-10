FROM python:3

WORKDIR /app

RUN pip install --upgrade pip
RUN apt-get update \
    && apt-get install -y ghostscript python3-tk libgl1-mesa-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
# CMD [ "python", "app.py" ]