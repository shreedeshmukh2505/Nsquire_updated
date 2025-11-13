# Architecture and Data Flow

## System Architecture Overview

NSquire follows a **3-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│                         (React Frontend)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Chatbot  │  │  Rank    │  │ Compare  │  │  Search  │       │
│  │          │  │ Predictor│  │          │  │          │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼──────────────┘
        │             │             │             │
        │        HTTP REST API (Axios)            │
        │             │             │             │
┌───────▼─────────────▼─────────────▼─────────────▼──────────────┐
│                      APPLICATION LAYER                           │
│                        (Flask Backend)                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                API Routes & Controllers                   │  │
│  │  /chat  /api/predict  /api/compare  /api/colleges/search │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                              │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │              Business Logic Layer                         │  │
│  │  • Query Processing (NLP)                                 │  │
│  │  • Fuzzy Matching                                         │  │
│  │  • Data Transformation                                    │  │
│  └────────────┬─────────────────────┬───────────────────────┘  │
│               │                     │                           │
│  ┌────────────▼──────┐  ┌──────────▼────────────────────────┐ │
│  │  Cohere AI NLP    │  │   ML Models (ml_models.py)        │ │
│  │  • Intent Extract │  │   • CutoffForecaster              │ │
│  │  • Entity Extract │  │   • AdmissionProbabilityPredictor │ │
│  │  • Translation    │  │   • SmartRecommendationSystem     │ │
│  └───────────────────┘  └───────────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────▼───────────────────────────────┐ │
│  │              SQLAlchemy ORM Layer                          │ │
│  │  • Database Abstraction                                    │ │
│  │  • Session Management                                      │ │
│  │  • Query Builder                                           │ │
│  └───────────────────────┬────────────────────────────────────┘ │
└────────────────────────────┼───────────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────────┐
│                        DATA LAYER                               │
│                    (SQLite / PostgreSQL)                        │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐           │
│  │ Colleges │◄──────┤ Courses  │◄──────┤ Cutoffs  │           │
│  │  (392)   │  1:N  │          │  1:N  │ (3,222+) │           │
│  └──────────┘       └──────────┘       └──────────┘           │
└────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. Chat Query Processing Flow

```
User Input: "What are the cutoffs for Computer Engineering in PICT?"
    │
    ▼
[React Chatbot Component]
    │
    │ POST /chat
    ▼
[Flask Chat Endpoint] (EDI_project_sql.py:587)
    │
    ▼
[detect_language()] (EDI_project_sql.py:181)
    │
    ├── English → Continue
    └── Hinglish → Set language flag
    │
    ▼
[expand_college_abbreviations()] (EDI_project_sql.py:230)
    │  "PICT" → "Pune Institute of Computer Technology"
    │
    ▼
[cohere_understand_query()] (EDI_project_sql.py:252)
    │  Prompt to Cohere AI
    │  Extract: intent, college, branch, year
    │
    ▼
[parse_cohere_response()] (EDI_project_sql.py:291)
    │  Parse AI response into entities
    │
    ▼
[match_college_name_db()] (EDI_project_sql.py:97)
    │  Fuzzy match college name
    │  Query database via SQLAlchemy
    │
    ▼
[Database Query]
    │  SELECT * FROM colleges WHERE name ILIKE '%Pune Institute%'
    │  JOIN courses ON courses.college_id = colleges.id
    │  JOIN cutoffs ON cutoffs.course_id = courses.id
    │
    ▼
[generate_dynamic_response_college()] (EDI_project_sql.py:431)
    │  Format response based on intent
    │
    ▼
[Response JSON]
    │
    ▼
[React UI Update]
    │  Display formatted response
```

---

### 2. Rank Prediction Flow (ML Pipeline)

