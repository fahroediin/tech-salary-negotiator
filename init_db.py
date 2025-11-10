#!/usr/bin/env python3
"""
Database initialization script for Tech Salary Negotiator
Run this script to set up the database tables and initial data
"""

import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize database with tables and sample data
    """
    try:
        logger.info("Initializing database with SQLAlchemy...")

        # Import and use SQLAlchemy initialization
        from database import init_database as db_init

        success = db_init()

        if success:
            logger.info("✅ Database initialization completed successfully!")
        else:
            logger.error("❌ Database initialization failed!")

        return success

    except Exception as e:
        logger.error(f"❌ Error during database initialization: {e}")
        return False

if __name__ == "__main__":
    init_database()