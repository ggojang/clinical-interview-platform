FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CLINICAL_API_HOST=0.0.0.0 \
    CLINICAL_API_PORT=8000

WORKDIR /app
COPY compiler /app/compiler
COPY fhir /app/fhir
COPY interoperability /app/interoperability
COPY knowledge /app/knowledge
COPY packages /app/packages
COPY policies /app/policies
COPY runtime /app/runtime
COPY schemas /app/schemas
COPY services /app/services

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000
CMD ["python", "-m", "services.interview_api"]
