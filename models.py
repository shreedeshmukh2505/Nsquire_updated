"""
Database Models for NSquire College Guidance System
Using SQLAlchemy ORM for database operations
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class College(Base):
    """
    College table - stores main college information
    """
    __tablename__ = 'colleges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    location = Column(String(100), index=True)
    type = Column(String(50))  # Public/Private
    rating = Column(Float)
    facilities = Column(JSON)  # Store as JSON array
    average_package = Column(Integer)  # In rupees
    highest_package = Column(Integer)  # In rupees
    top_recruiters = Column(JSON)  # Store as JSON array

    # Relationships
    courses = relationship("Course", back_populates="college", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<College(id={self.id}, name='{self.name}', location='{self.location}')>"

    def to_dict(self):
        """Convert college object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'type': self.type,
            'rating': float(self.rating) if self.rating else None,
            'facilities': self.facilities,
            'placements': {
                'average_package': self.average_package,
                'highest_package': self.highest_package,
                'top_recruiters': self.top_recruiters
            }
        }


class Course(Base):
    """
    Course table - stores course information for each college
    """
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    college_id = Column(Integer, ForeignKey('colleges.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    duration = Column(String(50))
    annual_fee = Column(Integer)  # In rupees

    # Relationships
    college = relationship("College", back_populates="courses")
    cutoffs = relationship("Cutoff", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', college_id={self.college_id})>"

    def to_dict(self, include_cutoffs=False):
        """Convert course object to dictionary"""
        result = {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'annual_fee': self.annual_fee
        }

        if include_cutoffs:
            result['cutoffs'] = {}
            for cutoff in self.cutoffs:
                year = str(cutoff.year)
                if year not in result['cutoffs']:
                    result['cutoffs'][year] = {}
                result['cutoffs'][year][cutoff.category] = cutoff.cutoff_rank

        return result


class Cutoff(Base):
    """
    Cutoff table - stores cutoff ranks by year and category
    """
    __tablename__ = 'cutoffs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    category = Column(String(10), nullable=False, index=True)  # GOPEN, LOPEN, TFWS, etc.
    cutoff_rank = Column(Integer, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="cutoffs")

    def __repr__(self):
        return f"<Cutoff(course_id={self.course_id}, year={self.year}, category='{self.category}', rank={self.cutoff_rank})>"

    def to_dict(self):
        """Convert cutoff object to dictionary"""
        return {
            'year': self.year,
            'category': self.category,
            'cutoff_rank': self.cutoff_rank
        }


# Database connection and session management
class DatabaseManager:
    """
    Manages database connections and sessions
    Supports both SQLite (local) and PostgreSQL (production)
    """

    def __init__(self, database_url=None):
        """
        Initialize database manager

        Args:
            database_url: Database connection string
                         If None, uses SQLite (colleges.db)
                         For PostgreSQL: postgresql://user:pass@host/db
        """
        if database_url is None:
            # Default to SQLite for local development
            database_url = 'sqlite:///colleges.db'

        # Create engine with appropriate settings
        if database_url.startswith('sqlite'):
            # SQLite specific settings
            self.engine = create_engine(
                database_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False  # Set to True for SQL query logging
            )
        else:
            # PostgreSQL settings
            self.engine = create_engine(
                database_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=5,
                max_overflow=10,
                echo=False
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully!")

    def drop_tables(self):
        """Drop all tables from the database (use with caution!)"""
        Base.metadata.drop_all(self.engine)
        print("All tables dropped!")

    def get_session(self):
        """
        Get a new database session

        Usage:
            db = DatabaseManager()
            session = db.get_session()
            try:
                # Use session
                colleges = session.query(College).all()
            finally:
                session.close()
        """
        return self.SessionLocal()

    def get_engine(self):
        """Get the SQLAlchemy engine"""
        return self.engine


# Singleton instance for easy import
_db_manager = None


def get_db_manager(database_url=None):
    """
    Get or create the database manager singleton

    Args:
        database_url: Database connection string (optional)

    Returns:
        DatabaseManager instance
    """
    global _db_manager

    if _db_manager is None:
        # Check for environment variable
        db_url = database_url or os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL')
        _db_manager = DatabaseManager(db_url)

    return _db_manager


def get_session():
    """
    Convenience function to get a database session

    Usage:
        from models import get_session
        session = get_session()
        colleges = session.query(College).all()
        session.close()
    """
    return get_db_manager().get_session()


def init_database(database_url=None):
    """
    Initialize the database (create tables)

    Args:
        database_url: Database connection string (optional)
    """
    db = get_db_manager(database_url)
    db.create_tables()
    return db


# Query helper functions
def get_college_by_name(session, name):
    """
    Get college by exact name match

    Args:
        session: SQLAlchemy session
        name: College name

    Returns:
        College object or None
    """
    return session.query(College).filter(College.name == name).first()


def search_colleges_by_name(session, search_term):
    """
    Search colleges by name (partial match)

    Args:
        session: SQLAlchemy session
        search_term: Search string

    Returns:
        List of College objects
    """
    return session.query(College).filter(
        College.name.ilike(f'%{search_term}%')
    ).all()


def get_colleges_by_location(session, location):
    """
    Get all colleges in a specific location

    Args:
        session: SQLAlchemy session
        location: City name

    Returns:
        List of College objects
    """
    return session.query(College).filter(College.location == location).all()


def get_course_cutoff(session, course_id, year, category):
    """
    Get cutoff for a specific course, year, and category

    Args:
        session: SQLAlchemy session
        course_id: Course ID
        year: Year (e.g., 2024)
        category: Category (e.g., 'GOPEN')

    Returns:
        Cutoff object or None
    """
    return session.query(Cutoff).filter(
        Cutoff.course_id == course_id,
        Cutoff.year == year,
        Cutoff.category == category
    ).first()


def get_colleges_by_cutoff_range(session, min_rank, max_rank, category='GOPEN', year=2024):
    """
    Get colleges within a cutoff rank range

    Args:
        session: SQLAlchemy session
        min_rank: Minimum rank
        max_rank: Maximum rank
        category: Category (default: 'GOPEN')
        year: Year (default: 2024)

    Returns:
        List of (College, Course, Cutoff) tuples
    """
    from sqlalchemy.orm import joinedload

    results = session.query(College, Course, Cutoff).join(
        Course, College.id == Course.college_id
    ).join(
        Cutoff, Course.id == Cutoff.course_id
    ).filter(
        Cutoff.year == year,
        Cutoff.category == category,
        Cutoff.cutoff_rank.between(min_rank, max_rank)
    ).order_by(Cutoff.cutoff_rank).all()

    return results


if __name__ == '__main__':
    # Test database creation
    print("Initializing database...")
    db = init_database()
    print("Database initialized successfully!")

    # Test session
    session = get_session()
    print(f"Session created: {session}")
    session.close()
    print("Database models loaded successfully!")
