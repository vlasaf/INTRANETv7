# Requirements Specification

## Project Overview
**Project Name:** HEXACO Telegram Bot  
**Version:** 1.1  
**Date:** May 31, 2024  
**Status:** In Development  

## Stakeholders
- **Product Owner:** User (Internal Company)
- **Development Team:** Claude AI Assistant
- **End Users:** Internal company employees

## Functional Requirements

### High Priority

#### FR-001: User Registration Flow
- **Description:** Bot must collect user basic information before test
- **Details:**
  - Greeting message on /start command
  - Gender selection (Male/Female) with inline buttons
  - Name collection (First name + Last name) via text input
  - Data validation for name inputs
- **Priority:** Critical
- **Acceptance Criteria:** User cannot proceed to test without completing registration

#### FR-002: HEXACO Test Implementation
- **Description:** Implement complete 100-question HEXACO personality test
- **Details:**
  - Present exactly 100 predefined questions in Russian
  - 5-point Likert scale response system:
    - 1 – Совершенно не согласен
    - 2 – Немного не согласен
    - 3 – Нейтрально, нет мнения
    - 4 – Немного согласен
    - 5 – Совершенно согласен
  - Questions presented one by one with inline keyboard buttons
  - Progress tracking (Question X of 100)
- **Priority:** Critical
- **Acceptance Criteria:** All 100 questions completed with valid responses

#### FR-002.1: Self-Determination Scale (SDS) Test Implementation
- **Description:** Implement the Self-Determination Scale (SDS) test.
- **Details:**
  - Present 10 predefined questions in Russian.
  - Each question consists of two statements (A and B).
  - 5-point response scale to indicate which statement is more true for the user:
    - 1 – Верно только А
    - 2 – Верно скорее А
    - 3 – Оба утверждение отчасти важны
    - 4 – Верно скорее Б
    - 5 – Верно только Б
  - Questions presented one by one with inline keyboard buttons.
  - Progress tracking (Question X of 10).
- **Priority:** High
- **Acceptance Criteria:** All 10 questions completed with valid responses.

#### FR-002.2: Schwartz Value Survey (SVS) Test Implementation
- **Description:** Implement the Schwartz Value Survey (SVS) test.
- **Details:**
  - Present 57 value statements in Russian.
  - User rates the importance of each value as a guiding principle in their life.
  - Response scale from -1 to 7 (specific values: -1, 0, 3, 6, 7):
    - -1 – Противоположно моим принципам
    -  0 – Совершенно не важна
    -  3 – Важна
    -  6 – Очень важна
    -  7 – Высшая значимость (не более двух)
  - Introduction includes a list of all values for pre- ознакомление.
  - Questions presented one by one with inline keyboard buttons.
  - Progress tracking (Value X of 57).
- **Priority:** High
- **Acceptance Criteria:** All 57 values rated with valid responses.

#### FR-002.3: Positive and Negative Affect Schedule (PANAS) Implementation
- **Description:** Implement the Positive and Negative Affect Schedule (PANAS) test.
- **Details:**
  - Present 20 adjectives (feelings/emotions) in Russian.
  - User rates to what extent they felt that way during the past few weeks.
  - 5-point response scale:
    - 1 – Почти или совсем нет
    - 2 – Немного
    - 3 – Умеренно
    - 4 – Значительно
    - 5 – Очень сильно
  - Questions presented one by one with inline keyboard buttons.
  - Progress tracking (Adjective X of 20).
- **Priority:** High
- **Acceptance Criteria:** All 20 adjectives rated with valid responses.

#### FR-002.4: Self-Efficacy Test Implementation
- **Description:** Implement the Self-Efficacy Test (General Self-Efficacy Scale by J. Maddux, M. Scheer).
- **Details:**
  - Present 23 statements in Russian.
  - User rates how much each statement describes them in ordinary life.
  - Response scale from -5 to +5 (excluding 0):
    - -5 – Совсем не про меня
    - ... (intermediate values)
    - +5 – Полностью про меня
  - Questions presented one by one with inline keyboard buttons (likely 2 rows of 5 buttons).
  - Progress tracking (Statement X of 23).
