FROM python:3.9-alpine AS builder
ENV NAMESPACES_FILE=""
ENV OUTPUT_DIR="out"

WORKDIR /app

COPY requirements.txt .
COPY artifactorynamespaces ./artifactorynamespaces
COPY bin ./bin

RUN apk add --no-cache build-base libffi-dev openssl-dev && \
    pip install -r requirements.txt && \
    pip install pyinstaller &&\
    pyinstaller artifactorynamespaces/main.py --onefile


FROM alpine:3.15

COPY --from=builder /app/dist/main /app/main

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

USER appuser

ENTRYPOINT ["/app/main"]
CMD [ "-h" ]