```
User Input: Rank=5000, Category=GOPEN
    │
    ▼
[RankPredictor Component]
    │
    │ POST /api/predict
    ▼
[Flask Predict Endpoint] (EDI_project_sql.py:891)
    │
    ▼
[Validate Input]
    │  • Check rank range (1-100,000)
    │  • Validate category
    │
    ▼
[Database Query: Get All Colleges]
    │  session.query(College).all()
    │
    ▼
[For Each College → For Each Course]
    │
    ▼
[Get 2024 Cutoff]
    │  query(Cutoff).filter(
    │      course_id = X,
    │      category = GOPEN,
    │      year = 2024
    │  )
    │
    ▼
[Check Eligibility: rank <= cutoff_rank]
    │  If YES → Continue ML Analysis
    │  If NO → Skip
    │
    ▼
┌─────────────── ML PIPELINE BEGINS ───────────────┐
│                                                   │
│  [Get Historical Cutoffs] (ml_models.py:359)     │
│      │                                            │
│      ▼                                            │
│  ┌──────────────────────────────────────┐        │
│  │   1. Cutoff Forecaster                │        │
│  │   (ml_models.py:18)                   │        │
│  └──────────────┬───────────────────────┘        │
│                 │                                 │
│                 ▼                                 │
│  • Prepare time series data (years, cutoffs)     │
│  • Train LinearRegression model                  │
│  • Predict 2025 cutoff                           │
│  • Calculate R² score, MSE                       │
│  • Determine confidence: High/Medium/Low         │
│  • Calculate uncertainty range (±std_dev)        │
│                 │                                 │
│                 ▼                                 │
│  Output: {                                        │
│    predicted_cutoff: 4850,                       │
│    confidence: 'High',                           │
│    r2_score: 0.956,                              │
│    trend: 'Decreasing',                          │
│    uncertainty_range: {lower: 4700, upper: 5000} │
│  }                                                │
│                 │                                 │
│                 ▼                                 │
│  ┌──────────────────────────────────────┐        │
│  │   2. Admission Probability Predictor  │        │
│  │   (ml_models.py:168)                  │        │
│  └──────────────┬───────────────────────┘        │
│                 │                                 │
│                 ▼                                 │
│  • Calculate rank_diff_percentage                │
│  • Calculate historical volatility (CV)          │
│  • Classify into category:                       │
│      - Highly Safe (≥30% advantage)              │
│      - Safe (≥20%)                               │
│      - Probable (≥10%)                           │
│      - Moderate (≥5%)                            │
│      - Reach (<5%)                               │
│  • Apply volatility penalty                      │
│  • Calculate final probability (0-100%)          │
│                 │                                 │
│                 ▼                                 │
│  Output: {                                        │
│    probability: 87.3,                            │
│    category: 'Safe',                             │
│    confidence_factors: {                         │
│      rank_advantage: '24.5%',                    │
│      historical_volatility: '6.8%'              │
│    }                                              │
│  }                                                │
│                 │                                 │
│                 ▼                                 │
│  ┌──────────────────────────────────────┐        │
│  │   3. Smart Recommendation System      │        │
│  │   (ml_models.py:245)                  │        │
│  └──────────────┬───────────────────────┘        │
│                 │                                 │
│                 ▼                                 │
│  • Normalize 6 factors to 0-100:                 │
│      1. Rank Eligibility (weight: 30%)           │
│      2. Placements (30%)                         │
│      3. Fees (15%)                               │
│      4. Rating (15%)                             │
│      5. Location (10%)                           │
│      6. Branches (5%)                            │
│  • Calculate weighted score                      │
│  • Generate breakdown                            │
│                 │                                 │
│                 ▼                                 │
│  Output: {                                        │
│    total_score: 85.9,                            │
│    breakdown: {                                   │
│      rank_eligibility: 100,                      │
│      placements: 75,                             │
│      fees: 80,                                   │
│      rating: 86,                                 │
│      location: 50,                               │
│      branches: 60                                │
│    }                                              │
│  }                                                │
└───────────────────┬───────────────────────────────┘
                    │
                    ▼
[Aggregate Results for All Branches]
    │
    ▼
[Sort Colleges by Recommendation Score]
    │
    ▼
[Response JSON]
    │  {
    │    rank: 5000,
    │    category: 'GOPEN',
    │    eligible_colleges: [...],
    │    total_colleges: 47,
    │    total_branches: 112
    │  }
    │
    ▼
[React UI Display]
    │  • Show summary stats
    │  • Render EligibilityCard for each college
    │  • Display ML scores and probabilities
```

---

### 3. College Comparison Flow

```
User Selects: [College A, College B, College C]
    │
    ▼
[ComparisonTool Component]
    │
    │ POST /api/compare
    ▼
[Flask Compare Endpoint] (EDI_project_sql.py:823)
    │
    ▼
[Validate Input]
    │  • Min 2 colleges, max 4
    │
    ▼
[Database Query for Each College]
    │  session.query(College).filter_by(id=college_id).first()
    │
    ▼
[Join with Courses and Cutoffs]
    │  for course in college.courses:
    │      for cutoff in course.cutoffs:
    │          if cutoff.year == 2024:
    │              cutoffs_2024[cutoff.category] = cutoff.cutoff_rank
    │
    ▼
[Format Comparison Data]
    │  {
    │    id, name, location, type, rating,
    │    facilities, placements, courses
    │  }
    │
    ▼
[Response JSON Array]
    │
    ▼
[ComparisonTable Component]
    │  Side-by-side display
    │  Highlight best values
```

---

### 4. Advanced Search Flow

```
User Filters: Location=Pune, Min_Rating=4.0, Fees<150k
    │
    ▼
[CollegeSearch Component]
    │
    │ GET /api/colleges/search?location=Pune&min_rating=4.0&max_fee=150000
    ▼
[Flask Search Endpoint] (EDI_project_sql.py:712)
    │
    ▼
[Build Dynamic Query]
    │  query = session.query(College).join(Course)
    │
    ▼
[Apply Filters Sequentially]
    │  if search_query:
    │      query.filter(College.name.ilike(...))
    │  if locations:
    │      query.filter(College.location.in_(locations))
    │  if min_fee/max_fee:
    │      query.filter(Course.annual_fee.between(...))
    │  if min_rating:
    │      query.filter(College.rating >= min_rating)
    │
    ▼
[Remove Duplicates]
    │  query.distinct()
    │
    ▼
[Apply Sorting]
    │  if sort_by == 'rating':
    │      query.order_by(College.rating.desc())
    │
    ▼
[Pagination]
    │  offset = (page - 1) * per_page
    │  query.offset(offset).limit(per_page)
    │
    ▼
[Format Results]
    │  {
    │    results: [...],
    │    total: 47,
    │    page: 1,
    │    per_page: 20,
    │    total_pages: 3
    │  }
    │
    ▼
[CollegeGrid Component]
    │  Display cards with pagination controls
```

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────────┐
│         COLLEGES            │
├─────────────────────────────┤
│ PK  id (Integer)            │
│     name (String) UNIQUE    │
│     location (String)       │
│     type (String)           │
│     rating (Float)          │
│     facilities (JSON)       │
│     average_package (Int)   │
│     highest_package (Int)   │
│     top_recruiters (JSON)   │
└──────────────┬──────────────┘
               │ 1
               │
               │ N
