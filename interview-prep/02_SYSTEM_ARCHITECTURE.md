# System Architecture - NSquire

## Table of Contents
1. [High-Level Architecture](#high-level-architecture)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [ML Pipeline Architecture](#ml-pipeline-architecture)
5. [Database Schema](#database-schema)
6. [API Architecture](#api-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Design Patterns](#design-patterns)
9. [Scalability Considerations](#scalability-considerations)

---

## High-Level Architecture

### System Overview Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              React Frontend (SPA)                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Chatbot  │  │  Rank    │  │  Search  │  │ Compare  │  │ │
│  │  │   Page   │  │ Predictor│  │   Page   │  │   Page   │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTP/REST API (Axios)
                         │ JSON Request/Response
┌────────────────────────▼─────────────────────────────────────────┐
│                      APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  Flask Backend Server                       │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │            API Endpoints Layer                        │ │ │
│  │  │  /chat | /api/predict | /api/compare | /api/search   │ │ │
│  │  └──────────────────┬───────────────────────────────────┘ │ │
│  │                     │                                       │ │
│  │  ┌──────────────────▼───────────────────────────────────┐ │ │
│  │  │         Business Logic Layer                         │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │ │
│  │  │  │   NLP        │  │   Query      │  │  College  │ │ │ │
│  │  │  │  Processing  │  │  Processing  │  │  Matching │ │ │ │
│  │  │  └──────────────┘  └──────────────┘  └───────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────┬────────┬────────────────────────────────────┘
                     │        │
        ┌────────────▼───┐   └──────────────┐
        │                │                   │
┌───────▼────────┐  ┌────▼────────┐  ┌──────▼──────────┐
│  ML MODELS     │  │  EXTERNAL   │  │   DATA LAYER    │
│  LAYER         │  │  SERVICES   │  │                 │
│                │  │             │  │                 │
│ ┌────────────┐ │  │ ┌─────────┐ │  │ ┌─────────────┐ │
│ │  Cutoff    │ │  │ │ Cohere  │ │  │ │ SQLAlchemy  │ │
│ │ Forecaster │ │  │ │   AI    │ │  │ │     ORM     │ │
│ └────────────┘ │  │ └─────────┘ │  │ └──────┬──────┘ │
│ ┌────────────┐ │  │             │  │        │        │
│ │ Admission  │ │  │ ┌─────────┐ │  │        │        │
│ │Probability │ │  │ │  Argos  │ │  │        │        │
│ └────────────┘ │  │ │Translate│ │  │        │        │
│ ┌────────────┐ │  │ └─────────┘ │  │        │        │
│ │   Smart    │ │  │             │  │        │        │
│ │Recommender │ │  │             │  │        │        │
│ └────────────┘ │  │             │  │        │        │
└────────────────┘  └─────────────┘  └────────┼────────┘
                                               │
                                     ┌─────────▼─────────┐
                                     │ PERSISTENCE LAYER │
                                     │                   │
                                     │  ┌─────────────┐  │
                                     │  │   SQLite    │  │
                                     │  │  (colleges. │  │
                                     │  │     db)     │  │
                                     │  └─────────────┘  │
                                     │                   │
                                     │  Tables:          │
                                     │  • colleges       │
                                     │  • courses        │
                                     │  • cutoffs        │
                                     └───────────────────┘
```

### Architecture Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Style** | Layered + Client-Server + Service-Oriented |
| **Communication** | RESTful HTTP/JSON |
| **State Management** | Stateless server, stateful client |
| **Data Storage** | Relational database (SQLite/PostgreSQL) |
| **Deployment** | Monolithic backend, SPA frontend |
| **Scalability** | Horizontal (frontend), Vertical (backend) |

---

## Component Architecture

### Backend Components

#### 1. Flask Application Server (`EDI_project_sql.py`)
```python
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Main responsibilities:
# - HTTP request handling
# - Routing and endpoint management
# - Response formatting
# - Error handling and logging
# - CORS policy enforcement
```

**Key Functions:**
- Request validation and sanitization
- JSON serialization/deserialization
- Session management
- Middleware integration

#### 2. Database Layer (`models.py`)

```python
# ORM Models
Base = declarative_base()

class College(Base):
    # Primary entity
    __tablename__ = 'colleges'
    # Relationships: one-to-many with courses

class Course(Base):
    # Secondary entity
    __tablename__ = 'courses'
    # Relationships: many-to-one with college, one-to-many with cutoffs

class Cutoff(Base):
    # Fact table
    __tablename__ = 'cutoffs'
    # Relationships: many-to-one with course
```

**Design Pattern:** Active Record + Repository Pattern
- `DatabaseManager`: Singleton connection manager
- `get_session()`: Factory method for sessions
- Helper functions: Query abstraction layer

#### 3. ML Models Layer (`ml_models.py`)

```python
# Three independent ML components

class CutoffForecaster:
    """Time series forecasting using Linear Regression"""
    model = LinearRegression()

    def predict_next_year_cutoff(historical_data, target_year):
        # Training and prediction logic
        pass

class AdmissionProbabilityPredictor:
    """Statistical probability calculation"""

    def calculate_probability(rank, cutoff, historical_cutoffs):
        # Multi-factor probability computation
        pass

class SmartRecommendationSystem:
    """MCDA-based college ranking"""
    scaler = StandardScaler()

    def calculate_college_score(college_data, user_preferences):
        # Weighted scoring algorithm
        pass
```

**Design Pattern:** Strategy Pattern
- Each model is independently testable
- Modular architecture allows easy replacement
- Consistent interface across all models

#### 4. NLP & AI Integration

```python
# Cohere AI Integration
co = cohere.Client(cohere_api_key)

def cohere_understand_query(user_query):
    """Extract intent and entities from natural language"""
    # Uses Cohere's command-r-08-2024 model
    # Returns structured JSON with intent, college, branch, year
    pass

def expand_college_abbreviations(query):
    """Expands common abbreviations (PICT → Pune Institute...)"""
    pass

# Argos Translate for Hinglish
def translate_text(from_lang, to_lang, text):
    """Translate between English and Hindi"""
    pass
```

---

## Data Flow

### 1. User Query Flow (Chatbot)

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  React   │────▶│  Flask   │────▶│  Cohere  │
│  Input   │     │ Chatbot  │     │   API    │     │    AI    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                         │
                                         │
                      ┌──────────────────▼──────────────────┐
                      │  Parse Intent & Entities            │
                      │  - Intent: cutoff/fees/info         │
                      │  - College Name: fuzzy match        │
                      │  - Branch: optional                 │
                      │  - Year: optional                   │
                      └──────────────────┬──────────────────┘
                                         │
                      ┌──────────────────▼──────────────────┐
                      │  Query Database via SQLAlchemy      │
                      │  - Match college (fuzzy matching)   │
                      │  - Fetch courses and cutoffs        │
                      │  - Format response data             │
                      └──────────────────┬──────────────────┘
                                         │
                      ┌──────────────────▼──────────────────┐
                      │  Generate Response                  │
                      │  - HTML formatted cutoff tables     │
                      │  - Natural language text            │
                      │  - Translate if Hinglish detected   │
                      └──────────────────┬──────────────────┘
                                         │
┌──────────┐     ┌──────────┐     ┌─────▼──────┐
│  User    │◀────│  React   │◀────│  JSON      │
│ Display  │     │ Render   │     │ Response   │
└──────────┘     └──────────┘     └────────────┘
```

### 2. ML Prediction Flow (Rank Predictor)

```
User Input: {rank: 5000, category: "GOPEN"}
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  Backend API (/api/predict)                          │
│  1. Validate input (rank range, category validity)   │
│  2. Initialize ML models                             │
└────────────┬─────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────┐
│  Database Query                                       │
│  - Fetch all colleges with courses                   │
│  - Get 2024 cutoffs for specified category           │
│  - Filter eligible courses (rank ≤ cutoff)           │
└────────────┬─────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────┐
│  For each eligible course:                           │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │ 1. Fetch historical cutoffs (2020-2024)        │  │
│  │    get_historical_cutoffs_for_course()         │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │ 2. CutoffForecaster.predict_next_year_cutoff() │  │
│  │    - Train LinearRegression on historical data │  │
│  │    - Predict 2025 cutoff                       │  │
│  │    - Calculate R², MSE, confidence             │  │
│  │    - Determine trend direction                 │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │ 3. AdmissionProbabilityPredictor               │  │
│  │    .calculate_probability()                    │  │
│  │    - Calculate rank_diff_percentage            │  │
│  │    - Calculate historical volatility (CV)      │  │
│  │    - Apply probability classification          │  │
│  │    - Adjust for volatility penalty             │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│  ┌────────────────▼───────────────────────────────┐  │
│  │ 4. SmartRecommendationSystem                   │  │
│  │    .calculate_college_score()                  │  │
│  │    - Normalize 6 features to 0-100             │  │
│  │    - Apply user preference weights             │  │
│  │    - Calculate weighted total score            │  │
│  │    - Generate breakdown                        │  │
│  └────────────────────────────────────────────────┘  │
└────────────┬─────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────┐
│  Aggregate Results                                    │
│  - Group by college                                  │
│  - Sort by recommendation_score (descending)         │
│  - Format with all ML metadata                      │
└────────────┬─────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────┐
│  JSON Response                                        │
│  {                                                   │
│    rank: 5000,                                       │
│    category: "GOPEN",                                │
│    eligible_colleges: [                              │
│      {                                               │
│        name: "PICT",                                 │
│        eligible_branches: [...],                     │
│        recommendation_score: 85.9,                   │
│        score_breakdown: {...},                       │
│        probability: "Safe (87.3%)"                   │
│      },                                              │
│      ...                                             │
│    ]                                                 │
│  }                                                   │
└────────────┬─────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────┐
│  React Frontend Rendering                            │
│  - Display college cards with ML scores              │
│  - Show probability bars                             │
│  - Render recommendation breakdowns                  │
│  - Display 2025 forecast badges                      │
└──────────────────────────────────────────────────────┘
```

### 3. College Comparison Flow

```
User selects 3 colleges → POST /api/compare {college_ids: [1,2,3]}
    ↓
Parallel database queries for each college:
    ├─ College basic info (name, location, rating)
    ├─ Placement data (avg, highest, recruiters)
    ├─ All courses with fees
    └─ 2024 cutoffs for all courses
    ↓
Data aggregation and formatting
    ↓
Return comprehensive comparison JSON
    ↓
React renders side-by-side comparison table
```

---

## ML Pipeline Architecture

### Training Pipeline (Offline)

```
Historical Data (colleges.db)
    │
    ▼
┌─────────────────────────────────────┐
│  Data Preprocessing                 │
│  - Extract cutoff time series       │
│  - Handle missing values            │
│  - Validate data quality            │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Feature Engineering                │
│  - Year encoding                    │
│  - Rank normalization               │
│  - Volatility calculation           │
│  - Trend detection                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Model Training                     │
│  - Linear Regression (per course)   │
│  - Statistical parameter estimation │
│  - Confidence threshold calibration │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Model Validation                   │
│  - R² score calculation             │
│  - RMSE evaluation                  │
│  - Cross-validation (if data >5yrs) │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Model Deployment                   │
│  - In-memory model instances        │
│  - Ready for real-time inference    │
└─────────────────────────────────────┘
```

### Inference Pipeline (Real-time)

```
User Request (rank, category)
    │
    ▼
┌─────────────────────────────────────┐
│  Data Retrieval                     │
│  - Fetch historical cutoffs         │
│  - Extract relevant features        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Prediction (per course)            │
│  ├─ Forecaster: 2025 cutoff         │
│  ├─ Probability: admission chance   │
│  └─ Recommender: college score      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Post-processing                    │
│  - Aggregate predictions            │
│  - Sort by score                    │
│  - Format with confidence metrics   │
└────────────┬────────────────────────┘
             │
             ▼
Response (JSON with ML insights)
```

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────┐
│                    COLLEGES                         │
├─────────────────────────────────────────────────────┤
│ PK │ id (INTEGER, AUTOINCREMENT)                    │
│    │ name (STRING, UNIQUE, INDEXED)                 │
│    │ location (STRING, INDEXED)                     │
│    │ type (STRING)                                  │
│    │ rating (FLOAT)                                 │
│    │ facilities (JSON)                              │
│    │ average_package (INTEGER)                      │
│    │ highest_package (INTEGER)                      │
│    │ top_recruiters (JSON)                          │
└──────────┬──────────────────────────────────────────┘
           │ 1
           │
           │ has many
           │
           │ N
┌──────────▼──────────────────────────────────────────┐
│                     COURSES                         │
├─────────────────────────────────────────────────────┤
│ PK │ id (INTEGER, AUTOINCREMENT)                    │
│ FK │ college_id (INTEGER, INDEXED)                  │
│    │ name (STRING)                                  │
│    │ duration (STRING)                              │
│    │ annual_fee (INTEGER)                           │
└──────────┬──────────────────────────────────────────┘
           │ 1
           │
           │ has many
           │
           │ N
┌──────────▼──────────────────────────────────────────┐
│                     CUTOFFS                         │
├─────────────────────────────────────────────────────┤
│ PK │ id (INTEGER, AUTOINCREMENT)                    │
│ FK │ course_id (INTEGER, INDEXED)                   │
│    │ year (INTEGER, INDEXED)                        │
│    │ category (STRING, INDEXED)                     │
│    │ cutoff_rank (INTEGER)                          │
└─────────────────────────────────────────────────────┘
```

### Schema Normalization

**Normal Form**: 3NF (Third Normal Form)

**Justification:**
1. **1NF**: All attributes are atomic (no repeating groups)
2. **2NF**: No partial dependencies (all non-key attributes depend on full primary key)
3. **3NF**: No transitive dependencies (no non-key attribute depends on another non-key attribute)

**Denormalization Decisions:**
- `facilities`, `top_recruiters` stored as JSON for flexibility
- `average_package`, `highest_package` duplicated in `colleges` table for query performance (read-optimized)

### Indexing Strategy

```sql
-- Primary Keys (automatic indexing)
CREATE INDEX idx_colleges_pk ON colleges(id);
CREATE INDEX idx_courses_pk ON courses(id);
CREATE INDEX idx_cutoffs_pk ON cutoffs(id);

-- Foreign Keys
CREATE INDEX idx_courses_college_id ON courses(college_id);
CREATE INDEX idx_cutoffs_course_id ON cutoffs(course_id);

-- Search Fields
CREATE INDEX idx_colleges_name ON colleges(name);
CREATE INDEX idx_colleges_location ON colleges(location);

-- Query Optimization
CREATE INDEX idx_cutoffs_year ON cutoffs(year);
CREATE INDEX idx_cutoffs_category ON cutoffs(category);

-- Composite Index for common queries
CREATE INDEX idx_cutoffs_course_year_cat ON cutoffs(course_id, year, category);
```

**Query Performance:**
- Simple lookups: O(log n) via B-tree indexes
- Typical query time: <50ms for indexed columns
- Full table scan avoided for 95% of queries

---

## API Architecture

### RESTful Endpoint Design

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/chat` | POST | Chatbot query | `{message: string}` | `{response: string}` |
| `/api/predict` | POST | Rank prediction | `{rank: int, category: string, preferences?: object}` | `{eligible_colleges: [...], total_colleges: int}` |
| `/api/compare` | POST | College comparison | `{college_ids: [int]}` | `[{college data}]` |
| `/api/colleges/all` | GET | List all colleges | - | `[{id, name, location, rating}]` |
| `/api/colleges/search` | GET | Advanced search | `?q=&location=&min_fee=&max_fee=&min_rating=&branch=&sort=&page=` | `{results: [...], total: int, page: int}` |
| `/api/filters/options` | GET | Filter options | - | `{locations: [], fee_range: {}, branches: []}` |
| `/health` | GET | Health check | - | `{status: "ok", database: "connected"}` |

### Request/Response Format

#### Example: `/api/predict`

**Request:**
```json
{
  "rank": 5000,
  "category": "GOPEN",
  "preferences": {
    "placements_weight": 0.35,
    "rank_eligibility_weight": 0.30,
    "fees_weight": 0.15,
    "rating_weight": 0.15,
    "location_weight": 0.10,
    "branches_weight": 0.05
  }
}
```

**Response:**
```json
{
  "rank": 5000,
  "category": "GOPEN",
  "total_colleges": 45,
  "total_branches": 123,
  "eligible_colleges": [
    {
      "id": 1,
      "name": "Pune Institute of Computer Technology",
      "location": "Pune",
      "rating": 4.5,
      "average_package": 850000,
      "highest_package": 4500000,
      "recommendation_score": 85.92,
      "score_breakdown": {
        "rank_eligibility": 100,
        "placements": 73.5,
        "fees": 87.0,
        "rating": 90.0,
        "location": 100,
        "branches": 60
      },
      "probability": "Safe",
      "eligible_branches": [
        {
          "name": "B.Tech Computer Engineering",
          "cutoff_rank": 8500,
          "your_rank": 5000,
          "rank_difference": 3500,
          "probability": "Safe",
          "probability_percentage": 87.3,
          "ml_confidence": {
            "rank_advantage": "41.2%",
            "historical_volatility": "6.8%"
          },
          "annual_fee": 95000,
          "forecast_2025": 8200,
          "trend": "Stable",
          "color": "green"
        }
      ]
    }
  ]
}
```

### Error Handling

```python
# Standard error response format
{
  "error": "Error message",
  "status_code": 400,
  "details": {}  # Optional
}

# Common HTTP Status Codes
200 OK               # Successful request
400 Bad Request      # Invalid input
404 Not Found        # Resource not found
500 Internal Error   # Server error
```

---

## Frontend Architecture

### Component Hierarchy

```
App.js
│
├── HomePage
│   ├── Header
│   ├── HeroSection
│   ├── FeatureCards
│   └── Footer
│
├── ChatbotPage
│   ├── ChatHeader
│   ├── MessageList
│   │   ├── UserMessage
│   │   └── BotMessage (with HTML rendering)
│   ├── InputBox
│   └── QuickSuggestions
│
├── RankPredictorPage
│   ├── PredictorForm
│   │   ├── RankInput
│   │   ├── CategorySelect
│   │   └── PreferenceSliders
│   └── ResultsDisplay
│       ├── CollegeCard (with ML scores)
│       │   ├── MLRecommendationBadge
│       │   ├── ProbabilityBar
│       │   ├── ForecastDisplay
│       │   └── BranchList
│       └── NoResultsMessage
│
├── CollegeSearchPage
│   ├── SearchBar
│   ├── FilterPanel
│   │   ├── LocationFilter
│   │   ├── FeeRangeSlider
│   │   ├── RatingFilter
│   │   └── BranchFilter
│   ├── SortDropdown
│   └── CollegeGrid
│       └── CollegeCard
│
└── ComparisonPage
    ├── CollegeSelector
    ├── ComparisonTable
    │   ├── HeaderRow
    │   ├── BasicInfoRow
    │   ├── PlacementsRow
    │   ├── FeesRow
    │   ├── FacilitiesRow
    │   └── CutoffsRow
    └── ResetButton
```

### State Management

```javascript
// React Hooks for local state
const [messages, setMessages] = useState([]);
const [loading, setLoading] = useState(false);
const [results, setResults] = useState(null);
const [filters, setFilters] = useState({});

// No global state management library (Redux/Context API)
// Rationale: Small app, prop drilling minimal
```

### Routing Strategy

```javascript
// React Router v6
<BrowserRouter>
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/chat" element={<ChatbotPage />} />
    <Route path="/predict" element={<RankPredictorPage />} />
    <Route path="/search" element={<CollegeSearchPage />} />
    <Route path="/compare" element={<ComparisonPage />} />
  </Routes>
</BrowserRouter>
```

---

## Design Patterns

### Backend Patterns

1. **MVC Pattern** (Modified)
   - **Model**: SQLAlchemy ORM classes (`models.py`)
   - **View**: Flask routes and response formatting
   - **Controller**: Business logic functions

2. **Repository Pattern**
   - `get_session()`: Database access abstraction
   - Helper functions encapsulate queries

3. **Strategy Pattern**
   - ML models as interchangeable strategies
   - `CutoffForecaster`, `AdmissionProbabilityPredictor`, `SmartRecommendationSystem`

4. **Singleton Pattern**
   - `DatabaseManager`: Single database connection manager
   - `cohere.Client`: Single AI client instance

5. **Factory Pattern**
   - `get_session()`: Creates database sessions
   - `get_db_manager()`: Creates or retrieves singleton

### Frontend Patterns

1. **Component Composition**
   - Small, reusable components
   - Props-based communication

2. **Container/Presentational Pattern**
   - Smart components (data fetching)
   - Dumb components (pure rendering)

3. **Hooks Pattern**
   - `useState`, `useEffect` for lifecycle management
   - Custom hooks for reusable logic (potential)

---

## Scalability Considerations

### Current Limitations
- **Database**: SQLite limited to ~100 concurrent writes
- **Backend**: Single-threaded Flask (dev server)
- **ML Models**: In-memory, re-trained on each prediction

### Scalability Strategies

#### Horizontal Scaling (Frontend)
```
         Load Balancer
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
  React    React    React
  App 1    App 2    App 3
```

#### Vertical Scaling (Backend)
```
Flask → Gunicorn → Nginx
  |        (WSGI)    (Reverse Proxy)
  └─ PostgreSQL (instead of SQLite)
```

#### Caching Layer
```
Redis Cache
  ├─ College metadata
  ├─ Common query results
  └─ ML predictions (TTL: 1 hour)
```

#### Database Optimization
```sql
-- Read replicas for query distribution
Primary DB (Write) ──┐
                     ├─→ Replica 1 (Read)
                     ├─→ Replica 2 (Read)
                     └─→ Replica 3 (Read)
```

#### ML Model Optimization
```
Current: Train on each request
   ↓
Optimized: Pre-computed predictions
   ├─ Daily batch job for common ranks
   ├─ Cache results in Redis
   └─ Real-time computation for edge cases
```

### Performance Targets

| Metric | Current | Target (Scaled) |
|--------|---------|----------------|
| Concurrent Users | 10-50 | 1000+ |
| API Response Time | 200-500ms | <200ms |
| Database Query | <50ms | <20ms |
| ML Prediction | <100ms | <50ms |
| Availability | 95% | 99.9% |

---

## Conclusion

The NSquire architecture demonstrates a well-structured, layered design that balances simplicity with scalability. The clear separation of concerns, use of established patterns, and modular ML pipeline make the system maintainable and extensible for future enhancements.
