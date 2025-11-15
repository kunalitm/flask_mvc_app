#!/bin/bash

echo "Starting Flask MVC Application..."
echo ""

# Function to handle cleanup
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
python run.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Both servers are running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Login with:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