- **Priority:** High
- **Acceptance Criteria:** All 23 statements rated with valid responses.

#### FR-002.5: PID-5-BF+M Test Implementation
- **Description:** Implement the Modified Personality Inventory, PID-5-BF+M.
- **Details:**
  - Present 36 questions in Russian.
  - 4-point response scale:
    - 1 – Совершенно неверно или часто неверно
    - 2 – Иногда или в некоторой степени неверно
    - 3 – Иногда или в некоторой степени верно
    - 4 – Совершенно верно или часто верно
  - Questions presented one by one with inline keyboard buttons.
  - Progress tracking (Question X of 36).
- **Priority:** High
- **Acceptance Criteria:** All 36 questions completed with valid responses.

#### FR-002.6: Test Selection Flow
- **Description:** Allow users to select which test to take if multiple tests are available and not yet completed.
- **Details:**
  - If a user starts the testing process (e.g., via /test or initial menu) and has multiple uncompleted tests, present a menu of available tests.
  - If only one test is available and uncompleted, start it automatically.
  - Completed tests should not appear in the selection menu.
- **Priority:** High
- **Acceptance Criteria:** User can correctly select an available test, or the only available test starts automatically. Completed tests are not offered.

#### FR-003: Score Calculation Engine
- **Description:** Calculate scores for all implemented tests according to their respective methodologies.
- **Details:**
  - **HEXACO:** Apply reverse scoring, calculate facet scores, 6 main factor scores, and Altruism score.
  - **SDS:** Calculate scores for Self-Contact, Choiceful Action, and the overall Self-Determination Index.
  - **SVS:** Calculate scores for 10 basic human values and higher-order value dimensions.
  - **PANAS:** Calculate scores for Positive Affect (PA) and Negative Affect (NA).
  - **Self-Efficacy:** Apply reverse scoring for designated items, calculate General Self-Efficacy (GSE) and Social Self-Efficacy (SSE).
  - **PID-5-BF+M:** Placeholder scoring (e.g., sum of scores) until specific rules are provided.
  - All calculations must be accurate per the original test methodologies.
- **Priority:** Critical
- **Acceptance Criteria:** Scores for all tests calculated accurately.

#### FR-004: Results Storage
- **Description:** Store test results in a structured format for future use.
- **Details:**
  - Save to local SQLite database.
  - Include timestamp, user_id, session_id, and test_type.
  - Store raw user responses as a JSON string in the `responses` column.
  - Store calculated scores (specific scales and overall scores for each test) as a JSON string in the `scores_json` column.
  - Data persistence for later retrieval.
- **Priority:** High
- **Acceptance Criteria:** All test results for all test types saved successfully with the proper structure.

#### FR-005: Results Display
- **Description:** Present test results to the user in a readable format for each completed test.
- **Details:**
  - For each test, display relevant calculated scores and scales.
  - Include brief, user-friendly interpretations or summaries for each test's results.
  - Option to review previous results (currently shows a summary of completed tests, detailed view per test TBD).
- **Priority:** High
- **Acceptance Criteria:** User receives clear, understandable results for each test they complete.

### Medium Priority

#### FR-006: Test Session Management
- **Description:** Handle test interruptions and resumptions.
- **Details:**
  - Save progress automatically after each question.
  - Session information (current test, current question, collected responses for current test) stored per user.
  - Allow users to continue an uncompleted test (currently implicitly handled by starting the test flow which resumes if a test is active).
  - Session timeout for inactivity is not explicitly implemented, but user state is maintained.
- **Priority:** Medium
- **Acceptance Criteria:** Users can effectively continue an interrupted test.

#### FR-007: Data Export
- **Description:** Ability to export aggregated results
- **Details:**
  - Export functionality for administrators
  - Anonymized data export option
  - CSV/JSON format support
- **Priority:** Medium
- **Acceptance Criteria:** Data can be exported in usable format

### Low Priority

