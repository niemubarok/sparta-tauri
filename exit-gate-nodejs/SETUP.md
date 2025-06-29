# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Edit configuration
nano .env

# Test GPIO functionality (optional - only on Raspberry Pi)
npm run test-gpio

# Start the application
npm start

# For development with auto-reload
npm run dev

# Access the application
# Open browser and go to: http://your-raspberry-pi-ip:3000
