FROM python:3.9  
# Adjust Python version as needed

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip3 install -U -r requirements.txt
CMD ["bash","run.sh"]
