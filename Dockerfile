FROM python:3.13-alpine
LABEL maintainer="volodymyr.vinohradov@gmail.com"
ENV PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT="/usr/local/"

RUN apk add --no-cache gcc musl-dev linux-headers

WORKDIR /src
COPY pyproject.toml uv.lock requirements.txt ./

# Install dependencies, sync with uv, and clean up unnecessary files
RUN pip install --no-cache-dir uv \
    && uv --no-cache-dir sync

# Copy the rest of the application code into the container
COPY . .
CMD ["sh", "-c", "alembic upgrade head && python src/db_dump_scheduler.py & python -m src.parse"]