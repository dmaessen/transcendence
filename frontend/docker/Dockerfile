FROM node:18-buster

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (if present)
COPY package*.json ./

# Install dependencies (if you have any)
RUN npm install

# Expose port 3000 (or the port you are using for the frontend)
EXPOSE 3000

# Start the frontend app (use `npm start` or your specific start command)
CMD ["npm", "start"]
