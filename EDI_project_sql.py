"""
NSquire College Guidance Chatbot - Flask Backend with SQLAlchemy
Updated to use SQL database instead of JSON
"""

import re
import json
from fuzzywuzzy import process, fuzz
from typing import Dict, List
import cohere
# from argostranslate import package, translate  # Removed - causes slow startup
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import database models
from models import (
    get_session,
    College,
    Course,
    Cutoff,
    search_colleges_by_name,
    get_colleges_by_location,
    get_course_cutoff
)

# Import ML models
from ml_models import (
    CutoffForecaster,
    AdmissionProbabilityPredictor,
    SmartRecommendationSystem,
    get_historical_cutoffs_for_course
)

load_dotenv()

# Cohere API setup
cohere_api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(cohere_api_key)

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests


# ============================================================================
# DATABASE HELPER FUNCTIONS
# ============================================================================

def get_all_colleges():
    """Get all colleges from database"""
    session = get_session()
    try:
        colleges = session.query(College).all()
        return [college_to_dict(college) for college in colleges]
    finally:
        session.close()


def college_to_dict(college):
    """Convert College object to dictionary format (similar to JSON structure)"""
    return {
        'id': college.id,
        'name': college.name,
        'location': college.location,
        'type': college.type,
        'rating': float(college.rating) if college.rating else 0,
        'facilities': college.facilities or [],
        'placements': {
            'average_package': college.average_package or 0,
            'highest_package': college.highest_package or 0,
            'top_recruiters': college.top_recruiters or []
        },
        'courses': [
            {
                'name': course.name,
                'duration': course.duration,
                'annual_fee': course.annual_fee,
                'cutoffs': get_cutoffs_for_course(course)
            }
            for course in college.courses
        ]
    }


def get_cutoffs_for_course(course):
    """Get cutoffs for a course organized by year and category"""
    cutoffs_dict = {}
    for cutoff in course.cutoffs:
        year_str = str(cutoff.year)
        if year_str not in cutoffs_dict:
            cutoffs_dict[year_str] = {}
        cutoffs_dict[year_str][cutoff.category] = cutoff.cutoff_rank
    return cutoffs_dict


def match_college_name_db(college_name):
    """
    Fuzzy match college name and return college data from database
    """
    if not college_name:
        return None

    session = get_session()
    try:
        # Try exact match first
        college = session.query(College).filter(
            College.name.ilike(college_name)
        ).first()

        if college:
            return college_to_dict(college)

        # Fuzzy matching fallback
        all_colleges = session.query(College).all()
        college_names = [c.name for c in all_colleges]

        best_match, score = process.extractOne(
            college_name,
            college_names,
            scorer=fuzz.token_set_ratio
        )

        if score > 75:  # Match threshold
            college = session.query(College).filter(
                College.name == best_match
            ).first()
            return college_to_dict(college) if college else None

        return None
    finally:
        session.close()


def find_eligible_colleges_db(rank, category):
    """
    Find eligible colleges based on rank and category using database
    """
    session = get_session()
    eligible_colleges = []

    try:
        # Get all colleges with their courses and cutoffs
        colleges = session.query(College).all()

        for college in colleges:
            eligible_branches = []

            for course in college.courses:
                # Get cutoff for this course, year 2024, and specified category
                cutoff = session.query(Cutoff).filter(
                    Cutoff.course_id == course.id,
                    Cutoff.year == 2024,
                    Cutoff.category == category
                ).first()

                if cutoff and rank <= cutoff.cutoff_rank:
                    eligible_branches.append(course.name)

            # Sort branches and take top 2
            eligible_branches = sorted(eligible_branches)[:2]

            if eligible_branches:
                eligible_colleges.append({
                    "college": college.name,
                    "branches": eligible_branches,
                    "rating": float(college.rating) if college.rating else 0
                })

        # Limit to 7 unique colleges sorted by rating
        return sorted(eligible_colleges, key=lambda x: x['rating'], reverse=True)[:7]

    finally:
        session.close()


