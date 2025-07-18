# Architecture Design

## System Overview
**System Name:** HEXACO Telegram Bot  
**Architecture Version:** 1.1  
**Last Updated:** May 31, 2024  

## Architectural Goals and Constraints

### Goals
- **Simplicity:** Clean, maintainable monolithic architecture
- **Reliability:** Robust error handling and data persistence
- **Performance:** Sub-2-second response times for all interactions
- **Scalability:** Support for 50+ concurrent test sessions
- **Security:** Local data storage with secure bot token management
- **Modularity:** Easy to extend for additional psychological tests (Demonstrated by successful integration of multiple diverse tests: HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M)

### Constraints
- **Local Deployment:** No cloud services, Windows environment only
- **Single Developer:** Code must be self-documenting and maintainable
- **Budget:** Free tools and libraries only
- **Dependencies:** Minimal external dependencies beyond Telegram API
- **Language:** Russian interface, English code documentation

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Test Telegram Bot                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Telegram      │  │   Bot Handler   │  │  Scoring Engine │ │
│  │   Bot API       │◄─┤  (Question &    ├─►│  (Multi-Test    │ │
│  │                 │  │   Auth Logic)   │  │   Scorers)      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                       │                    │       │
│           │                       ▼                    │       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Session       │  │   Data Access   │  │  Database      │ │
│  │   Manager       │◄─┤  (Database Mgr) ├─►│   (SQLite)      │ │
│  │ (In-Memory)     │  │                 │  │   Multi-Test    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Backend Framework
- **Language:** Python 3.7+ (Currently developed/tested with Python 3.11)
- **Bot Framework:** pyTelegramBotAPI (telebot)
- **Version:** Latest stable
- **Justification:** High trust score, active community, comprehensive features

#### Database
- **Engine:** SQLite 3
- **ORM/Access:** Raw SQL with python `sqlite3` module
- **Rationale:** Lightweight, serverless, suitable for local deployment and current project scale.
- **File Location:** Determined by `DATABASE_PATH` in `config/settings.py` (defaults to `./data/hexaco_bot.db` relative to execution path)

#### Infrastructure
- **Deployment:** Local Windows machine
- **Process Management:** Direct Python execution
- **Configuration:** Environment variables (.env file)
- **Logging:** Python logging module with file output

## Component Architecture

### 1. Bot Handler Layer (Mainly `QuestionHandler`)
**Purpose:** Manages all Telegram interactions, user registration, test selection, question flow, and initial response handling.
**Location:** `src/handlers/question_handler.py`

#### Components & Responsibilities:
- **User Authentication/Registration Logic:** Handles `/start`, collects user details (name, gender) and stores them.
- **Test Flow Management:** 
    - Presents a menu of available (uncompleted) tests.
    - Initiates the selected test flow (HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M).
    - Manages the sequence of questions for the current test.
    - Displays questions with appropriate answer formats (Likert scales, specific options) using inline keyboards.
    - Tracks progress within the current test (e.g., "Question X of Y").
- **CallbackQuery Handling:** Processes user answers from inline buttons.
- **Interaction with SessionManager:** Retrieves and updates user session data (current test, responses, completed status).
- **Interaction with Scoring Modules:** Triggers score calculation upon test completion.
- **Result Presentation:** Formats and sends test results messages to the user.
- **Error Handling:** Provides user-friendly error messages for common issues (e.g., session errors, incomplete data).

### 2. Session Manager (`SessionManager` class & `UserSession` dataclass)
**Purpose:** Manages user-specific session data in memory.
**Location:** `src/session/session_manager.py`

#### Components & Responsibilities:
- **`SessionManager`:**
    - Stores and retrieves `UserSession` objects for each active user (dictionary keyed by `user_id`).
    - Creates new sessions for new users or upon request.
    - Provides methods to update session state (e.g., current test type, current question number, responses, test completion status).
- **`UserSession` (dataclass):**
    - Holds all session-specific data for a user:
        - `session_id` (UUID)
        - `user_id`
        - `state` (current point in the bot interaction, e.g., `registration_gender`, `testing`, `menu`)
        - `registration_data` (temporary storage during registration)
        - `current_test_type` (e.g., 'hexaco', 'sds')
        - `current_question` (number for the `current_test_type`)
        - `responses` (dictionary mapping test_type to a dictionary of {question_num: answer})
        - `test_completed` (dictionary mapping test_type to a boolean indicating completion)
        - `last_interaction_time`
- **Data Persistence:** Session data is primarily in-memory. The `test_sessions` table in the database can serve for long-term audit or if persistent session state across bot restarts is strictly needed (currently, it stores basic session start/end). Raw responses and final scores are persisted in the `results` table.

### 3. Scoring Engine Modules (Individual Scorer Classes)
**Purpose:** Calculate scores and generate interpretations for each psychological test based on its specific methodology.
**Location:** `src/scoring/` (e.g., `hexaco_scorer.py`, `sds_scorer.py`, etc.)

