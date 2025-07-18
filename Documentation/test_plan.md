# Test Plan

## Testing Overview
**Document Version:** 1.1  
**Last Updated:** May 31, 2024  
**Testing Strategy:** Multi-level testing with emphasis on scoring accuracy for all tests, user experience, and robust multi-test session management.

## Testing Scope

### In Scope
- **Scoring Algorithms:** Complete validation of all questions and scoring rules for HEXACO, SDS, SVS, PANAS, Self-Efficacy, and PID-5-BF+M tests.
- **Bot Handler Functions (`QuestionHandler`):** All Telegram message and callback handlers, including registration, test selection, question presentation, and answer processing.
- **Database Operations (`DatabaseManager`):** CRUD operations for users and results, multi-test data persistence (test_type, scores_json, responses), data integrity.
- **User Registration Flow:** Gender selection, name validation, user record creation.
- **Test Selection Flow:** Correct display of available (uncompleted) tests, handling of single vs. multiple available tests.
- **Test Session Management (`SessionManager`, `UserSession`):** Progress tracking within each test, state management for multiple concurrent tests and users, correct storage of responses per test type, handling of completed tests.
- **Results Generation:** Score calculation for all tests, JSON format validation for `scores_json` and `responses`, display formatting for all tests.
- **Error Handling:** All exception scenarios, user-friendly error messages, graceful degradation.
- **Performance Testing (Basic):** Concurrent user interaction, memory usage, response times.
- **Security Testing (Basic):** Token handling, basic input validation.

### Out of Scope
- **Telegram API Testing:** Third-party service (assumed working)
- **Python Standard Library:** Built-in modules (sqlite3, json, etc.)
- **Load Testing Beyond 50 Users:** Project scope limitation
- **Cross-platform Testing:** Windows-only deployment
- **Internationalization:** Russian language only

## Testing Levels

### Unit Testing
**Target Coverage:** 95%+ for scoring algorithms, 85%+ overall  
**Framework:** pytest with coverage reporting  
**Responsibility:** Development Team  

#### Test Categories
- [x] **Component Functionality Testing**
  - Individual function behavior validation
  - Input/output verification
  - Edge case handling
  - Parameter validation

- [x] **HEXACO Scoring Engine Testing**
  - Question-to-facet mapping accuracy
  - Reverse scoring implementation
  - Facet score calculations (24 facets)
  - Factor score calculations (6 factors + Altruism)
  - Score range validation (1.0-5.0)

- [x] **Database Operations Testing**
  - User CRUD operations
  - Session management functions
  - Result storage and retrieval
  - Data integrity validation
  - Concurrent access handling

- [x] **Session Management Testing**
  - Session creation and cleanup
  - Progress tracking accuracy
  - Timeout handling (24 hours)
  - Resume functionality

### Integration Testing
**Approach:** Bottom-up integration testing  
**Environment:** Local development environment with test database  

#### Test Categories
- [x] **Bot Handler Integration**
  - Message routing between handlers
  - State management across interactions
  - Callback query processing
  - Error propagation and handling

- [x] **Database Integration**
  - Database schema validation
  - Transaction management
  - Connection pooling behavior
  - Backup and restore operations

- [x] **Scoring System Integration**
  - End-to-end score calculation
  - Data flow from answers to results
  - JSON format compliance
  - Result persistence validation

- [x] **Session Flow Integration**
  - Complete user journey testing
  - Registration → Test → Results flow
  - Session state consistency
  - Progress preservation

### System Testing
**Environment:** Production-like local environment  
**Data:** Anonymized test data with known expected results  

#### Test Categories
- [x] **End-to-End User Scenarios**
  - Complete test completion for each available test (HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M).
  - Scenario: User completes one test, then selects and completes another.
  - Scenario: User has some tests completed, some not; selection menu shows only uncompleted.
  - Session interruption and resume (implicit through current state saving).
  - Multiple users interacting with different tests concurrently (conceptual validation).