# ============================================================================
# ORIGINAL FUNCTIONS (Updated to use database)
# ============================================================================

def detect_language(sentence):
    """Detect language (English vs Hinglish)"""
    hinglish_keywords = {"kya", "ka", "hai", "kyunki", "aur", "kaise", "ki", "ke"}
    words = set(sentence.lower().split())
    if words & hinglish_keywords:
        return "hinglish"
    return "english"


def setup_translation():
    """Setup translation languages for Argos Translate - DISABLED for faster startup"""
    pass  # Translation disabled to improve startup time


def translate_text(from_lang, to_lang, text):
    """Translate text between languages - DISABLED, returns original text"""
    # Translation disabled for faster startup - just return original English text
    return text


def cohere_understand_query_eligibility(user_query):
    """Cohere-based intent and entity extraction for eligibility and best college queries"""
    # Expand abbreviations before sending to Cohere
    expanded_query = expand_college_abbreviations(user_query)

    prompt = (
        f"Extract the following details from the user's query: '{expanded_query}'\n"
        "Classify the query intent into one of the following categories: [cutoff/fees/highest_package/average_package/info/eligibility/best_college].\n"
        "Identify the rank and category if the query is about rank-based college eligibility.\n"
        "If the query asks about the best college from eligible options, classify it as 'best_college'.\n"
        "Provide the response in the following JSON format:\n"
        "{"
        "\"intent\": \"[intent]\","
        "\"college_name\": \"[college_name or 'None']\","
        "\"branch\": \"[branch or 'None']\","
        "\"year\": \"[year or 'None']\","
        "\"rank\": \"[rank or 'None']\","
        "\"category\": \"[category or 'None']\""
        "}\n"
    )
    response = co.chat(
        model="command-r-08-2024",
        message=prompt,
        max_tokens=100,
        temperature=0.5
    )
    return response.text.strip()


def expand_college_abbreviations(query):
    """Expand common college abbreviations in the query"""
    abbreviations = {
        'PICT': 'Pune Institute of Computer Technology',
        'COEP': 'College of Engineering Pune',
        'VJTI': 'Veermata Jijabai Technological Institute',
        'SPCE': 'Sardar Patel College of Engineering',
        'VIT': 'Vishwakarma Institute of Technology',
        'MIT': 'MIT Academy of Engineering',
        'PCCOE': 'Pimpri Chinchwad College of Engineering',
    }

    expanded_query = query
    for abbr, full_name in abbreviations.items():
        # Use word boundaries to avoid partial matches
        import re
        pattern = r'\b' + re.escape(abbr) + r'\b'
        expanded_query = re.sub(pattern, full_name, expanded_query, flags=re.IGNORECASE)

    return expanded_query


def cohere_understand_query(user_query):
    """Cohere-based intent and entity extraction for other queries"""
    # Expand abbreviations before sending to Cohere
    expanded_query = expand_college_abbreviations(user_query)

    prompt = (
        f"Extract the following details from the user's query: '{expanded_query}'\n"
        "Provide the response in the following format:\n"
        "Intent: [cutoff/fees/highest_package/average_package/info]\n"
        "College: [the college name, if mentioned, otherwise 'None']\n"
        "Branch: [the branch name if mentioned, otherwise 'None']\n"
        "Year: [the year if provided, otherwise 'None']"
    )
    response = co.chat(
        model="command-r-08-2024",
        message=prompt,
        max_tokens=50,
        temperature=0.5
    )
    return response.text.strip()


def parse_cohere_response_eligibility(ai_response):
    """Parse Cohere response for eligibility and best college queries"""
    try:
        entities = json.loads(ai_response)
    except json.JSONDecodeError:
        entities = {'intent': None, 'college_name': None, 'branch': None, 'year': None, 'rank': None, 'category': None}
        lines = ai_response.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key in entities and value.lower() != 'none':
                    entities[key] = value
    return entities