#### Components & Responsibilities (General for each Scorer, e.g., `HexacoScorer`, `SdsScorer`):
- **Score Calculation Logic:** Implements the specific algorithm for its test (e.g., handling direct/reverse items, summing subscales, calculating indices).
    - Example `HexacoScorer`: Calculates 6 main factors, facets, and Altruism.
    - Example `SdsScorer`: Calculates Self-Contact, Choiceful Action, SDS Index.
    - Example `PanasScorer`: Calculates Positive Affect and Negative Affect.
- **Result Formatting:** Creates a user-friendly message string containing the calculated scores and a brief interpretation.
- **Response Conversion:** May provide methods to convert raw responses to a storable format (e.g., JSON for `responses` column).

### 4. Data Access Layer (`DatabaseManager` class)
**Purpose:** Handles all SQLite database operations, including schema creation/management and CRUD operations for users and test results.
**Location:** `src/data/database.py`

#### Components & Responsibilities:
- **Connection Management:** Provides database connections.
- **Schema Initialization:** Creates tables (`users`, `test_sessions`, `results`) if they don't exist, including constraints and indexes.
- **User Data Management:** Creates and retrieves user records.
- **Test Session Data Management (Basic):** Creates records in `test_sessions` (primarily for linking results if needed).
- **Test Result Management:** Saves detailed test results, including `user_id`, `test_type`, raw `responses` (JSON), and calculated `scores_json` for each completed test part.
- **Data Retrieval:** Provides methods to fetch results for specific users or test types.

## Database Design