- [x] **Performance Testing**
  - Response time validation (<2 seconds)
  - Concurrent user support (up to 50)
  - Memory usage monitoring
  - Database performance under load

- [x] **Security Testing**
  - Input validation and sanitization
  - SQL injection prevention
  - Bot token security verification
  - Data access control testing

- [x] **Reliability Testing**
  - Extended operation testing (24+ hours)
  - Error recovery mechanisms
  - Data consistency validation
  - Graceful degradation testing

### User Acceptance Testing (UAT)
**Environment:** Production environment  
**Participants:** Internal company employees (target users)  
**Duration:** 1 week testing period  

#### Test Scenarios
- [x] **Usability Testing**
  - Russian language interface clarity
  - Navigation intuitiveness
  - Progress indicator effectiveness
  - Error message comprehensibility

- [x] **Business Scenario Testing**
  - Complete assessment workflow for each of the implemented psychological tests.
  - Results interpretation accuracy and clarity for each test.
  - Time-to-completion measurement for each test.
  - User satisfaction feedback regarding the multi-test experience.

- [x] **Accessibility Testing**
  - Various Telegram client compatibility
  - Different screen sizes and devices
  - Network condition tolerance
  - User error recovery

## Test Data Strategy

### Test Questions & Answer Options
- For each test (HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M), a complete set of questions and their specific answer options are defined in their respective `src/data/<test_name>_questions.py` files.
- This data is used directly by the `QuestionHandler` to present questions to the user.

```python
# Conceptual Example: src/data/sds_questions.py
# SDS_QUESTIONS = [
#     {"id": 1, "text_a": "Statement A1", "text_b": "Statement B1"}, ...
# ]
# SDS_ANSWER_OPTIONS = [
#     {"text": "Верно только А", "value": 1}, ...
# ]
```

### Known Score Calculations (for each test)
- For each implemented test, a set of sample user responses and the corresponding expected calculated scores (subscales, overall scores, interpretations where applicable) should be prepared.
- This is crucial for validating the correctness of each Scorer module in `src/scoring/`.

```python
# Conceptual Example: Test case for a hypothetical "SDSScorer"
# SDS_TEST_CASES = [
#     {
#         "responses": {1: 1, 2: 5, 3: 2, ..., 10: 4}, // User answers for SDS questions
#         "expected_scores": {
#             "self_contact": 15,
#             "choiceful_action": 20,
#             "sds_index": 35,
#             "interpretation": "Some interpretation text..."
#         }
#     }
# ]
```

### User Test Data
```python
# Anonymous user data for testing
TEST_USERS = [
    {
        "user_id": 123456,
        "username": "test_user_1",
        "first_name": "Тест",
        "last_name": "Пользователь",
        "gender": "Male"
    }
]
```

### Critical Test Cases

#### TC001: Complete Test Flow for Each Implemented Test
**Objective:** Verify end-to-end user journey for each available psychological test.
**Applies to:** HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M.
**Pre-conditions:** Bot running, database initialized, user registered.
**Steps (generic for each test `T`):
1. User is presented with the test selection menu (if multiple tests are available and uncompleted for the user).
2. User selects test `T`.
3. Bot displays the introductory message for test `T`.
4. User clicks the "Start Test `T`" button.
5. Bot presents questions for test `T` one by one, with correct answer options.
6. User answers all questions for test `T`.
7. Upon completion, bot calculates scores for test `T` using the respective Scorer.
8. Bot displays the formatted results and interpretation for test `T`.
9. Bot saves the raw responses and calculated scores for test `T` to the `results` table in the database (with correct `user_id` and `test_type`).
10. Bot marks test `T` as completed in the user's session.
**Expected Results:** 
- Test `T` is correctly initiated.
- All questions for test `T` are presented correctly with appropriate answer formats.
- Scores for test `T` are calculated accurately according to its methodology.
- Results for test `T` are displayed clearly to the user.
- Results for test `T` are correctly stored in the database.
- Test `T` is marked as completed and, if no other tests are pending, user is informed, or if others are pending, the selection menu (excluding `T`) is shown or the next test starts (if only one was left).

