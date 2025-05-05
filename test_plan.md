# Test Plan for Master of Jokes (MoJ2)

## Overview
This document outlines the testing strategy for the "Master of Jokes" web application, which includes user authentication, joke management (posting, viewing, rating), and database interactions.

## Test Objectives
- Verify that all user-facing features work as intended.
- Ensure data integrity in the database.
- Confirm correct access control and permissions.
- Validate edge cases and error handling.

## Scope
- Authentication: Register, Login, Logout
- Jokes: Leave (Post), View, Take, Edit, Delete
- Rating system
- Permissions & access control
- Moderator features

## Test Types
- Unit Tests (Flask routes, form validation, DB operations)
- Integration Tests (flows involving multiple components)
- Functional Tests (user-facing functionality)

## Tools
- [pytest](https://docs.pytest.org/)
- Flask’s built-in test client

## Structure
Test files are organized in `tests/`:
- `test_auth.py`
- `test_jokes.py`
- `test_permissions.py`
- `test_moderator.py`

## Database
A temporary in-memory SQLite DB will be used during testing.

---

## Test Cases

### `test_auth.py`

| Test ID      | Description                        | Expected Result                      |
|--------------|------------------------------------|--------------------------------------|
| AUTH-001     | Register with valid data           | Redirect to login page               |
| AUTH-002     | Login with valid credentials       | Redirect to homepage                 |
| AUTH-003     | Logout from session                | Redirect to login page               |
| AUTH-004     | Manual database insert and fetch   | User is retrieved with correct info  |

---

### `test_jokes.py`

#### `/leave` - Joke Submission Page

| Test ID  | Description                             | Expected Result                                |
|----------|-----------------------------------------|------------------------------------------------|
| JOKE-001 | Post joke with valid title/body         | Joke is successfully added                     |
| JOKE-002 | Post joke without a title               | Error: "Title is required."                    |
| JOKE-003 | Post joke with too long a title         | Error: "Title must be no more than 10 words."  |
| JOKE-004 | Post duplicate title                    | Error: "You already used this title"           |


#### `/take` - Joke Exchange Page

| Test ID  | Description                                     | Expected Result                              |
|----------|-------------------------------------------------|----------------------------------------------|
| JOKE-005 | Successfully take a joke after leaving one      | Success message shown                         |
| JOKE-006 | Attempt to take the same joke twice             | Error: "You have already taken this joke!"    |
| JOKE-007 | Try taking a joke without first leaving one     | Error: "You need to leave a joke first!"      |


#### `/my`, `/view/<id>` - User Jokes & Viewing

| Test ID  | Description                                 | Expected Result                             |
|----------|---------------------------------------------|---------------------------------------------|
| JOKE-008 | View personal jokes after leaving one       | Joke appears in personal list               |
| JOKE-009 | View personal jokes without any jokes       | Message: "No jokes found"                   |
| JOKE-010 | View joke with insufficient joke balance     | Error: "Not enough joke balance..."         |


#### `/rate`, `/update`, `/delete` - Joke Interaction

| Test ID  | Description                                 | Expected Result                                         |
|----------|---------------------------------------------|---------------------------------------------------------|
| JOKE-011 | Submit a new rating for a joke              | Success message: "Your rating has been submitted!"      |
| JOKE-012 | Update a previously submitted rating        | Success message: "Your rating has been updated!"        |
| JOKE-013 | Delete own joke                             | Success message: "Joke deleted."                        |
| JOKE-014 | Update joke body                            | Success message: "Joke updated successfully!"           |

---

### `test_permissions.py`

| Test ID      | Description                                      | Expected Result            |
|--------------|--------------------------------------------------|----------------------------|
| PERM-001     | Redirect when accessing joke page unauthenticated| Page redirects to login    |
| PERM-002     | Prevent posting joke without login               | Page redirects to login    |

---

### `test_moderator.py`

| Test ID      | Description                                       | Expected Result                           |
|--------------|---------------------------------------------------|-------------------------------------------|
| MOD-001      | Access moderator dashboard                        | "Welcome, Moderator!" is visible          |
| MOD-002      | View user list in moderator panel                 | Moderator nickname is visible             |
| MOD-003      | Promote a regular user to moderator               | Message: "User promoted to moderator"     |
| MOD-004      | Demote a moderator to regular user                | Message: "Moderator demoted to user"      |
| MOD-005      | Non-moderator tries accessing dashboard           | Message: "Unauthorized access"            |
| MOD-006      | Prevent demotion of last moderator                | Message: "Cannot remove the last moderator" |
| MOD-007      | Moderator updates user’s joke balance             | Balance is updated and success message shown |

---

## Notes
- The `client` fixture creates a fresh in-memory DB for each test run to isolate test state.
- Moderator-related tests simulate role change by directly modifying the DB.
- Joke interaction features rely on login state and role-based access.


##  Running the Tests

Activate your virtual env (Optional)
```bash
source venv/bin/activate
```
Run all tests
```bash
pytest
```
Run only the joke tests
```bash
pytest tests/test_jokes.py
```
Show verbose output for better test tracking
```bash
pytest -v
```
Run a specific test by test_name
```bash
pytest tests/test_moderator.py::test_moderator_update_balance 
```
