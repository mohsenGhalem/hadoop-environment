#!/bin/bash
set -e
cd "$(dirname "$0")"

HADOOP_VERSION=3.4.3
TARBALL="hadoop-$HADOOP_VERSION.tar.gz"
MIRRORS=(
  "https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/$TARBALL"
  "https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/$TARBALL"
)

# 1. Download Hadoop once on the host (resumes if interrupted)
if ! gzip -t "$TARBALL" 2>/dev/null; then
  for url in "${MIRRORS[@]}"; do
    echo ">> Downloading $url"
    for attempt in 1 2 3 4 5; do
      if curl -fL --retry 5 --retry-delay 3 -C - -o "$TARBALL" "$url"; then break; fi
      echo "   download interrupted, resuming (attempt $attempt)..."
      sleep 3
    done
    gzip -t "$TARBALL" 2>/dev/null && break
    echo "   mirror failed, trying next one"; rm -f "$TARBALL"
  done
  gzip -t "$TARBALL" || { echo "Could not download $TARBALL"; exit 1; }
fi
echo ">> $TARBALL ready"

# 2. Network
docker network inspect hadoop_network >/dev/null 2>&1 || docker network create hadoop_network

# 3. Base image + cluster
docker build -t hadoop-base:$HADOOP_VERSION .
docker build --platform linux/amd64 -t hadoop-base:$HADOOP_VERSION-amd64 .  # for historyserver
docker compose up -d --build
docker ps
