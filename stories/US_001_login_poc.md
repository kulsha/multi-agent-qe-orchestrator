# US_001_POC — Login & Authentication (POC)

## Metadata
- **Story ID:** US_001_poc
- **Feature:** Login & Authentication
- **Application:** OrangeHRM
- **Module:** Auth
- **Priority:** High
- **Created By:** QA Lead
- **Target URL:** https://opensource-demo.orangehrmlive.com/web/index.php/auth/login

---

## Problem Statement

OrangeHRM requires a secure login mechanism so that only authorised users
can access the system. Users must be able to log in using a valid username
and password combination. The system must prevent unauthorised access by
rejecting invalid credentials and displaying appropriate error messages.
After a successful login the user must be redirected to the HR dashboard.
After a failed login the user must remain on the login page with a clear
error message. The login page must display all required UI elements on load.

---

## Acceptance Criteria

### AC_001 — Successful Login with Valid Credentials
**Given** the user is on the OrangeHRM login page
**When** the user enters a valid username (Admin) and valid password (admin123)
**Then** the user should be redirected to the HR Dashboard
**And** the dashboard URL should contain /dashboard
**And** the user's name should be visible in the top navigation bar

### AC_002 — Login Fails with Invalid Credentials
**Given** the user is on the OrangeHRM login page
**When** the user enters an invalid username or incorrect password
**Then** the login should fail
**And** an error message "Invalid credentials" should be displayed
**And** the user should remain on the login page

### AC_003 — Login Page UI Elements Are Present
**Given** the user navigates to the OrangeHRM login page
**When** the page loads completely
**Then** the following elements should be visible:
- Username input field
- Password input field
- Login button
- OrangeHRM logo

---

## Test Data

| Field    | Valid Value | Invalid Value | Edge Case           |
|----------|-------------|---------------|---------------------|
| Username | Admin       | invaliduser   | (empty), whitespace |
| Password | admin123    | wrongpassword | (empty), whitespace |

---

## Out of Scope
- Password reset flow
- Multi-factor authentication
- Session timeout behaviour
- SSO / LDAP login
- Empty field validation messages
- Password masking verification