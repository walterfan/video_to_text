#!/usr/bin/env python3
"""
Database initialization script for the video-to-text application.
Run this script to create the database tables and optionally create an admin user.
"""

import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

from app import create_app, db
from app.models import User

def init_db():
    """Initialize the database with tables and optionally create an admin user."""
    app = create_app('development')
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        print("Database tables created successfully!")

        username = os.environ.get('ADMIN_USERNAME') or 'admin'
        password = os.environ.get('ADMIN_PASSWORD') or 'pass1234'
        email = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
        
        # Check if admin user already exists (by username or email)
        admin_user = User.query.filter_by(username=username).first()
        if not admin_user:
            # Also check if email is already taken
            existing_email_user = User.query.filter_by(email=email).first()
            if existing_email_user:
                print(f"Email '{email}' is already taken by user '{existing_email_user.username}'")
                print("Please use a different email address or username.")
                return
            
            # Create admin user
            admin_user = User(
                username=username,
                email=email
            )
            admin_user.set_password(password)
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("Admin user created successfully!")
                print(f"Username: {username}")
                print(f"Password: {password}")
                print(f"Email: {email}")
                print("\n⚠️  IMPORTANT: Change the admin password in production!")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {e}")
                print("Please check that the username and email are unique.")
        else:
            print(f"Admin user '{username}' already exists.")

if __name__ == '__main__':
    init_db()
