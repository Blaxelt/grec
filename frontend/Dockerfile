FROM node:24-alpine AS builder

WORKDIR /app

COPY ./frontend/package.json ./frontend/package-lock.json .

RUN npm ci

COPY ./frontend/ .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]