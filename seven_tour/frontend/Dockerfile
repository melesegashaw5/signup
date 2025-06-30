# Use an official Node runtime as a parent image
FROM node:18-alpine as build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package.json ./
COPY package-lock.json ./
# If you use yarn:
# COPY yarn.lock ./

# Install dependencies
RUN npm install
# If you use yarn:
# RUN yarn install --frozen-lockfile

# Copy the rest of the application code
COPY . ./

# Build the React app for production
RUN npm run build
# If you use yarn:
# RUN yarn build

# Production stage: Nginx for serving static files
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config (optional, if you need custom configuration)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