def parse_cohere_response(ai_response):
    """Parse Cohere response for other queries"""
    entities = {'intent': None, 'college_name': None, 'branch': None, 'year': None}
    lines = ai_response.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if 'intent' in key and value.lower() != 'none':
                entities['intent'] = value
            elif 'college' in key and value.lower() != 'none':
                entities['college_name'] = value
            elif 'branch' in key and value.lower() != 'none':
                entities['branch'] = value
            elif 'year' in key and value.lower() != 'none':
                entities['year'] = value
    return entities


def find_best_college_and_branch(eligible_entries):
    """Find best college from eligible entries"""
    if not eligible_entries:
        return None
    best_entry = eligible_entries[0]
    return {
        "college": best_entry["college"],
        "branch": best_entry["branches"][0],
        "rating": best_entry["rating"]
    }


def generate_best_college_response(best_entry, language):
    """Generate best college response"""
    if not best_entry:
        if language == 'hinglish':
            return "Maaf kijiye, mujhe aapke eligible colleges mein se best college nahi mila."
        else:
            return "Sorry, I couldn't determine the best college from your eligible entries."

    prompt = (
        f"Why is {best_entry['college']} the best choice for the branch {best_entry['branch']}? "
        f"The college has a rating of {best_entry['rating']}/5. Use bold text for section headers like 'Academic Reputation:' "
        f"and highlight its academic reputation, facilities, and other notable features."
    )
    response = co.chat(
        model="command-r-08-2024",
        message=prompt,
        max_tokens=300,
        temperature=0.4
    )
    explanation = response.text.strip()

    # Handle markdown formatting
    explanation = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', explanation)
    explanation = re.sub(r'##\s*(.*?):', r'<strong>\1:</strong>', explanation)
    explanation = re.sub(r'([A-Za-z\s]+):', r'<strong>\1:</strong>', explanation)

    if language == 'hinglish':
        translated_explanation = translate_text('en', 'hi', explanation)
        return f"{best_entry['college']} branch {best_entry['branch']} ke saath sabse acha college hai.\n\n{translated_explanation}"
    else:
        return f"The best college is {best_entry['college']} with branch {best_entry['branch']}.\n\n{explanation}"


def generate_eligibility_response(eligible_entries, language='english'):
    """Generate eligibility response"""
    if not eligible_entries:
        if language == 'hinglish':
            return "Maaf kijiye, aapke rank ke liye koi college nahi mila."
        else:
            return "Sorry, no colleges were found for your rank."

    response = "Eligible colleges and top branches:\n\n" if language == 'english' else "Yogya college aur unke top branch:\n\n"

    for entry in eligible_entries:
        response += f"{entry['college']}\n"
        for branch in entry['branches']:
            response += f"- {branch}\n"
        response += "\n"

    return response.rstrip()


def get_cutoff_details(college_data, branch_name=None, year=None):
    """Get cutoff details"""
    year = year if year else '2024'
    branch_cutoffs = []

    for course in college_data['courses']:
        if branch_name and branch_name.lower() not in course['name'].lower():
            continue
        cutoff = course['cutoffs'].get(year, {})
        branch_cutoffs.append({
            'branch': course['name'],
            'cutoff': cutoff
        })

    return branch_cutoffs


