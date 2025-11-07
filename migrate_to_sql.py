"""
Migration Script: JSON to SQL Database
Converts dataset1.json to SQLite/PostgreSQL database
"""

import json
import os
import sys
from models import (
    init_database,
    get_session,
    College,
    Course,
    Cutoff,
    get_db_manager
)


def load_json_data(file_path='dataset1.json'):
    """
    Load college data from JSON file

    Args:
        file_path: Path to JSON file

    Returns:
        List of college dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Loaded {len(data)} colleges from {file_path}")
        return data
    except FileNotFoundError:
        print(f"✗ Error: File '{file_path}' not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON format - {e}")
        sys.exit(1)


def migrate_data(json_data, session):
    """
    Migrate JSON data to SQL database

    Args:
        json_data: List of college dictionaries
        session: SQLAlchemy session

    Returns:
        Dictionary with migration statistics
    """
    stats = {
        'colleges': 0,
        'courses': 0,
        'cutoffs': 0,
        'errors': []
    }

    print("\n" + "="*60)
    print("Starting Database Migration")
    print("="*60)

    for idx, college_data in enumerate(json_data, 1):
        try:
            print(f"\n[{idx}/{len(json_data)}] Processing: {college_data['name']}")

            # Create College record
            college = College(
                name=college_data['name'],
                location=college_data.get('location', 'Unknown'),
                type=college_data.get('type', 'Public'),
                rating=college_data.get('rating'),
                facilities=college_data.get('facilities', []),
                average_package=college_data.get('placements', {}).get('average_package'),
                highest_package=college_data.get('placements', {}).get('highest_package'),
                top_recruiters=college_data.get('placements', {}).get('top_recruiters', [])
            )

            session.add(college)
            session.flush()  # Get college.id without committing
            stats['colleges'] += 1
            print(f"  ✓ Added college (ID: {college.id})")

            # Process courses
            courses_data = college_data.get('courses', [])
            print(f"  → Processing {len(courses_data)} courses...")

            for course_idx, course_data in enumerate(courses_data, 1):
                # Create Course record
                course = Course(
                    college_id=college.id,
                    name=course_data['name'],
                    duration=course_data.get('duration', '4 years'),
                    annual_fee=course_data.get('annual_fee', 0)
                )

                session.add(course)
                session.flush()  # Get course.id
                stats['courses'] += 1

                # Process cutoffs
                cutoffs_data = course_data.get('cutoffs', {})
                cutoff_count = 0

                for year_str, categories in cutoffs_data.items():
                    year = int(year_str)

                    for category, rank in categories.items():
                        # Create Cutoff record
                        cutoff = Cutoff(
                            course_id=course.id,
                            year=year,
                            category=category,
                            cutoff_rank=rank
                        )

                        session.add(cutoff)
                        stats['cutoffs'] += 1
                        cutoff_count += 1

                print(f"    [{course_idx}] {course_data['name'][:50]}... ({cutoff_count} cutoffs)")

            # Commit after each college to prevent data loss on error
            session.commit()
            print(f"  ✓ Committed college '{college.name}' to database")

        except Exception as e:
            session.rollback()
            error_msg = f"Error processing '{college_data.get('name', 'Unknown')}': {str(e)}"
            print(f"  ✗ {error_msg}")
            stats['errors'].append(error_msg)
            continue

    return stats


def verify_migration(session):
    """
    Verify data integrity after migration

    Args:
        session: SQLAlchemy session

    Returns:
        Boolean indicating success
    """
    print("\n" + "="*60)
    print("Verifying Migration")
    print("="*60)

    try:
        # Count records
        college_count = session.query(College).count()
        course_count = session.query(Course).count()
        cutoff_count = session.query(Cutoff).count()

        print(f"✓ Colleges in database: {college_count}")
        print(f"✓ Courses in database: {course_count}")
        print(f"✓ Cutoffs in database: {cutoff_count}")

        # Sample verification - check if first college exists
        first_college = session.query(College).first()
        if first_college:
            print(f"\n✓ Sample college: {first_college.name}")
            print(f"  - Location: {first_college.location}")
            print(f"  - Rating: {first_college.rating}")
            print(f"  - Courses: {len(first_college.courses)}")

            if first_college.courses:
                first_course = first_college.courses[0]
                print(f"\n✓ Sample course: {first_course.name}")
                print(f"  - Fee: ₹{first_course.annual_fee:,}")
                print(f"  - Cutoffs: {len(first_course.cutoffs)}")

        return True

    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False


def print_statistics(stats):
    """
    Print migration statistics

    Args:
        stats: Dictionary with migration statistics
    """
    print("\n" + "="*60)
    print("Migration Statistics")
    print("="*60)
    print(f"Colleges migrated: {stats['colleges']}")
    print(f"Courses migrated:  {stats['courses']}")
    print(f"Cutoffs migrated:  {stats['cutoffs']}")
    print(f"Total records:     {stats['colleges'] + stats['courses'] + stats['cutoffs']}")

    if stats['errors']:
        print(f"\n⚠ Errors encountered: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n✓ Migration completed successfully with no errors!")


def main():
    """
    Main migration function
    """
    print("\n" + "="*60)
    print("NSquire College Database Migration")
    print("JSON → SQLite/PostgreSQL")
    print("="*60)

    # Check if database already exists
    if os.path.exists('colleges.db'):
        response = input("\n⚠ Database 'colleges.db' already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            sys.exit(0)
        else:
            # Delete existing database
            os.remove('colleges.db')
            print("✓ Deleted existing database")

    # Initialize database
    print("\nInitializing database...")
    try:
        db = init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        sys.exit(1)

    # Load JSON data
    json_data = load_json_data('dataset1.json')

    # Get database session
    session = get_session()

    try:
        # Migrate data
        stats = migrate_data(json_data, session)

        # Print statistics
        print_statistics(stats)

        # Verify migration
        if verify_migration(session):
            print("\n" + "="*60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nDatabase file: colleges.db")
            print("You can now update EDI_project.py to use this database.")
            return True
        else:
            print("\n✗ Migration verification failed!")
            return False

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        session.rollback()
        return False

    finally:
        session.close()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
