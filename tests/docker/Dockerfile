# PostgreSQL image with the Q3C extension pre-installed. Building this once
# and reusing the image is much faster than the CI approach of installing
# q3c into a freshly-started container every run.
#
# q3c is built from an upstream tag rather than installed from the PGDG apt
# repository: the apt package is unpinned and tracks the latest release, so
# it silently drifts away from the version production runs. Keep the default
# equal to production; override with `--build-arg Q3C_VERSION=...` (or the
# Q3C_VERSION environment variable when going through docker compose).
ARG Q3C_VERSION=2.0.1

FROM postgres:16 AS q3c-build
ARG Q3C_VERSION
# q3c 2.0.1's Makefile links its `prepare` helper against PostgreSQL's full
# $(LIBS), hence the -dev libraries (2.0.6 no longer needs them).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential ca-certificates curl postgresql-server-dev-16 \
        liblz4-dev libreadline-dev libzstd-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL "https://github.com/segasai/q3c/archive/refs/tags/v${Q3C_VERSION}.tar.gz" \
        | tar xz -C /tmp \
    && make -C "/tmp/q3c-${Q3C_VERSION}" \
    && make -C "/tmp/q3c-${Q3C_VERSION}" install DESTDIR=/q3c-install

FROM postgres:16
COPY --from=q3c-build /q3c-install/ /