def generate_cutoff_response(branch_cutoffs, college_name, language='english'):
    """Generate cutoff response"""
    if not branch_cutoffs:
        if language == 'hinglish':
            return "Maaf kijiye, is branch ke liye cutoff details nahi mili."
        else:
            return "Sorry, cutoff details for this branch are not available."

    response = f"""<div class='cutoff-container'>
    <h3 class='college-name'>Cutoff Details for {college_name}</h3>
    <div class='branches-container'>"""

    sorted_branches = sorted(branch_cutoffs, key=lambda x: x['branch'])

    for branch in sorted_branches:
        response += f"""
        <div class='branch-item'>
            <h4 class='branch-name'>{branch['branch']}</h4>
            <div class='cutoff-details'>"""

        for category, rank in branch['cutoff'].items():
            formatted_rank = f"{rank:,}"
            response += f"""
                <div class='category-item'>
                    <span class='category'>{category}:</span>
                    <span class='rank'>{formatted_rank}</span>
                </div>"""

        response += """
            </div>
        </div>"""

    response += """
    </div>
</div>"""

    return response


def generate_dynamic_response_college(intent, college_data, language='english', branch=None, year=None):
    """Generate dynamic response for college-specific queries"""
    if not college_data:
        if language == 'hinglish':
            return "Maaf kijiye, mujhe college ke baare mein jaankari nahi mili."
        else:
            return "Sorry, I couldn't find information about the college."

    if intent == 'cutoff':
        branch_cutoffs = get_cutoff_details(college_data, branch, year)
        return generate_cutoff_response(branch_cutoffs, college_data['name'], language)

    elif intent == 'fees':
        annual_fee = college_data['courses'][0]['annual_fee']
        if language == 'hinglish':
            return f"{college_data['name']} ki fees:\n₹{annual_fee:,}/saal"
        else:
            return f"The fees for {college_data['name']} are:\n₹{annual_fee:,}/year"

    elif intent == 'highest_package' or intent == 'highest_salary':
        highest_package = college_data['placements']['highest_package']
        if language == 'hinglish':
            return f"{college_data['name']} ka highest package ₹{highest_package:,}/saal hai."
        else:
            return f"The highest package for {college_data['name']} is ₹{highest_package:,}/year."

    elif intent == 'average_package' or intent == 'average_salary':
        avg_package = college_data['placements']['average_package']
        if language == 'hinglish':
            return f"{college_data['name']} ka average package ₹{avg_package:,}/saal hai."
        else:
            return f"The average package for {college_data['name']} is ₹{avg_package:,}/year."

    elif intent == 'info':
        location = college_data['location']
        rating = college_data['rating']
        facilities = ", ".join(college_data['facilities'])
        if language == 'hinglish':
            return (f"{college_data['name']} ki location {location} hai aur rating {rating}/5 hai. "
                    f"Facilities mein shamil hain: {facilities}.")
        else:
            return (f"{college_data['name']} is located in {location}, has a rating of {rating}/5. "
                    f"Facilities include: {facilities}.")

    return "Sorry, I couldn't understand your query."


def generate_dynamic_response_eligibility(intent, language='english', rank=None, category=None, eligible_entries=None):
    """Generate dynamic response for eligibility and best college queries"""
    if intent == 'eligibility':
        eligible_entries = find_eligible_colleges_db(rank, category)
        return generate_eligibility_response(eligible_entries, language)

    if intent == 'best_college':
        best_entry = find_best_college_and_branch(eligible_entries)
        return generate_best_college_response(best_entry, language)

    return "Sorry, I couldn't understand your query."


def handle_casual_conversation(user_query):
    """Handle casual conversational queries using Cohere"""
    conversational_intents = [
        "greeting", "small_talk", "how_are_you", "introduction",
        "farewell", "appreciation", "joke", "general_chat"
    ]

    prompt = (
        f"Classify the intent of this message: '{user_query}'\n"
        "Possible intents: " + ", ".join(conversational_intents) + "\n"
        "If the intent is casual/conversational, generate a friendly, natural response. "
        "If it doesn't fit a conversational intent, return 'NOT_CONVERSATIONAL'.\n"
        "Format your response as: 'Intent: [intent]\nResponse: [generated_response]'"
    )

    response = co.chat(
        model="command-r-08-2024",
        message=prompt,
        max_tokens=100,
        temperature=0.7
    )

    generated_text = response.text.strip()
    lines = generated_text.split('\n')
    intent = lines[0].split(': ')[1] if len(lines) > 0 and ':' in lines[0] else None

    if intent and intent != 'NOT_CONVERSATIONAL':
        response_text = lines[1].split(': ')[1] if len(lines) > 1 else generated_text
        return response_text

    return None


