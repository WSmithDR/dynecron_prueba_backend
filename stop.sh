#!/bin/bash

# Colors
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Stop and remove the containers and their associated networks
echo -e "${GREEN}Stopping and cleaning up Dynecron Backend services...${NC}"
docker compose -f docker-compose.yml down

echo -e "${GREEN}✅ Dynecron Backend services have been stopped and cleaned up.${NC}"
