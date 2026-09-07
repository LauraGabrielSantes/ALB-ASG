FROM node:18-alpine AS builder

WORKDIR /app

ARG REACT_APP_API_URL=/api
ARG BACKEND_HOST=backend
ARG BACKEND_PORT=8000
ENV NODE_ENV=production
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV BACKEND_HOST=${BACKEND_HOST}
ENV BACKEND_PORT=${BACKEND_PORT}
ENV npm_config_update_notifier=false

COPY package.json ./

RUN npm install --no-audit --no-fund

COPY . .

RUN npm run build


FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

COPY --from=builder /app/build /usr/share/nginx/html

RUN mkdir -p /etc/nginx/templates
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]