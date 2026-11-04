FROM python:3.12-slim

# Create an unprivileged execution user
RUN groupadd --gid 10001 sandbox && \
    useradd \
        --uid 10001 \
        --gid 10001 \
        --no-create-home \
        --shell /usr/sbin/nologin \
        sandbox

# Configure Python for predictable execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONNOUSERSITE=1 \
    HOME=/tmp

# Create a non-writable working directory
WORKDIR /workspace

# Never execute generated code as root
USER 10001:10001

# Read Python source from standard input
ENTRYPOINT ["python", "-I", "-S", "-"]
