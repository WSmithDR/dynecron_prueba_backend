#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to get container IP
get_container_ip() {
    local container_name=$1
    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $container_name 2>/dev/null
}

# Function to get container port mapping
get_container_port() {
    local container_name=$1
    docker inspect -f '{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} -> {{(index $conf 0).HostPort}}{{end}}' $container_name 2>/dev/null
}

# 🧹 Stop any orphan containers from previous runs
echo -e "${BLUE}🧹 Cleaning up orphan containers (if any)...${NC}"
docker compose -f docker-compose.yml down --remove-orphans

# 🚀 Build and start the Backend service in detached mode
echo -e "${BLUE}🚀 Starting Dynecron Backend...${NC}"
docker compose -f docker-compose.yml up -d --build

# Wait for service to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
sleep 3

# Get container information
BACKEND_IP=$(get_container_ip dynecron_prueba_backend)
BACKEND_PORT=$(get_container_port dynecron_prueba_backend)

# Display service information
echo -e "\n${BLUE}📡 Service Information:${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
echo -e "${GREEN}🌐 Backend API:${NC}"
echo -e "   • Container: dynecron_prueba_backend"
echo -e "   • IP: ${BACKEND_IP}"
echo -e "   • Port: ${BACKEND_PORT}"
echo -e "   • URL: http://localhost:8000"
echo -e "   • Docs: http://localhost:8000/docs"
echo -e "${BLUE}----------------------------------------${NC}"

# Check if service is running
if docker ps | grep -q dynecron_prueba_backend; then
    echo -e "\n${GREEN}✅ Backend is running successfully!${NC}"
    echo -e "\n${YELLOW}📋 Showing logs (Ctrl+C to stop)...${NC}"
    docker compose -f docker-compose.yml logs -f
else
    echo -e "\n${RED}❌ Failed to start backend. Check logs with: docker compose -f docker-compose.yml logs${NC}"
fi
