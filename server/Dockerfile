# syntax=docker/dockerfile:1.7
# Hunter Realms game server: Canary (pinned) + our datapack and generated assets.
# Build from the repo root:  docker build -f server/Dockerfile -t hunterrealms-server .

# ---- 1. generate assets, items.xml and the world map from source ----
FROM python:3.12-slim AS gen
RUN pip install --no-cache-dir grpcio-tools==1.66.2 pillow==10.4.0
WORKDIR /src
COPY tools tools
COPY assets assets
COPY server/data-hunterrealms server/data-hunterrealms
RUN tools/build_all.sh - /gen

# ---- 2. compile the Canary engine at the pinned commit ----
FROM ubuntu:24.04 AS build
ARG DEBIAN_FRONTEND=noninteractive
ARG CANARY_REPO=https://github.com/opentibiabr/canary.git
ARG CANARY_COMMIT=09fde48ffa9afaf5c424bde460ec0c4c7c734e51
RUN apt-get update && apt-get install -y --no-install-recommends \
      cmake git unzip build-essential ca-certificates curl zip tar pkg-config \
      ninja-build autoconf automake libtool python3 \
    && rm -rf /var/lib/apt/lists/*
RUN git clone "$CANARY_REPO" /canary && cd /canary && git checkout "$CANARY_COMMIT"
RUN baseline=$(grep '"builtin-baseline"' /canary/vcpkg.json | cut -d'"' -f4) \
    && git clone https://github.com/microsoft/vcpkg.git /opt/vcpkg \
    && cd /opt/vcpkg && git checkout "$baseline" && ./bootstrap-vcpkg.sh -disableMetrics
ENV VCPKG_ROOT=/opt/vcpkg
WORKDIR /canary
RUN --mount=type=cache,target=/root/.cache/vcpkg \
    cmake --preset linux-release -DTOGGLE_BIN_FOLDER=ON && cmake --build --preset linux-release

# ---- 3. runtime ----
FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends mariadb-client ca-certificates tzdata \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /srv/hunterrealms
COPY --from=build /canary/build/linux-release/bin/canary ./canary
COPY --from=build /canary/data ./data
COPY --from=build /canary/schema.sql /canary/key.pem ./
COPY server/core-overrides/ ./data/
COPY server/data-hunterrealms ./data-hunterrealms
COPY --from=gen /src/server/data-hunterrealms/monster ./data-hunterrealms/monster
COPY --from=gen /gen/assets/appearances.dat ./data/items/appearances.dat
COPY --from=gen /gen/items.xml ./data/items/items.xml
COPY --from=gen /gen/world/ ./data-hunterrealms/world/
COPY server/config.lua ./config.lua
COPY server/sql ./sql
COPY --chmod=755 server/docker-entrypoint.sh ./docker-entrypoint.sh
RUN useradd -r -u 1001 hunter && chown -R hunter /srv/hunterrealms
USER hunter
EXPOSE 7171 7172
ENTRYPOINT ["./docker-entrypoint.sh"]
