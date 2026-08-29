FROM node:22-alpine
WORKDIR /app
COPY app/package*.json ./
RUN npm ci
COPY app ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "127.0.0.1"]
