#!/bin/bash
docker-compose -f docker/docker_compose.yml build --no-cache
docker-compose -f docker/docker_compose.yml up