def process_user_query(user_query):
    """Main query processing function"""
    detected_language = detect_language(user_query)

    # Try eligibility/best college query first
    ai_response_eligibility = cohere_understand_query_eligibility(user_query)
    parsed_data_eligibility = parse_cohere_response_eligibility(ai_response_eligibility)

    intent_eligibility = parsed_data_eligibility.get('intent', None)

    if intent_eligibility in ['eligibility', 'best_college']:
        rank = int(parsed_data_eligibility['rank']) if parsed_data_eligibility['rank'] and parsed_data_eligibility['rank'] != 'None' else None
        category = parsed_data_eligibility['category'].upper() if parsed_data_eligibility['category'] and parsed_data_eligibility['category'] != 'None' else 'GOPEN'

        if intent_eligibility == 'eligibility' and rank is not None:
            eligible_entries = find_eligible_colleges_db(rank, category)
            return generate_dynamic_response_eligibility(
                intent_eligibility,
                language=detected_language,
                rank=rank,
                category=category,
                eligible_entries=eligible_entries
            )

        if intent_eligibility == 'best_college':
            eligible_entries = find_eligible_colleges_db(rank if rank else 0, category)
            return generate_dynamic_response_eligibility(
                intent_eligibility,
                language=detected_language,
                eligible_entries=eligible_entries
            )

    # Regular college query - try this first
    ai_response = cohere_understand_query(user_query)
    parsed_data = parse_cohere_response(ai_response)

    intent = parsed_data['intent']
    college_name = parsed_data['college_name']
    branch_name = parsed_data['branch']
    year = parsed_data['year']

    # Only check casual conversation if no college was mentioned
    if not college_name or college_name == 'None':
        casual_response = handle_casual_conversation(user_query)
        if casual_response:
            return casual_response

    college_data = match_college_name_db(college_name)

    return generate_dynamic_response_college(
        intent,
        college_data,
        language=detected_language,
        branch=branch_name,
        year=year
    )


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    print("Chat endpoint hit!")

    print("Request method:", request.method)
    print("Request content type:", request.content_type)
    print("Request data:", request.get_json())

    try:
        data = request.get_json()
        if not data:
            print("No JSON data received")
            return jsonify({"error": "No data provided"}), 400

        user_query = data.get('message', '')
        print(f"Received query: {user_query}")

        if not user_query:
            return jsonify({"error": "Please enter a valid query."}), 400

        # Process query (now using database)
        response = process_user_query(user_query)
        print(f"Generated response: {response}")

        return jsonify({"response": response})

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "database": "connected"})


# ============================================================================
# COLLEGE COMPARISON API ENDPOINTS
# ============================================================================

