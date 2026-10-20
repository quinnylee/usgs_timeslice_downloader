FROM python:3.11-slim

WORKDIR /app

COPY . /app
RUN mkdir -p usgs_timeslices

RUN pip install -e .

ENTRYPOINT ["python", "scripts/download_timeslices.py"]