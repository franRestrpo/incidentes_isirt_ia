# Etapa de construcción (Build Stage)
FROM node:20 AS build

WORKDIR /app

# Copiar package.json
COPY package.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código de la aplicación
COPY . .

# Construir la aplicación para producción
RUN npm run build

# Etapa de producción (Production Stage)
FROM nginx:alpine

# Copiar los archivos estáticos construidos desde la etapa de construcción
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar la configuración de Nginx (si tienes una personalizada)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
