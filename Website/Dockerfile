FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && groupadd --system techverse \
    && useradd --system --gid techverse --home-dir /app techverse \
    && mkdir -p /var/lib/techverse \
    && chown techverse:techverse /var/lib/techverse
COPY --chown=techverse:techverse . .
ENV TECHVERSE_INSTANCE_DIR=/var/lib/techverse \
    HOST=0.0.0.0 \
    PORT=5000
USER techverse
EXPOSE 5000
CMD ["python", "run.py"]