### Entity Relationship Diagram (Conceptual)
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │  test_sessions  │       │     results     │
│ (user_id PK)    │◄───┬──┤(session_id PK)  │◄───┬──┤ (result_id PK)│
├─────────────────┤   (1) │ user_id (FK)    │   (1) │ session_id (FK) │
│ username        │       ├─────────────────┤       │ user_id (FK)    │
│ first_name      │       │ status          │       │ test_type       │
│ last_name       │       │ started_at      │       │ responses (JSON)│
│ gender          │       │ completed_at    │       │ scores_json(JSON)│
│ created_at      │       └─────────────────┘       │ created_at      │
│ updated_at      │                                 └─────────────────┘
└─────────────────┘
(1 user can have N sessions, 1 session can have N results if tests are modularly saved, though current logic is 1 result per test type per session instance in UserSession)
```
Note: The `test_sessions` table is less central to the active test flow now, as `UserSession` in memory holds more detailed state. `results` are tied to `user_id` and `test_type`.

### Table Schemas (as per `database.py`)

#### `users`
```sql
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `test_sessions` (Primarily for historical reference/linking if needed)
```sql
CREATE TABLE IF NOT EXISTS test_sessions (
    session_id TEXT PRIMARY KEY, -- Corresponds to UserSession.session_id
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'abandoned')), -- General engagement status
    current_question INTEGER DEFAULT 1, -- Potentially deprecated as this is per-test in UserSession
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

#### `results`
```sql
CREATE TABLE IF NOT EXISTS results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL, -- Links to a UserSession instance via its session_id
    user_id INTEGER NOT NULL,
    test_type TEXT NOT NULL CHECK (test_type IN ('hexaco', 'sds', 'svs', 'panas', 'self_efficacy', 'pid5bfm')),
    honesty_humility REAL, -- HEXACO specific, nullable
    emotionality REAL, -- HEXACO specific, nullable
    extraversion REAL, -- HEXACO specific, nullable
    agreeableness REAL, -- HEXACO specific, nullable
    conscientiousness REAL, -- HEXACO specific, nullable
    openness REAL, -- HEXACO specific, nullable
    altruism REAL, -- HEXACO specific, nullable
    self_contact REAL, -- SDS specific, nullable
    choiceful_action REAL, -- SDS specific, nullable
    sds_index REAL, -- SDS specific, nullable
    scores_json TEXT, -- JSON string of all calculated scores for the test_type
    responses TEXT NOT NULL, -- JSON string of raw user answers for the test_type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES test_sessions (session_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

## Data Flow Diagram

### User Registration & Initial Test Selection Flow
```
User → /start → QuestionHandler (Auth) → Collects Name/Gender → Stores in UserSession & DB (users table)
  ↓
(If registered) → QuestionHandler (Test Flow) → Retrieves UserSession.test_completed
  ↓
(If multiple tests available) → Display Test Selection Menu (Inline Keyboard)
  ↓
User Selects Test → Callback to QuestionHandler → Updates UserSession.current_test_type → Start Specific Test Intro
  ↓
(If one test available) → QuestionHandler → Updates UserSession.current_test_type → Start Specific Test Intro
```

### Test Execution Flow (Generic for any selected test)
```
Start Specific Test Intro (e.g., _send_hexaco_intro) → User clicks "Start Test" button
     ↓
Callback to QuestionHandler (e.g., _handle_start_hexaco_test_callback)
     ↓
Updates UserSession (current_question=1, responses[test_type]={}) → Show First Question (_show_question)
     ↓
User Answer (Inline Button) → Callback to QuestionHandler (_handle_answer_callback)
     ↓
Delete previous question message → Save response in UserSession.responses[test_type]
     ↓
Increment UserSession.current_question → Show Next Question OR Complete Test
     ↓ (Loop until all questions answered)
_complete_test_part → Calls Specific Scorer (e.g., hexaco_scorer.calculate_scores)
     ↓
Scorer returns results → Format results message → Send to User
     ↓
Save results to DB (results table: user_id, test_type, responses, scores_json) → Mark test as completed in UserSession.test_completed[test_type]
     ↓
Offer next test selection or end message
```

### Score Calculation Flow (Conceptual, within each Scorer)
```
Raw Answers for a Test (from UserSession.responses[test_type])
     ↓
Specific Scorer (e.g., SdsScorer.calculate_scores)
     ↓
Apply Test-Specific Logic (e.g., reverse coding, subscale summation, index calculation)
     ↓
Return Calculated Scores (dictionary)
```

## Component Interactions

### Message Processing Workflow
1. **Telegram API** receives user message
2. **Bot Handler** parses message and determines handler
3. **Session Manager** retrieves/updates session state
4. **Business Logic** processes request (registration, test, results)
5. **Data Access Layer** performs database operations
6. **Response Generation** creates Telegram response
7. **Bot Handler** sends response via Telegram API

### Error Handling Strategy
- **Input Validation:** Validate all user inputs before processing
- **Database Errors:** Graceful degradation with retry mechanisms
- **API Errors:** Handle Telegram API rate limits and timeouts
- **Session Recovery:** Automatic session restoration on bot restart
- **User Feedback:** Clear error messages in Russian

## Security Architecture

### Data Protection
- **Local Storage:** All sensitive data stored locally in SQLite
- **No Cloud Dependencies:** Zero external data transmission except Telegram API
- **Encryption:** Bot token stored in environment variables
- **Access Control:** Database file permissions restricted

### Input Validation
- **SQL Injection Prevention:** Parameterized queries only
- **Data Sanitization:** All user inputs validated and sanitized
- **Session Validation:** UUID-based session identifiers
- **Rate Limiting:** Built-in Telegram API rate limiting

## Performance Considerations

### Response Time Optimization
- **Database Indexing:** Indices on frequently queried columns
- **Connection Pooling:** Single persistent database connection
- **Memory Management:** Efficient session state handling
- **Caching Strategy:** In-memory caching for HEXACO questions

### Scalability Measures
- **Concurrent Sessions:** Support for 50+ simultaneous users
- **Database Performance:** Optimized queries and schema design
- **Memory Usage:** Minimal memory footprint per session
- **Resource Monitoring:** Logging for performance analysis

## Deployment Architecture

### Local Deployment Model
```
Windows Machine
├── Python Environment
│   ├── hexaco_bot/
│   │   ├── src/
│   │   ├── data/
│   │   ├── logs/
│   │   └── config/
│   └── .env (Bot Token)
└── SQLite Database (./data/hexaco_bot.db)
```

### File Structure
```
hexaco_bot/
├── src/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start_handler.py
│   │   ├── registration_handler.py
│   │   ├── test_handler.py
│   │   └── results_handler.py
│   ├── session/
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   └── progress_tracker.py
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── hexaco_calculator.py
│   │   └── score_interpreter.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── database_manager.py
│   │   └── repositories.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── main.py
├── data/
│   ├── hexaco_bot.db
│   ├── questions.json
│   └── scoring_rules.json
├── logs/
│   └── bot.log
├── config/
│   └── settings.py
├── tests/
│   ├── test_scoring.py
│   ├── test_handlers.py
│   └── test_database.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Quality Attributes

### Maintainability
- **Modular Design:** Clear separation of concerns
- **Code Documentation:** Comprehensive docstrings and comments
- **Type Hints:** Python type annotations for better IDE support
- **Testing Strategy:** Unit tests for critical components

### Reliability
- **Error Recovery:** Graceful handling of all error scenarios
- **Data Persistence:** Automatic session and result persistence
- **Logging:** Comprehensive logging for debugging and monitoring
- **Backup Strategy:** Regular database backups

### Usability
- **Intuitive Interface:** Clear Russian language instructions
- **Progress Feedback:** Visual progress indicators during test
- **Error Messages:** User-friendly error explanations
- **Help System:** Built-in help and guidance

## Integration Points

### Telegram Bot API Integration
- **Webhook vs Polling:** Polling mode for local deployment
- **Message Types:** Text messages, inline keyboards, callback queries
- **Rate Limiting:** Respect Telegram API rate limits (30 requests/second)
- **Error Handling:** Retry mechanisms for failed API calls

### Database Integration
- **Connection Management:** Single persistent connection
- **Transaction Handling:** ACID compliance for critical operations
- **Schema Migration:** Version-controlled database updates
- **Backup Integration:** Automated backup mechanisms

---
*Architecture Design completed: May 31, 2024*
*Status: Ready for implementation* 