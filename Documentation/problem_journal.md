# Problem Journal

## Problem Management Overview
**Document Version:** 1.1  
**Last Updated:** May 31, 2024  
**Total Problems Logged (Summarized):** 7  
**Open Problems:** 0  
**Resolved Problems:** 7  

## Problem Categories
- **Technical:** Code bugs, system failures, integration issues
- **Configuration:** Environment setup, dependency issues
- **Logic:** Errors in business logic or algorithms

## Problem Entries (Summarized Retrospectively)

### Problem #001 (Initial Bot Launch & Config Issues)
**Date Reported:** Approx. Dec 2024 - Jan 2025  
**Reporter:** User/System  
**Category:** Configuration, Technical  
**Severity:** High  
**Status:** Resolved  

**Problem Description:** Bot failed to launch due to `UnicodeDecodeError` when reading `.env` file and `ValueError: BOT_TOKEN environment variable is required` due to incorrect path handling for `.env`.  

**Location:** `config/settings.py`, `.env` file handling.  

**Solution Approach:** Changed `.env` file encoding to UTF-8. Explicitly constructed the `.env` path in `config/settings.py` using `Path(__file__).resolve().parent.parent / '.env'`.  

**Resolution Date:** Approx. Jan 2025  

---

### Problem #002 (HEXACO Button Removal Logic)
**Date Reported:** Approx. Feb 2025  
**Reporter:** User  
**Category:** Logic  
**Severity:** Medium  
**Status:** Resolved  

**Problem Description:** "Назад" (Back) and "Пропустить" (Skip) buttons were only removed for the first two questions of the HEXACO test, not for all 100.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (method `_show_question` for HEXACO).  

**Solution Approach:** Modified `_show_question` to consistently not add these buttons for any HEXACO question.  

**Resolution Date:** Approx. Feb 2025  

---

### Problem #003 (SessionManager `save_session` Attribute Error)
**Date Reported:** Approx. Feb-Mar 2025  
**Reporter:** System (Error Log)  
**Category:** Technical  
**Severity:** Medium  
**Status:** Resolved  

**Problem Description:** Bot raised `AttributeError: 'SessionManager' object has no attribute 'save_session'`. The actual method was `save_response`.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (method `_handle_answer_callback`).  

**Solution Approach:** Changed the call from `self.session_manager.save_session(...)` to `self.session_manager.save_response(...)` with correct parameters.  

**Resolution Date:** Approx. Mar 2025  

---

### Problem #004 (SVS Question Display Syntax Error)
**Date Reported:** Approx. April 2025  
**Reporter:** System (Error Log)  
**Category:** Technical  
**Severity:** Medium  
**Status:** Resolved  

**Problem Description:** `SyntaxError: unterminated f-string literal` occurred when trying to display SVS questions due to a formatting issue in an f-string.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (in `_show_question` related to SVS display logic).  

**Solution Approach:** Corrected the f-string formatting for SVS question text.  

**Resolution Date:** Approx. April 2025  

---

### Problem #005 (User ID Handling for Registered User Test Start)
**Date Reported:** Approx. April 2025  
**Reporter:** User  
**Category:** Logic, Technical  
**Severity:** Medium  
**Status:** Resolved  

**Problem Description:** Pressing "Пройти тест" after `/start` (for a registered user) failed to correctly identify the `user_id` for starting the test flow.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (callback `_handle_select_initial_test_callback`).  

**Solution Approach:** Refactored how `user_id` is obtained in `_handle_select_initial_test_callback` (using `call.from_user.id`) and introduced `_start_test_flow` method to centralize test initiation logic.  

**Resolution Date:** Approx. April 2025  

---

### Problem #006 (Self-Efficacy "Unknown Test Type" Error)
**Date Reported:** Approx. May 2025  
**Reporter:** User/System (Error Log)  
**Category:** Logic, Technical  
**Severity:** High  
**Status:** Resolved  

**Problem Description:** When selecting the Self-Efficacy test, an error "Attempted to initiate test flow with unknown test_type: self_efficacy" occurred. The callback data from the button was `start_self_efficacy_test` but `_initiate_test_flow` expected just `self_efficacy`.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (generation of callback data in `_start_test_flow` and handling in `_handle_start_test_callback` pattern matching).  

**Solution Approach:** Ensured callback data for starting tests is consistently the `test_type` itself (e.g., `self_efficacy`) and updated relevant handlers (e.g. `_handle_start_self_efficacy_test_callback` and its registration).  

**Resolution Date:** Approx. May 2025  

---

### Problem #007 (Completed Tests Not Disappearing / Incorrect DB Save)
**Date Reported:** Approx. May 2025  
**Reporter:** User  
**Category:** Logic, Technical, Database  
**Severity:** High  
**Status:** Resolved  

**Problem Description:** 
1. Completed tests were still being offered in the test selection menu.
2. Test results were potentially not being saved correctly or checked reliably, contributing to issue #1.  

**Location:** `hexaco_bot/src/handlers/question_handler.py` (`_start_test_flow`), `hexaco_bot/src/data/database.py` (`save_test_result`, `get_all_user_results`, `results` table schema).  

**Root Cause Analysis:** Issues included: incorrect key for `responses_json` (was `responses_json` instead of `responses` in `save_test_result` call), `CHECK` constraint in `results` table not including all test types, `get_all_user_results` not correctly filtering, and `UserSession.test_completed` state not being robustly synchronized/checked.  

**Solution Approach:** 
1. Corrected `UserSession.test_completed` update logic and its usage in `_start_test_flow`.
2. Updated `DatabaseManager`:
    - Ensured `CHECK` constraint for `test_type` in `results` table includes all current and future tests (e.g., 'hexaco', 'sds', 'svs', 'panas', 'self_efficacy').
    - Corrected parameter name in `save_test_result` from `responses_json` to `responses` when passing to `_execute_query`.
    - Ensured `get_all_user_results` correctly queries by `user_id` and retrieves necessary `test_type` data.
3. Ensured database is correctly identified and re-created after schema changes if necessary.  

**Resolution Date:** Approx. May 2025  

---

## Problem Summary Dashboard (Based on Summarized Log)

### Problems by Category
| Category      | Open | In Progress | Resolved | Total |
|---------------|------|-------------|----------|-------|
| Technical     | 0    | 0           | 5        | 5     |
| Configuration | 0    | 0           | 1        | 1     |
| Logic         | 0    | 0           | 4        | 4     |
| Database      | 0    | 0           | 1        | 1     |

*Note: Some problems had multiple categories.*

### Problems by Severity
| Severity | Open | In Progress | Resolved | Total |
|----------|------|-------------|----------|-------|
| Critical | 0    | 0           | 0        | 0     |
| High     | 0    | 0           | 4        | 4     |
| Medium   | 0    | 0           | 3        | 3     |
| Low      | 0    | 0           | 0        | 0     |

---
*Last Updated: May 31, 2024 by Claude AI Assistant* 