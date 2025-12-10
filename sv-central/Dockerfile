# ---- Etapa 1: Build ----
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package.json y lock para instalar dependencias primero
COPY package*.json ./

# Instalar TODAS las dependencias (incluye devDependencies para compilar)
RUN npm install

# Copiar el resto del proyecto
COPY . .

# Compilar el proyecto (dist/)
RUN npm run build


# ---- Etapa 2: Runtime ----
FROM node:18-alpine

WORKDIR /app

# Copiar solo lo necesario para correr la app
COPY package*.json ./

# Instalar solo dependencias de producción
RUN npm install --only=production

# Copiar el build ya compilado
COPY --from=builder /app/dist ./dist

# Exponer puerto
EXPOSE 4001

# Comando de arranque
CMD ["npm","run", "start:prod"]
