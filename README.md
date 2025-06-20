# Tiffin Service CRM

A comprehensive Customer Relationship Management (CRM) system designed specifically for tiffin (meal delivery) services. This application helps manage customers, subscriptions, orders, deliveries, and includes advanced route optimization features.

## 🚀 Features

### Core Business Management
- **Customer Management**: Complete customer profiles with contact information, addresses, and preferences
- **Subscription Management**: Flexible tiffin plans (Gold, Silver, Trial options)
- **Order Management**: Daily order creation, tracking, and status updates
- **Delivery Management**: Comprehensive delivery scheduling and tracking
- **Payment Tracking**: Billing and payment management system

### Advanced Features
- **Route Optimization**: Advanced Traveling Salesman Problem (TSP) solver for efficient delivery routes
- **Geographic Clustering**: Intelligent grouping of deliveries by zones
- **Real-time Analytics**: Dashboard with business insights and metrics
- **Responsive Design**: Mobile-friendly interface for all devices

### Tiffin Plans Supported
- **Gold Plan**: $25/month, 6 meals/week, premium features (4 rotis, 8oz sabji, 6oz dal/kadhi, weekly dessert)
- **Silver Plan**: $18/month, 5 meals/week, standard features (3 rotis, 6oz sabji, 4oz dal/kadhi, monthly dessert)
- **Trial Plans**: 1-day and 6-day trial options for new customers

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: JWT-based authentication and authorization
- **API**: RESTful API design with comprehensive endpoints
- **Route Optimization**: Custom TSP algorithm with geopy integration

### Frontend (React)
- **Framework**: React 18 with modern hooks and context
- **Styling**: Tailwind CSS with shadcn/ui components
- **State Management**: React Context for authentication and global state
- **API Communication**: Axios for HTTP requests
- **Routing**: React Router for navigation

## 📦 Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm (recommended) or npm

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python src/main.py
```

5. The backend will be available at `http://localhost:5001`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
pnpm install
# or
npm install
```

3. Start the development server:
```bash
pnpm run dev
# or
npm run dev
```

4. The frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Backend Configuration
- Database URL can be configured via environment variables
- JWT secret key should be set for production
- CORS is configured to allow frontend access

### Frontend Configuration
- API base URL is configured in `src/lib/api.js`
- Update the backend URL if deploying to different domains

## 📱 Usage

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

### Key Workflows

1. **Customer Management**
   - Add new customers with complete profile information
   - Search and filter customers
   - View customer subscription history

2. **Order Management**
   - Create daily orders for active subscriptions
   - Track order status (pending, confirmed, prepared, delivered)
   - Bulk order creation for efficiency

3. **Delivery Optimization**
   - Use the route optimization feature to plan efficient delivery routes
   - View optimized routes with time estimates
   - Track delivery status in real-time

4. **Business Analytics**
   - Monitor daily revenue and order volumes
   - Track delivery performance metrics
   - Analyze customer growth and retention

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Refresh JWT token

### Customers
- `GET /api/customers` - List customers
- `POST /api/customers` - Create customer
- `GET /api/customers/{id}` - Get customer details
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Orders
- `GET /api/orders` - List orders
- `POST /api/orders` - Create order
- `POST /api/orders/bulk-create` - Bulk create orders
- `PUT /api/orders/{id}/status` - Update order status

### Deliveries
- `GET /api/deliveries` - List deliveries
- `GET /api/deliveries/today` - Today's deliveries
- `POST /api/deliveries/optimize-route` - Optimize delivery routes
- `PUT /api/deliveries/{id}/status` - Update delivery status

### Plans & Subscriptions
- `GET /api/plans` - List tiffin plans
- `GET /api/subscriptions` - List subscriptions
- `POST /api/subscriptions` - Create subscription

## 🔍 Route Optimization Algorithm

The system includes a sophisticated route optimization engine:

- **TSP Solver**: Implements Nearest Neighbor heuristic with 2-opt improvement
- **Geographic Clustering**: Groups deliveries by zones for efficiency
- **Real Distance Calculation**: Uses geopy for accurate geodesic distances
- **Time Estimation**: Calculates realistic delivery times including travel
- **Multiple Routes**: Supports splitting large delivery sets into manageable routes

## 🚀 Deployment

### Production Deployment

1. **Backend Deployment**:
   - Configure production database (PostgreSQL recommended)
   - Set environment variables for security
   - Deploy to cloud platform (AWS, Heroku, DigitalOcean)

2. **Frontend Deployment**:
   - Build production bundle: `pnpm run build`
   - Deploy to static hosting (Netlify, Vercel, AWS S3)
   - Update API URLs for production backend

### Environment Variables

Backend `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost/tiffin_crm
JWT_SECRET_KEY=your-secret-key
FLASK_ENV=production
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For support and questions, please open an issue in the GitHub repository.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by real tiffin service business needs
- Route optimization algorithms based on academic research
- UI/UX designed for efficiency and ease of use

