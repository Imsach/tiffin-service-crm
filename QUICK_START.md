# Quick Start Guide

## Prerequisites
- Python 3.11+
- Node.js 20+
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd tiffin-service-crm
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
```
Backend will be available at: http://localhost:5001

### 3. Frontend Setup
```bash
cd frontend
npm install  # or pnpm install
npm run dev  # or pnpm run dev
```
Frontend will be available at: http://localhost:5173

### 4. Default Login
- Username: `admin`
- Password: `admin123`

## Key Features to Test

1. **Dashboard**: Overview of orders, deliveries, and revenue
2. **Customers**: Add and manage customer information
3. **Orders**: Create and track tiffin orders
4. **Deliveries**: Route optimization and delivery tracking
5. **Plans**: Gold ($25/month) and Silver ($18/month) tiffin plans

## API Documentation
The backend provides RESTful APIs for all operations. Key endpoints:
- `/api/auth/login` - Authentication
- `/api/customers` - Customer management
- `/api/orders` - Order management
- `/api/deliveries` - Delivery and route optimization
- `/api/plans` - Tiffin plan information

## Route Optimization
The system includes advanced route optimization using:
- Traveling Salesman Problem (TSP) algorithms
- Geographic clustering for delivery zones
- Real-time distance and time calculations

## Support
For issues or questions, please refer to the main README.md or open an issue in the repository.

