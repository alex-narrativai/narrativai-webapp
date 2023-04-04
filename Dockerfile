# app/Dockerfile

FROM python:3.11-bullseye

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        netbase \
        build-essential \
        curl \
        software-properties-common \
        && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8501

CMD streamlit run NarrativAI_Dashboard.py