@app.route('/api/colleges/all', methods=['GET'])
def get_all_colleges_api():
    """Get list of all colleges (name and id only)"""
    try:
        session = get_session()
        colleges = session.query(College.id, College.name, College.location, College.rating).all()

        result = [
            {
                'id': c.id,
                'name': c.name,
                'location': c.location,
                'rating': float(c.rating) if c.rating else 0
            }
            for c in colleges
        ]

        session.close()
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_all_colleges: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/filters/options', methods=['GET'])
def get_filter_options():
    """Get available filter options for search"""
    try:
        session = get_session()

        # Get unique locations
        locations = session.query(College.location).distinct().all()
        location_list = sorted([loc[0] for loc in locations if loc[0]])

        # Get fee range
        fees = session.query(Course.annual_fee).filter(Course.annual_fee > 0).all()
        fee_values = [f[0] for f in fees]
        min_fee = min(fee_values) if fee_values else 0
        max_fee = max(fee_values) if fee_values else 300000

        # Get unique branches
        branches = session.query(Course.name).distinct().all()
        # Extract branch type (e.g., "Computer Engineering" from "B.Tech Computer Engineering")
        branch_types = set()
        for branch in branches:
            branch_name = branch[0]
            # Extract the branch name after "B.Tech" or similar prefix
            if 'B.Tech' in branch_name:
                branch_type = branch_name.replace('B.Tech', '').strip()
                branch_types.add(branch_type)

        branch_list = sorted(list(branch_types))

        # Get rating range
        ratings = session.query(College.rating).filter(College.rating.isnot(None)).all()
        rating_values = [float(r[0]) for r in ratings]
        min_rating = min(rating_values) if rating_values else 0
        max_rating = max(rating_values) if rating_values else 5.0

        session.close()

        return jsonify({
            'locations': location_list,
            'fee_range': {
                'min': min_fee,
                'max': max_fee
            },
            'branches': branch_list[:20],  # Top 20 branches
            'rating_range': {
                'min': min_rating,
                'max': max_rating
            }
        })

    except Exception as e:
        print(f"Error in get_filter_options: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/colleges/search', methods=['GET'])
def search_colleges_api():
    """Advanced search colleges with filters"""
    try:
        # Get query parameters
        search_query = request.args.get('q', '').strip()
        locations = request.args.getlist('location')  # Multiple locations
        min_fee = request.args.get('min_fee', type=int)
        max_fee = request.args.get('max_fee', type=int)
        min_rating = request.args.get('min_rating', type=float)
        branch = request.args.get('branch', '').strip()
        sort_by = request.args.get('sort', 'rating')  # rating, name, fees
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        session = get_session()

        # Base query with joins
        query = session.query(College).join(Course)

        # Apply filters
        if search_query:
            query = query.filter(College.name.ilike(f'%{search_query}%'))

        if locations:
            query = query.filter(College.location.in_(locations))

        if min_fee is not None or max_fee is not None:
            if min_fee is not None and max_fee is not None:
                query = query.filter(Course.annual_fee.between(min_fee, max_fee))
            elif min_fee is not None:
                query = query.filter(Course.annual_fee >= min_fee)
            elif max_fee is not None:
                query = query.filter(Course.annual_fee <= max_fee)

        if min_rating is not None:
            query = query.filter(College.rating >= min_rating)

        if branch:
            query = query.filter(Course.name.ilike(f'%{branch}%'))

        # Remove duplicates
        query = query.distinct()

        # Apply sorting
        if sort_by == 'rating':
            query = query.order_by(College.rating.desc())
        elif sort_by == 'name':
            query = query.order_by(College.name.asc())
        elif sort_by == 'fees':
            query = query.order_by(Course.annual_fee.asc())
        else:
            query = query.order_by(College.rating.desc())

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        offset = (page - 1) * per_page
        colleges = query.offset(offset).limit(per_page).all()

        # Format results with comprehensive data
        result = []
        for college in colleges:
            # Get fee range
            fees = [c.annual_fee for c in college.courses if c.annual_fee > 0]
            min_college_fee = min(fees) if fees else 0
            max_college_fee = max(fees) if fees else 0

            # Get branch count
            branch_count = len(college.courses)

            # Get available branches (top 3)
            top_branches = [c.name for c in college.courses[:3]]

            result.append({
                'id': college.id,
                'name': college.name,
                'location': college.location,
                'type': college.type,
                'rating': float(college.rating) if college.rating else 0,
                'fee_range': {
                    'min': min_college_fee,
                    'max': max_college_fee
                },
                'branch_count': branch_count,
                'top_branches': top_branches,
                'placements': {
                    'average': college.average_package or 0,
                    'highest': college.highest_package or 0
                },
                'facilities_count': len(college.facilities) if college.facilities else 0
            })

        session.close()

        return jsonify({
            'results': result,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })

    except Exception as e:
        print(f"Error in search_colleges: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_colleges():
    """Compare multiple colleges side-by-side"""
    try:
        data = request.get_json()
        college_ids = data.get('college_ids', [])

        if not college_ids or len(college_ids) < 2:
            return jsonify({"error": "Please select at least 2 colleges to compare"}), 400

        if len(college_ids) > 4:
            return jsonify({"error": "Maximum 4 colleges can be compared at once"}), 400

        session = get_session()
        colleges_data = []

        for college_id in college_ids:
            college = session.query(College).filter_by(id=college_id).first()

            if not college:
                continue

            # Get all courses with cutoffs
            courses_info = []
            for course in college.courses:
                # Get 2024 cutoffs for this course
                cutoffs_2024 = {}
                for cutoff in course.cutoffs:
                    if cutoff.year == 2024:
                        cutoffs_2024[cutoff.category] = cutoff.cutoff_rank

                if cutoffs_2024:  # Only include courses with cutoffs
                    courses_info.append({
                        'name': course.name,
                        'fee': course.annual_fee,
                        'duration': course.duration,
                        'cutoffs': cutoffs_2024
                    })

            colleges_data.append({
                'id': college.id,
                'name': college.name,
                'location': college.location,
                'type': college.type,
                'rating': float(college.rating) if college.rating else 0,
                'facilities': college.facilities or [],
                'placements': {
                    'average_package': college.average_package or 0,
                    'highest_package': college.highest_package or 0,
                    'top_recruiters': college.top_recruiters or []
                },
                'courses': courses_info
            })

        session.close()

        if len(colleges_data) < 2:
            return jsonify({"error": "Could not find enough valid colleges to compare"}), 404

        return jsonify(colleges_data)

    except Exception as e:
        print(f"Error in compare_colleges: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict_colleges():
    """Predict eligible colleges based on rank and category"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        rank = data.get('rank')
        category = data.get('category', 'GOPEN')

        if not rank:
            return jsonify({"error": "Rank is required"}), 400

        try:
            rank = int(rank)
        except ValueError:
            return jsonify({"error": "Invalid rank value"}), 400

        if rank < 1 or rank > 100000:
            return jsonify({"error": "Rank must be between 1 and 100000"}), 400

        # Valid categories - match actual database categories
        valid_categories = ['GOPEN', 'LOPEN', 'GOBCH', 'LOBCH', 'GSCH', 'LSCH', 'GSTH', 'GNT1H', 'GNT2H', 'GNT3H', 'GVJH']
        if category not in valid_categories:
            return jsonify({"error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"}), 400

        session = get_session()

        # Initialize ML models
        prob_predictor = AdmissionProbabilityPredictor()
        forecaster = CutoffForecaster()
        recommender = SmartRecommendationSystem()

        # Query colleges with courses that have cutoffs for the given category and rank
        eligible_colleges = []

        # Get user preferences (can be extended to get from request)
        user_preferences = data.get('preferences', {
            'placements_weight': 0.30,
            'rank_eligibility_weight': 0.30,
            'fees_weight': 0.15,
            'rating_weight': 0.15,
            'location_weight': 0.10
        })

        # Get all colleges with their courses and cutoffs
        colleges = session.query(College).all()

        for college in colleges:
            college_data = {
                'id': college.id,
                'name': college.name,
                'location': college.location,
                'type': college.type,
                'rating': float(college.rating) if college.rating else 0,
                'average_package': college.average_package or 0,
                'highest_package': college.highest_package or 0,
                'eligible_branches': [],
                'probability': 'N/A'
            }

            # Get all courses for this college
            for course in college.courses:
                # Get cutoff for this course, category, and year 2024
                cutoff = session.query(Cutoff).filter(
                    Cutoff.course_id == course.id,
                    Cutoff.category == category,
                    Cutoff.year == 2024
                ).first()

                if cutoff:
                    # Calculate probability based on rank vs cutoff
                    if rank <= cutoff.cutoff_rank:
                        # Get historical cutoffs for ML prediction
                        historical_cutoffs = get_historical_cutoffs_for_course(course.id, category)
                        historical_ranks = [h['cutoff_rank'] for h in historical_cutoffs]

                        # ML-based admission probability
                        ml_probability = prob_predictor.calculate_probability(
                            rank, cutoff.cutoff_rank, historical_ranks
                        )

                        # Get cutoff trend and forecast
                        if len(historical_cutoffs) >= 2:
                            forecast = forecaster.predict_next_year_cutoff(historical_cutoffs, 2025)
                            trend_analysis = forecaster.get_historical_trend_analysis(historical_cutoffs)
                        else:
                            forecast = None
                            trend_analysis = None

                        rank_diff = cutoff.cutoff_rank - rank
                        percentage_diff = (rank_diff / cutoff.cutoff_rank) * 100

                        college_data['eligible_branches'].append({
                            'name': course.name,
                            'cutoff_rank': cutoff.cutoff_rank,
                            'your_rank': rank,
                            'probability': ml_probability['category'],
                            'probability_percentage': ml_probability['probability'],
                            'ml_confidence': ml_probability['confidence_factors'],
                            'annual_fee': course.annual_fee,
                            'rank_difference': rank_diff,
                            'forecast_2025': forecast['predicted_cutoff'] if forecast else None,
                            'trend': trend_analysis['trend_direction'] if trend_analysis else 'Unknown',
                            'color': ml_probability['color']
                        })

            # Only include colleges with at least one eligible branch
            if college_data['eligible_branches']:
                # Sort branches by probability percentage
                college_data['eligible_branches'].sort(
                    key=lambda x: x['probability_percentage'],
                    reverse=True
                )

                # Set overall college probability to the best branch probability
                college_data['probability'] = college_data['eligible_branches'][0]['probability']

                # Calculate smart recommendation score
                best_branch = college_data['eligible_branches'][0]
                recommendation_input = {
                    'rank_difference_percentage': (best_branch['rank_difference'] / best_branch['cutoff_rank']) * 100,
                    'average_package': college_data['average_package'],
                    'highest_package': college_data['highest_package'],
                    'annual_fee': best_branch['annual_fee'],
                    'rating': college_data['rating'],
                    'location': college_data['location'],
                    'eligible_branches_count': len(college_data['eligible_branches'])
                }

                score_result = recommender.calculate_college_score(recommendation_input, user_preferences)
                college_data['recommendation_score'] = score_result['total_score']
                college_data['score_breakdown'] = score_result['breakdown']

                eligible_colleges.append(college_data)

        session.close()

        # Sort colleges by recommendation score (ML-based ranking)
        eligible_colleges.sort(key=lambda x: x['recommendation_score'], reverse=True)

        return jsonify({
            'rank': rank,
            'category': category,
            'eligible_colleges': eligible_colleges,
            'total_colleges': len(eligible_colleges),
            'total_branches': sum(len(c['eligible_branches']) for c in eligible_colleges)
        })

    except Exception as e:
        print(f"Error in predict_colleges: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Ensure CORS is configured correctly
# In production, you might want to restrict origins to your Vercel domain
# For now, allow all origins (you can restrict later)
CORS(app, resources={r"/*": {"origins": "*"}})


if __name__ == '__main__':
    print("Starting NSquire Chatbot with SQL Database...")
    print("Database: colleges.db")

    # Get port from environment variable (Railway provides this)
    port = int(os.environ.get('PORT', 5001))
    print(f"Server: http://0.0.0.0:{port}")

    # Set debug=False for production
    is_production = os.environ.get('FLASK_ENV') == 'production'
    app.run(debug=not is_production, host='0.0.0.0', port=port)
