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
- **Gold Plan**: $285 CAD/month, 6 days/week, 24 tiffins (8 rotis, 12oz sabji, 12oz dal/kadhi, weekly dessert, includes paan)
- **Silver Plan**: $240 CAD/month, 6 days/week, 24 tiffins (5 rotis, 8oz sabji, 8oz dal/kadhi, weekly dessert)
- **Student Plan**: $220 CAD/month, Discounted Silver Plan for students (requires student ID verification)
- **Trial Plans**: 6-day trial ($90) and 1-day trial ($15) options for new customers

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
- PostgreSQL 12+ (recommended for production)
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

4. Configure environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

5. Set up PostgreSQL database:
```bash
# Create database and user (see DATABASE_MIGRATION.md for details)
sudo -u postgres createdb tiffin_crm
sudo -u postgres createuser tiffin_user
```

6. Initialize the database:
```bash
python scripts/init_db.py
```

7. Start the backend server:
```bash
python src/main.py
```

The backend will be available at `http://localhost:5001`

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
The backend uses environment variables for configuration. Key settings include:

- **Database**: PostgreSQL connection string
- **Security**: JWT secret keys and session configuration  
- **CORS**: Allowed origins for frontend access
- **Email**: SMTP settings for notifications (optional)
- **Logging**: Log level and file configuration

### Frontend Configuration
- API base URL is configured in `src/lib/api.js`
- Update the backend URL if deploying to different domains
- Environment-specific builds supported

### Environment Files
- `.env.example` - Template with all available options
- `.env` - Your local configuration (not tracked in git)
- Production deployments should use environment variables

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
   - View plan-wise revenue breakdown (Gold: $285, Silver: $240, Student: $220 CAD)

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
- `GET /api/plans` - List tiffin plans (Gold: $285, Silver: $240, Student: $220 CAD)
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
   - Set up PostgreSQL database on your cloud provider
   - Configure environment variables for production
   - Set `FLASK_ENV=production` 
   - Use strong secret keys for JWT and Flask
   - Deploy to cloud platform (AWS, Heroku, DigitalOcean)

2. **Frontend Deployment**:
   - Build production bundle: `pnpm run build`
   - Deploy to static hosting (Netlify, Vercel, AWS S3)
   - Update API URLs for production backend

3. **Database Migration**:
   - See `backend/DATABASE_MIGRATION.md` for detailed PostgreSQL setup
   - Use Flask-Migrate for schema updates: `flask db upgrade`

### Environment Variables

Backend `.env` file:
```
DATABASE_URL=postgresql://user:password@localhost/tiffin_crm
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=https://yourdomain.com
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