#### FR-008: User Profile Management
- **Description:** Allow users to view their test history
- **Details:**
  - List of completed tests with dates
  - Comparison of results over time
  - Profile editing capabilities
- **Priority:** Low
- **Acceptance Criteria:** Users can access their historical data

## Non-Functional Requirements

### Performance
- **NFR-001:** Bot must respond to user interactions within 2 seconds
- **NFR-002:** Support concurrent users (up to 50 simultaneous test sessions)
- **NFR-003:** Database operations must complete within 1 second
- **NFR-004:** Test completion time should be 15-20 minutes average

### Security
- **NFR-005:** User data must be stored securely in local database
- **NFR-006:** No sensitive personal information beyond name and test results
- **NFR-007:** Bot token must be stored securely (environment variables)
- **NFR-008:** Data access limited to authorized personnel only

### Usability
- **NFR-009:** Interface must be intuitive for non-technical users
- **NFR-010:** All messages in Russian language
- **NFR-011:** Clear navigation with inline buttons
- **NFR-012:** Error messages must be user-friendly and actionable
- **NFR-013:** Test questions displayed clearly with adequate spacing

### Scalability
- **NFR-014:** Architecture must support easy addition of new psychological tests. (Demonstrated by adding multiple new tests: SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M)
- **NFR-015:** Database schema must accommodate future feature extensions. (Revised to support multiple test types and flexible score storage via JSON.)
- **NFR-016:** Code must be modular for easy maintenance. (Ongoing effort, structure with separate data/scoring/handlers per test helps.)

### Reliability
- **NFR-017:** Bot must have 99% uptime during business hours
- **NFR-018:** Automatic recovery from connection failures
- **NFR-019:** Data backup mechanisms for test results
- **NFR-020:** Graceful error handling for all user interactions

### Compatibility
- **NFR-021:** Support all Telegram client platforms (mobile, desktop, web)
- **NFR-022:** Compatible with Python 3.7+ (Current: Python 3.11 or as per user environment)
- **NFR-023:** Local deployment on Windows environment (Confirmed as primary deployment environment)

## Technical Constraints and Assumptions

### Constraints
- **TC-001:** Must be deployed locally (no cloud services) (Maintained)
- **TC-002:** Single developer implementation (Maintained)
- **TC-003:** Budget constraint: free tools and libraries only (Maintained)
- **TC-004:** No external API dependencies except Telegram Bot API (Maintained)
- **TC-005:** Use pyTelegramBotAPI library (Maintained)

### Assumptions
- **AS-001:** Users have basic Telegram knowledge (Maintained)
- **AS-002:** Internal network has reliable internet for Telegram API (Maintained)
- **AS-003:** Questions for all tests are based on recognized psychological methodologies. (Maintained)
- **AS-004:** Users will complete each test in a single logical session (preferred, though progress is saved). (Maintained)
- **AS-005:** Company employees are primary target audience (Maintained)

## Data Requirements

