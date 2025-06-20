# Tiffin Service CRM - Project Structure

## Overview
This project contains a complete tiffin service CRM system with React frontend and Flask backend.

## Directory Structure

```
tiffin-service-crm/
├── README.md                 # Main project documentation
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT License
├── backend/                 # Flask backend application
│   ├── src/                # Source code
│   │   ├── main.py         # Application entry point
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Virtual environment (excluded from git)
├── frontend/              # React frontend application
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   ├── lib/         # Utility libraries
│   │   └── App.jsx      # Main application component
│   ├── package.json     # Node.js dependencies
│   ├── dist/           # Production build (excluded from git)
│   └── node_modules/   # Node dependencies (excluded from git)
└── docs/              # Additional documentation
    ├── api-documentation.md
    ├── deployment-guide.md
    └── user-manual.md
```

## Key Files

### Backend
- `backend/src/main.py` - Flask application entry point
- `backend/src/models/database.py` - Database models and schema
- `backend/src/routes/` - API endpoint definitions
- `backend/src/utils/route_optimizer.py` - Route optimization algorithms

### Frontend
- `frontend/src/App.jsx` - Main React application
- `frontend/src/components/` - Reusable UI components
- `frontend/src/contexts/AuthContext.jsx` - Authentication management
- `frontend/src/lib/api.js` - API communication layer

## Getting Started

1. Clone the repository
2. Follow the installation instructions in README.md
3. Start the backend server first, then the frontend
4. Access the application at http://localhost:5173

## Development Workflow

1. Backend development: Work in `backend/src/`
2. Frontend development: Work in `frontend/src/`
3. Test both applications locally before committing
4. Use the provided API documentation for integration

## Deployment

- Backend: Deploy Flask application to cloud platform
- Frontend: Build with `pnpm run build` and deploy static files
- Database: Configure PostgreSQL for production use

## Support

Refer to the main README.md for detailed setup and usage instructions.

