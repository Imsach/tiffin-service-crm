#!/usr/bin/env python3
"""
Database initialization script for Tiffin CRM
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from src.models.database import db

def init_database():
    """Initialize the database with tables and default data."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Database initialization completed!")
        print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    init_database()

