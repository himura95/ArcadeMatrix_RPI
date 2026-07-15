#!/bin/bash
until docker ps >/dev/null 2>&1; do
  echo "Waiting for Docker..."
  sleep 2
done
echo "Docker is up! Running cleanup..."
docker run --privileged debian:bookworm bash -c 'apt-get update && apt-get install -y kpartx && for i in $(losetup -a | grep ArcadeMatrix_Build | awk -F: "{print \$1}"); do kpartx -d $i; losetup -d $i; done'
rm -f /tmp/ArcadeMatrix_Build*.img /workspace/ArcadeMatrix_Release.img ArcadeMatrix_Release.img
echo "Starting build..."
./scripts/build_image.sh 14G
