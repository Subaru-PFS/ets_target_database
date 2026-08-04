# PostgreSQL image with the Q3C extension pre-installed, mirroring the
# packages installed on-the-fly in .github/workflows/test_database.yml.
# Building this once and reusing the image is much faster than the CI
# approach of installing q3c into a freshly-started container every run.
FROM postgres:16

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-16-q3c \
    && rm -rf /var/lib/apt/lists/*
