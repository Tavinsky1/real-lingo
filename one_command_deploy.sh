#!/bin/bash
# One-command deployment for LingoWorld
# Run this single command on your server after uploading the tar.gz file

cd /var/www && \
tar -xzf /tmp/lingo_deployment_final.tar.gz && \
cd lingo_project && \
chmod +x quick_deploy.sh && \
./quick_deploy.sh