### User Data Model (DB: `users` table)
```json
{
  "user_id": "integer (Telegram ID, PRIMARY KEY)",
  "username": "string (Telegram username, nullable)",
  "first_name": "string",
  "last_name": "string", 
  "gender": "string (male/female)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### User Session Data (In-memory: `SessionManager` - `UserSession` class)
```json
{
  "session_id": "string (UUID, matches session_id in DB test_sessions for linking if needed)",
  "user_id": "integer",
  "state": "string (e.g., 'registration_gender', 'registration_first_name', 'testing', 'menu')",
  "registration_data": {
    "first_name": "string (temporary)",
    "last_name": "string (temporary)",
    "gender": "string (temporary)"
  },
  "current_test_type": "string (e.g., 'hexaco', 'sds', 'panas', nullable)",
  "current_question": "integer (1-based index for the current_test_type, nullable)",
  "responses": {
    "hexaco": { "question_num": "answer_value", ... },
    "sds": { "question_num": "answer_value", ... },
    // ... other tests
  },
  "test_completed": {
    "hexaco": "boolean",
    "sds": "boolean",
    // ... other tests
  },
  "last_interaction_time": "datetime"
}
```

### Test Session Data Model (DB: `test_sessions` table - primarily for historical/audit if needed, main session logic is in-memory)
```json
{
  "session_id": "string (UUID, PRIMARY KEY)",
  "user_id": "integer (FOREIGN KEY to users)",
  "status": "string (active, completed, abandoned) - reflects overall user engagement, not specific test.",
  "current_question": "integer (Can be deprecated or re-purposed as this is now in UserSession per test)",
  "started_at": "timestamp",
  "completed_at": "timestamp (nullable)"
}
```

### Results Data Model (DB: `results` table)
```json
{
  "result_id": "integer (PRIMARY KEY AUTOINCREMENT)",
  "session_id": "string (FOREIGN KEY to test_sessions)",
  "user_id": "integer (FOREIGN KEY to users)",
  "test_type": "string (e.g., 'hexaco', 'sds', 'panas', 'pid5bfm', CHECK constraint includes all active tests)",
  "honesty_humility": "REAL (nullable, specific to HEXACO)",
  "emotionality": "REAL (nullable, specific to HEXACO)",
  "extraversion": "REAL (nullable, specific to HEXACO)",
  "agreeableness": "REAL (nullable, specific to HEXACO)",
  "conscientiousness": "REAL (nullable, specific to HEXACO)",
  "openness": "REAL (nullable, specific to HEXACO)",
  "altruism": "REAL (nullable, specific to HEXACO)",
  "self_contact": "REAL (nullable, specific to SDS)",
  "choiceful_action": "REAL (nullable, specific to SDS)",
  "sds_index": "REAL (nullable, specific to SDS)",
  "scores_json": "TEXT (JSON string containing all calculated scores for the specific test_type, e.g., URICA stages, Dweck scales, PANAS PA/NA)",
  "responses": "TEXT (JSON string of user's raw answers for the specific test_type)",
  "created_at": "timestamp"
}
```

## Integration Requirements

### Telegram Bot API Integration
- **IR-001:** Full integration with Telegram Bot API
- **IR-002:** Support for inline keyboards and callback queries
- **IR-003:** Message editing capabilities for progress updates
- **IR-004:** Error handling for API rate limits

### Database Integration
- **IR-005:** SQLite database for local data storage
- **IR-006:** Database schema migration support
- **IR-007:** Data integrity constraints
- **IR-008:** Backup and restore capabilities

## Acceptance Criteria

### System Level Acceptance Criteria
- [ ] Bot responds correctly to /start command
- [ ] Complete user registration flow works
- [ ] All HEXACO questions presented correctly
- [ ] All SDS questions presented correctly
- [ ] All SVS questions presented correctly
- [ ] All PANAS questions presented correctly
- [ ] All Self-Efficacy questions presented correctly
- [ ] All PID-5-BF+M questions presented correctly
- [ ] Score calculation matches methodologies for all tests
- [ ] Results stored in specified format for all tests
- [ ] User can complete full tests without errors
- [ ] Completed tests are correctly marked and not offered again
- [ ] Test selection menu works as expected
- [ ] Bot handles multiple concurrent users
- [ ] All error scenarios handled gracefully

### User Experience Acceptance Criteria
- [ ] Test completion time under 25 minutes
- [ ] Clear instructions provided at each step
- [ ] Progress indicator works correctly
- [ ] Results are understandable and actionable
- [ ] Bot responds promptly to all interactions

### Technical Acceptance Criteria
- [ ] Code follows Python best practices
- [ ] Database operations are optimized
- [ ] All dependencies properly managed
- [ ] Local deployment works correctly
- [ ] Comprehensive error logging implemented

## Requirements Approval

- [x] Stakeholder Review - Approved (December 26, 2024)
- [x] Technical Review - Approved (December 26, 2024)  
- [x] Final Approval - Approved (December 26, 2024)

## Change Log
| Date | Change | Approved By | Impact |
|------|--------|-------------|--------|
| 2024-12-26 | Initial specification | - | Baseline |

---
*Last Updated: December 26, 2024 by Claude AI Assistant* 