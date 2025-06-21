# Database Migration Guide

This guide explains how to migrate from SQLite to PostgreSQL and set up the configuration system.

## Prerequisites

### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### Start PostgreSQL Service
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql
```

## Database Setup

### 1. Create Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE tiffin_crm;
CREATE USER tiffin_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE tiffin_crm TO tiffin_user;
\q
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the .env file with your database credentials
nano backend/.env
```

Update the DATABASE_URL in your `.env` file:
```
DATABASE_URL=postgresql://tiffin_user:your_secure_password@localhost:5432/tiffin_crm
```

## Migration Steps

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database Migration
```bash
# Initialize Flask-Migrate (if not already done)
flask db init

# Create migration for current schema
flask db migrate -m "Initial migration to PostgreSQL"

# Apply migration
flask db upgrade
```

### 3. Data Migration (if needed)
If you have existing SQLite data to migrate:

```bash
# Export data from SQLite
python scripts/export_sqlite_data.py

# Import data to PostgreSQL
python scripts/import_to_postgresql.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key | Required for production |
| `JWT_SECRET_KEY` | JWT signing key | Required for production |
| `CORS_ORIGINS` | Allowed CORS origins | localhost:3000,localhost:5173 |

### Production Configuration

For production deployment:

```bash
# Set environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export SECRET_KEY=your-super-secret-key
export JWT_SECRET_KEY=your-jwt-secret-key
```

## Verification

### 1. Test Database Connection
```bash
python -c "
from src.main import app
with app.app_context():
    from src.models.database import db
    print('Database connection successful!')
    print(f'Database URL: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')
"
```

### 2. Verify Tables
```bash
# Connect to PostgreSQL
psql -U tiffin_user -d tiffin_crm

# List tables
\dt

# Check a specific table
\d customers
```

## Troubleshooting

### Common Issues

1. **Connection refused**
   - Ensure PostgreSQL is running
   - Check firewall settings
   - Verify connection parameters

2. **Authentication failed**
   - Check username and password
   - Verify user permissions
   - Update pg_hba.conf if needed

3. **Database does not exist**
   - Create the database manually
   - Check database name spelling

### Logs
Check application logs for detailed error messages:
```bash
tail -f logs/app.log
```

## Security Best Practices

1. **Use strong passwords** for database users
2. **Limit database user permissions** to only what's needed
3. **Use environment variables** for sensitive configuration
4. **Enable SSL** for database connections in production
5. **Regular backups** of your PostgreSQL database

## Backup and Restore

### Backup
```bash
pg_dump -U tiffin_user -h localhost tiffin_crm > backup.sql
```

### Restore
```bash
psql -U tiffin_user -h localhost tiffin_crm < backup.sql
```

