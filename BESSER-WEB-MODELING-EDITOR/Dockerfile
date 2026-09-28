FROM node:20-alpine

RUN apk add --no-cache \
    build-base \
    g++ \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    giflib-dev

WORKDIR /app

ENV DEPLOYMENT_URL="http://localhost:8080"
ENV BACKEND_URL="http://localhost:9000/besser_api"
ENV APOLLON_REDIS_URL=""

COPY . .

RUN npm install
RUN npm run build:webapp:local
RUN npm run build:server

EXPOSE 8080 9000

CMD ["npm", "run", "start"]
