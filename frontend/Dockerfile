#FRONTEND
FROM node:18-alpine AS builder

WORKDIR /app

RUN npm install -g typescript

COPY ./package.json .
COPY ./tsconfig.json .
COPY ./app.ts .

RUN tsc


#NGINX
FROM nginx:alpine


COPY index.html /usr/share/nginx/html/

COPY --from=builder /app/dist /usr/share/nginx/html/dist/

EXPOSE 80