#### TC002: Scoring Accuracy for Each Implemented Test
**Objective:** Validate the correctness of each test's scoring algorithm.
**Applies to:** HEXACOScorer, SDSScorer, SVSScorer, UricaScorer, DweckScorer, PanasScorer, SelfEfficacyScorer.
**Pre-conditions:** Known set of answers for each test with pre-calculated expected scores.
**Steps (for each Scorer `S` and its corresponding test data):
1. Provide the Scorer `S` with the predefined set of answers.
2. Trigger the `calculate_scores` method of Scorer `S`.
3. Compare the returned scores (all subscales, main scores, indices) with the pre-calculated expected scores.
**Expected Results:** 
- All calculated scores by Scorer `S` must exactly match the expected scores for its test.
- For tests with reverse-scored items or special conditions (e.g., Dweck Q4), these must be handled correctly.

#### TC003: Test Selection Logic and Completed Test Handling
**Objective:** Verify that the test selection menu behaves correctly based on the user's completed tests.
**Pre-conditions:** Bot running, user registered. Database may contain some completed test results for the user.
**Steps:**
1. User initiates a test session (e.g., via `/test` or `/start` if already registered).
2. Bot checks `UserSession.test_completed` and/or queries the `results` table for the user.
3. **Scenario A (No tests completed):** Bot displays a menu with all available tests.
4. **Scenario B (Some tests completed, some not):** Bot displays a menu listing only the uncompleted tests.
5. **Scenario C (All tests completed):** Bot displays a message indicating all tests are done, or offers to review results (if implemented).
6. User selects an available test from the menu (if applicable).
7. The selected test starts correctly.
**Expected Results:**
- In Scenario A, all tests are listed as available.
- In Scenario B, only uncompleted tests are listed and selectable.
- In Scenario C, no tests are offered for taking; an appropriate message is shown.
- Attempting to start an already completed test (if somehow possible through a stale callback, etc.) should be gracefully handled (e.g., message indicating it's done).

#### TC004: Data Persistence and Integrity for All Tests
**Objective:** Verify that raw responses and calculated scores for all test types are correctly saved to and retrieved from the database.
**Applies to:** All test types.
**Pre-conditions:** User completes a test.
**Steps:**
1. User completes a test (e.g., PANAS).
2. Bot saves results to the `results` table.
3. Manually inspect the `results` table (or use a DB query tool) for the corresponding record.
4. Verify:
    - `user_id` is correct.
    - `test_type` is correct (e.g., 'panas').
    - `responses` column contains the correct JSON string of the user's raw answers.
    - `scores_json` column contains the correct JSON string of all calculated scores for that test (e.g., PA and NA scores for PANAS).
5. (If applicable) Trigger any bot function that might retrieve/display past results and verify consistency.
**Expected Results:**
- All data fields for the completed test are accurately stored in the `results` table.
- JSON structures in `responses` and `scores_json` are valid and contain the correct data.
- Data can be retrieved consistently if needed.

## Test Environment Setup

### Development Environment
```bash
# Test environment setup
python -m venv test_env
test_env\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio
```

### Test Database Configuration
```python
# Separate test database
TEST_DATABASE_PATH = "./data/test_hexaco_bot.db"
# Auto-cleanup after tests
```

### Mock Services
```python
# Mock Telegram API for testing
class MockTelegramAPI:
    def send_message(self, chat_id, text):
        return {"message_id": 123, "status": "sent"}
    
    def answer_callback_query(self, callback_query_id):
        return {"status": "answered"}
```

## Test Cases Documentation

### Critical Test Cases

#### TC001: Complete Test Flow for Each Implemented Test
**Objective:** Verify end-to-end user journey for each available psychological test.
**Applies to:** HEXACO, SDS, SVS, PANAS, Self-Efficacy, PID-5-BF+M.
**Pre-conditions:** Bot running, database initialized, user registered.
**Steps (generic for each test `T`):
1. User is presented with the test selection menu (if multiple tests are available and uncompleted for the user).
2. User selects test `T`.
3. Bot displays the introductory message for test `T`.
4. User clicks the "Start Test `T`" button.
5. Bot presents questions for test `T` one by one, with correct answer options.
6. User answers all questions for test `T`.
7. Upon completion, bot calculates scores for test `T` using the respective Scorer.
8. Bot displays the formatted results and interpretation for test `T`.
9. Bot saves the raw responses and calculated scores for test `T` to the `results` table in the database (with correct `user_id` and `test_type`).
10. Bot marks test `T` as completed in the user's session.
**Expected Results:** 
- Test `T` is correctly initiated.
- All questions for test `T` are presented correctly with appropriate answer formats.
- Scores for test `T` are calculated accurately according to its methodology.
- Results for test `T` are displayed clearly to the user.
- Results for test `T` are correctly stored in the database.
- Test `T` is marked as completed and, if no other tests are pending, user is informed, or if others are pending, the selection menu (excluding `T`) is shown or the next test starts (if only one was left).

#### TC002: Scoring Accuracy for Each Implemented Test
**Objective:** Validate the correctness of each test's scoring algorithm.
**Applies to:** HEXACOScorer, SDSScorer, SVSScorer, PanasScorer, SelfEfficacyScorer, PID5BFMScorer.
**Pre-conditions:** Known set of answers for each test with pre-calculated expected scores.
**Steps (for each Scorer `S` and its corresponding test data):
1. Provide the Scorer `S` with the predefined set of answers.
2. Trigger the `calculate_scores` method of Scorer `S`.
3. Compare the returned scores (all subscales, main scores, indices) with the pre-calculated expected scores.
**Expected Results:** 
- All calculated scores by Scorer `S` must exactly match the expected scores for its test.
- For tests with reverse-scored items, these must be handled correctly.

#### TC003: Test Selection Logic and Completed Test Handling
**Objective:** Verify that the test selection menu behaves correctly based on the user's completed tests.
**Pre-conditions:** Bot running, user registered. Database may contain some completed test results for the user.
**Steps:**
1. User initiates a test session (e.g., via `/test` or `/start` if already registered).
2. Bot checks `UserSession.test_completed` and/or queries the `results` table for the user.
3. **Scenario A (No tests completed):** Bot displays a menu with all available tests.
4. **Scenario B (Some tests completed, some not):** Bot displays a menu listing only the uncompleted tests.
5. **Scenario C (All tests completed):** Bot displays a message indicating all tests are done, or offers to review results (if implemented).
6. User selects an available test from the menu (if applicable).
7. The selected test starts correctly.
**Expected Results:**
- In Scenario A, all tests are listed as available.
- In Scenario B, only uncompleted tests are listed and selectable.
- In Scenario C, no tests are offered for taking; an appropriate message is shown.
- Attempting to start an already completed test (if somehow possible through a stale callback, etc.) should be gracefully handled (e.g., message indicating it's done).

#### TC004: Data Persistence and Integrity for All Tests
**Objective:** Verify that raw responses and calculated scores for all test types are correctly saved to and retrieved from the database.
**Applies to:** All test types.
**Pre-conditions:** User completes a test.
**Steps:**
1. User completes a test (e.g., PANAS).
2. Bot saves results to the `results` table.
3. Manually inspect the `results` table (or use a DB query tool) for the corresponding record.
4. Verify:
    - `user_id` is correct.
    - `test_type` is correct (e.g., 'panas').
    - `responses` column contains the correct JSON string of the user's raw answers.
    - `scores_json` column contains the correct JSON string of all calculated scores for that test (e.g., PA and NA scores for PANAS).
5. (If applicable) Trigger any bot function that might retrieve/display past results and verify consistency.
**Expected Results:**
- All data fields for the completed test are accurately stored in the `results` table.
- JSON structures in `responses` and `scores_json` are valid and contain the correct data.
- Data can be retrieved consistently if needed.

## Test Automation Strategy

### Automated Test Categories
- **Unit Tests:** 100% automated with pytest
- **Integration Tests:** 90% automated
- **Performance Tests:** 80% automated with custom scripts
- **Security Tests:** 70% automated with vulnerability scanners

### Test Execution Schedule
- **Pre-commit:** Unit tests (fast subset)
- **Daily:** Full unit + integration test suite
- **Weekly:** Complete test suite including performance
- **Pre-deployment:** Full acceptance testing

### Continuous Integration
```yaml
# GitHub Actions or similar
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=src tests/
```

## Test Quality Metrics

### Coverage Targets
- **Scoring Algorithm:** 100% line coverage
- **Database Operations:** 95% line coverage
- **Bot Handlers:** 90% line coverage
- **Overall Project:** 85% line coverage

### Quality Gates
- **Zero Critical Bugs:** No P0/P1 issues in production
- **Performance:** All responses <2 seconds
- **Reliability:** 99% uptime during testing
- **Accuracy:** 100% scoring algorithm correctness

### Test Reporting
```python
# Coverage reporting
pytest --cov=src --cov-report=html --cov-report=term
```

## Test Tools and Frameworks

### Testing Frameworks
- **pytest:** Primary testing framework
- **pytest-cov:** Coverage reporting
- **pytest-asyncio:** Async testing support
- **unittest.mock:** Mocking Telegram API

### Performance Tools
- **memory_profiler:** Memory usage tracking
- **time:** Response time measurement
- **sqlite3 EXPLAIN:** Database query optimization

### Security Tools
- **bandit:** Security vulnerability scanning
- **safety:** Dependency vulnerability checking

## Test Data Management

### Test Data Sources
- **Official HEXACO-PI-R:** Validated question set
- **Research Papers:** Expected scoring examples
- **Anonymous Users:** Real-world usage patterns

### Data Privacy
- **No Personal Data:** Test with fictional users
- **Anonymization:** Remove all identifying information
- **Secure Storage:** Test data encrypted and access-controlled

## Defect Management

### Bug Classification
- **P0 Critical:** Bot completely non-functional
- **P1 High:** Core functionality broken
- **P2 Medium:** Feature degradation
- **P3 Low:** Minor UI/UX issues

### Bug Lifecycle
1. **Discovery:** Test execution or user report
2. **Triage:** Severity and priority assignment
3. **Assignment:** Developer allocation
4. **Resolution:** Fix implementation
5. **Verification:** Test case validation
6. **Closure:** Stakeholder approval

## Test Schedule

### Phase 7 Testing Timeline
- **Week 1:** Unit testing implementation
- **Week 2:** Integration testing
- **Week 3:** System and performance testing
- **Week 4:** User acceptance testing
- **Ongoing:** Regression testing

### Test Milestones
- [ ] Unit test suite complete (95% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Security tests cleared
- [ ] UAT approval received

## Success Criteria

### Testing Success Metrics
- [ ] All critical test cases pass
- [ ] Coverage targets achieved
- [ ] Performance requirements met
- [ ] Zero security vulnerabilities
- [ ] User acceptance criteria satisfied

### Quality Assurance Sign-off
- [ ] Technical testing complete
- [ ] Performance validation complete
- [ ] Security assessment complete
- [ ] User acceptance testing complete
- [ ] Documentation review complete

---
*Test Plan created: December 26, 2024*  
*Testing Strategy: Multi-level comprehensive validation*  
*Status: Ready for implementation* 