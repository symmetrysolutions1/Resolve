FROM python:3.12-slim

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "-m", "resolve_scout"]
CMD ["demo"]