┌──────────────▼──────────────┐
│          COURSES            │
├─────────────────────────────┤
│ PK  id (Integer)            │
│ FK  college_id (Integer)    │
│     name (String)           │
│     duration (String)       │
│     annual_fee (Integer)    │
└──────────────┬──────────────┘
               │ 1
               │
               │ N
┌──────────────▼──────────────┐
│          CUTOFFS            │
├─────────────────────────────┤
│ PK  id (Integer)            │
│ FK  course_id (Integer)     │
│     year (Integer)          │
│     category (String)       │
│     cutoff_rank (Integer)   │
└─────────────────────────────┘

INDEXES:
  - colleges.name
  - colleges.location
  - courses.college_id
  - cutoffs.course_id
  - cutoffs.year
  - cutoffs.category
```

### Relationships

1. **College → Courses** (One-to-Many)
   - One college offers multiple courses
   - `courses.college_id` foreign key to `colleges.id`
   - Cascade delete: deleting college removes all courses

2. **Course → Cutoffs** (One-to-Many)
   - One course has multiple cutoffs (per year, per category)
   - `cutoffs.course_id` foreign key to `courses.id`
   - Cascade delete: deleting course removes all cutoffs

---

## Component Architecture (Frontend)

### Component Hierarchy

```
App (Router)
    └── CollegeGuide (Layout)
        ├── Navbar
        ├── MainContent (Landing)
        ├── About
        ├── Features
        ├── Contact
        ├── Chatbot
        │   └── FloatingChat
        ├── RankPredictor
        │   ├── CategorySelector
        │   ├── RankSlider
        │   └── EligibilityCard (repeated)
        ├── ComparisonTool
        │   └── ComparisonTable
        └── CollegeSearch
            ├── SearchFilters
            ├── FilterChip (repeated)
            └── CollegeGrid (repeated)
```

### State Management

**Local Component State (useState)**
- Used for: form inputs, UI toggles, loading states
- Examples:
  - RankPredictor: `rank`, `category`, `predictions`, `loading`
  - Chatbot: `messages`, `inputValue`, `isTyping`
  - CollegeSearch: `filters`, `results`, `page`

**Props Drilling**
- Parent components pass data and callbacks to children
- Example: `RankPredictor` → `CategorySelector` (onCategoryChange)

**No Global State Management**
- Project uses simple state management (no Redux/Context)
- API responses drive state updates
- Good for medium-complexity applications

---

## API Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/chat` | POST | Process chatbot query | `{message: string}` | `{response: string}` |
| `/api/predict` | POST | Predict eligible colleges | `{rank: int, category: string}` | `{eligible_colleges: [...]}` |
| `/api/compare` | POST | Compare colleges | `{college_ids: [int]}` | `[{college_data}]` |
| `/api/colleges/all` | GET | List all colleges | - | `[{id, name, location, rating}]` |
| `/api/colleges/search` | GET | Search with filters | Query params | `{results: [...], total, page}` |
| `/api/filters/options` | GET | Get filter options | - | `{locations: [], branches: []}` |
| `/health` | GET | Health check | - | `{status: "ok"}` |

---

## Deployment Architecture

### Development
```
[React Dev Server :3000] ←→ [Flask Dev Server :5001] ←→ [SQLite DB]
```

### Production
```
[Vercel CDN] → [React Build (Static)]
                      ↓
                  [API Routes]
                      ↓
              [Railway Backend] ←→ [PostgreSQL DB]
```

---

## Security Considerations

1. **CORS Configuration**: `CORS(app)` allows cross-origin requests
2. **Input Validation**: Rank range, category validation
3. **SQL Injection Prevention**: SQLAlchemy ORM (parameterized queries)
4. **API Rate Limiting**: Consider adding for Cohere API
5. **Environment Variables**: `.env` for sensitive keys (COHERE_API_KEY)

---

## Performance Optimization Strategies

1. **Database Indexing**: Indexes on frequently queried columns
2. **Query Optimization**: Use joins instead of nested queries
3. **Pagination**: Limit results (20 per page)
4. **Connection Pooling**: SQLAlchemy pool management
5. **Frontend Optimization**: Component memoization opportunities

---

**Key Takeaway**: The architecture demonstrates clear separation of concerns, scalable database design, and integration of multiple technologies (React, Flask, ML, NLP) into a cohesive system.
