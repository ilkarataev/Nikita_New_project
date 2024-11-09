#!/bin/bash

# Variables
BASE_PATH="/home/graphics_api/graphics_api_project"
REMOTE="graphics-project.dds-ltd.website"
DOCKER_COMPOSE_FILE="docker-compose-prod.yaml"
DEPLOY_USER="graphics_api"

deploy() {
    rsync -avz --exclude='deploy.sh' --exclude='.env*' --exclude='README.md' --exclude='.git' --exclude='nginx_for_server' --exclude='local_mysql_data' -e 'ssh -o StrictHostKeyChecking=no' ./ ${DEPLOY_USER}@"$REMOTE:$BASE_PATH/"

     ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@$REMOTE "cd $BASE_PATH;docker-compose -f ${DOCKER_COMPOSE_FILE} up -d --build"
}

# Deploy
deploy