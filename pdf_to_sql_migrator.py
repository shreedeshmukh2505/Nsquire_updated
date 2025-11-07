"""
PDF to SQL Database Migrator
Parses cutoff PDF files and updates the SQL database with new cutoff data
"""

import re
import PyPDF2
import logging
from typing import Dict, List
from models import get_session, College, Course, Cutoff
from sqlalchemy.exc import IntegrityError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFToSQLMigrator:
    """
    Migrates cutoff data from PDF files to SQL database
    """

    def __init__(self):
        # Pattern to match college code and name
        self.college_name_pattern = r'^(\d{5})\s*-\s*(.+?)(?=\n|$)'
        # Pattern to match branch code and name
        self.branch_pattern = r'(\d{10})\s*-\s*(.+?)(?=\n|$)'
        # Pattern to match status
        self.status_pattern = r'Status:\s*(.+?)(?=\n|$)'
        # Pattern to match stage
        self.stage_pattern = r'Stage\s*([IVX]+)(?:-Non PWD)?'

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return ""

    def parse_cutoff_data(self, section_text: str) -> List[Dict]:
        """Extract cutoff data from a branch section."""
        cutoff_data = []
        lines = section_text.split('\n')

        # Look for the "State Level" line
        state_level_index = -1
        for i, line in enumerate(lines):
            if 'State Level' in line:
                state_level_index = i
                break

        if state_level_index == -1:
            return cutoff_data

        # Look for categories line
        categories = []
        categories_line_index = -1

        for i in range(state_level_index + 1, min(state_level_index + 5, len(lines))):
            line = lines[i].strip()
            if not line:
                continue

            # Look for category patterns (4-6 character codes)
            potential_categories = re.findall(r'\b[A-Z]{4,6}\b', line)
            if len(potential_categories) >= 3:
                categories = potential_categories
                categories_line_index = i
                break

        if not categories:
            return cutoff_data

        # Look for data rows (stages with ranks)
        for i in range(categories_line_index + 1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            # Look for stage information
            stage_match = re.search(r'\b([IVX]+)(?:-Non\s+PWD)?\b', line)
            if stage_match:
                stage = stage_match.group(1)
                stage_data = []

                # Collect data for this stage
                for j in range(i, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue

                    # Stop at boundaries
                    if (re.search(r'\b([IVX]+)(?:-Non\s+PWD)?\b', next_line) and j > i) or \
                       'Status:' in next_line or re.match(r'^\d{10}', next_line):
                        break

                    # Find ranks and percentages
                    ranks = re.findall(r'\b(\d{4,6})\b', next_line)
                    percentages = re.findall(r'\(([\d.]+)\)', next_line)

                    if ranks:
                        stage_data.extend([(rank, None) for rank in ranks])

                    if percentages:
                        for percentage in percentages:
                            for k in range(len(stage_data) - 1, -1, -1):
                                rank, existing_percentage = stage_data[k]
                                if existing_percentage is None:
                                    stage_data[k] = (rank, percentage)
                                    break

                # Match categories with data
                complete_data = [(rank, percentage) for rank, percentage in stage_data
                                if rank and percentage]

                for j, (rank, percentage) in enumerate(complete_data):
                    if j < len(categories):
                        category = categories[j]
                        try:
                            cutoff_data.append({
                                'stage': stage,
                                'category': category,
                                'rank': int(rank),
                                'percentage': float(percentage)
                            })
                        except ValueError:
                            continue

        return cutoff_data

    def find_or_create_college(self, session, college_name: str) -> College:
        """Find existing college or create new one."""
        # Try to find existing college
        college = session.query(College).filter(
            College.name.like(f'%{college_name}%')
        ).first()

        if not college:
            # Create new college with basic info
            college = College(
                name=college_name,
                location='Unknown',  # You may want to extract this from the PDF
                type='Unknown',
                rating=0.0,
                facilities=[],
                average_package=0,
                highest_package=0,
                top_recruiters=[]
            )
            session.add(college)
            session.flush()  # Get the ID
            logger.info(f"Created new college: {college_name}")

        return college

    def find_or_create_course(self, session, college: College, branch_name: str) -> Course:
        """Find existing course or create new one."""
        # Try to find existing course
        course = session.query(Course).filter(
            Course.college_id == college.id,
            Course.name == branch_name
        ).first()

        if not course:
            # Create new course
            course = Course(
                college_id=college.id,
                name=branch_name,
                duration='4 years',  # Default for B.Tech
                annual_fee=0  # You may want to extract this from the PDF
            )
            session.add(course)
            session.flush()
            logger.info(f"Created new course: {branch_name} for {college.name}")

        return course

    def update_cutoff(self, session, course: Course, year: int, category: str, rank: int):
        """Update or create cutoff entry."""
        # Check if cutoff already exists
        existing_cutoff = session.query(Cutoff).filter(
            Cutoff.course_id == course.id,
            Cutoff.year == year,
            Cutoff.category == category
        ).first()

        if existing_cutoff:
            # Update existing cutoff
            if existing_cutoff.cutoff_rank != rank:
                old_rank = existing_cutoff.cutoff_rank
                existing_cutoff.cutoff_rank = rank
                logger.info(f"Updated cutoff for {course.name} ({category}): {old_rank} -> {rank}")
        else:
            # Create new cutoff
            cutoff = Cutoff(
                course_id=course.id,
                year=year,
                category=category,
                cutoff_rank=rank
            )
            session.add(cutoff)
            logger.info(f"Added cutoff for {course.name} ({category}): {rank}")

    def migrate_pdf_to_database(self, pdf_path: str, year: int = 2024):
        """
        Main method to parse PDF and migrate data to SQL database.

        Args:
            pdf_path: Path to the PDF file
            year: Academic year for the cutoff data (default: 2024)
        """
        logger.info(f"Starting migration from {pdf_path} for year {year}")

        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            logger.error("Could not extract text from PDF")
            return False

        # Split into lines
        lines = text.split('\n')

        # Find college sections
        college_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            match = re.match(r'^(\d{5})\s*-\s*(.+)$', line)
            if match:
                college_lines.append((i, match.group(1), match.group(2).strip()))

        logger.info(f"Found {len(college_lines)} colleges in PDF")

        session = get_session()
        total_colleges = 0
        total_branches = 0
        total_cutoffs = 0

        try:
            # Process each college
            for idx, (line_index, college_code, college_name) in enumerate(college_lines):
                try:
                    # Get college section
                    start_line = line_index
                    end_line = college_lines[idx + 1][0] if idx + 1 < len(college_lines) else len(lines)
                    college_section = '\n'.join(lines[start_line:end_line])

                    # Find or create college
                    college = self.find_or_create_college(session, college_name)
                    total_colleges += 1

                    # Find all branches in this college
                    branch_matches = re.finditer(self.branch_pattern, college_section)

                    for branch_match in branch_matches:
                        branch_code = branch_match.group(1)
                        branch_name = branch_match.group(2).strip()

                        # Get branch section
                        start_pos = branch_match.end()
                        next_match = re.search(self.branch_pattern, college_section[start_pos:])
                        end_pos = start_pos + next_match.start() if next_match else len(college_section)
                        branch_section = college_section[start_pos:end_pos]

                        # Find or create course
                        course = self.find_or_create_course(session, college, branch_name)
                        total_branches += 1

                        # Parse cutoff data
                        cutoff_data = self.parse_cutoff_data(branch_section)

                        # Update cutoffs in database
                        for cutoff_entry in cutoff_data:
                            self.update_cutoff(
                                session,
                                course,
                                year,
                                cutoff_entry['category'],
                                cutoff_entry['rank']
                            )
                            total_cutoffs += 1

                    # Commit after each college to save progress
                    session.commit()
                    logger.info(f"Processed college {idx + 1}/{len(college_lines)}: {college_name}")

                except Exception as e:
                    logger.error(f"Error processing college {college_name}: {e}")
                    session.rollback()
                    continue

            logger.info("=" * 80)
            logger.info("Migration completed successfully!")
            logger.info(f"Total colleges processed: {total_colleges}")
            logger.info(f"Total branches processed: {total_branches}")
            logger.info(f"Total cutoffs updated: {total_cutoffs}")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.error(f"Error during migration: {e}")
            session.rollback()
            return False

        finally:
            session.close()


# Usage example
if __name__ == "__main__":
    import sys

    migrator = PDFToSQLMigrator()

    # Get PDF path from command line or use default
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "cutoff.pdf"

    # Get year from command line or use default
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2024

    print(f"\n{'='*80}")
    print(f"PDF to SQL Migration Tool")
    print(f"{'='*80}")
    print(f"PDF File: {pdf_path}")
    print(f"Year: {year}")
    print(f"{'='*80}\n")

    # Run migration
    success = migrator.migrate_pdf_to_database(pdf_path, year)

    if success:
        print("\n✅ Migration completed successfully!")
        print("The database has been updated with new cutoff data.")
    else:
        print("\n❌ Migration failed. Check the logs for details.")

    print(f"\n{'='*80}\n")
