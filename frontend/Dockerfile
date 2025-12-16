# Fase 1: Build (usa Node per compilare React)
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Fase 2: Serve (usa Nginx per mostrare il sito)
FROM nginx:alpine
# Copia i file compilati dalla fase 1 alla cartella di Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Espone la porta 80
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]