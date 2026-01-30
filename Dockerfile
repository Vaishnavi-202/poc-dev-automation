FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Sanity check only (no UI execution)
CMD ["python", "-c", "print('POC_SMOKE Docker image built successfully')"]
