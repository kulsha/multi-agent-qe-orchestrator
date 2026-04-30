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
error message. The login page must display all required UI elements on load
and all interactive elements must function correctly.

---

## Acceptance Criteria

### AC_001 — Successful Login with Valid Credentials
**Given** the user is on the OrangeHRM login page
**When** the user enters a valid username (Admin) and valid password (admin123)
**Then** the user should be redirected to the HR Dashboard
**And** the dashboard URL should contain /dashboard
**And** the user's name should be visible in the top navigation bar
**And** when the user enters an invalid username or incorrect password
**Then** the login should fail and the user should remain on the login page

### AC_002 — Login Validation Behaviour
**Given** the user is on the OrangeHRM login page
**When** the user enters valid credentials (Admin / admin123)
**Then** the user should be successfully redirected to the dashboard
**And** when the user enters an invalid username (invaliduser) with any password
**Then** an error message "Invalid credentials" should be displayed
**And** when the user enters a valid username with an incorrect password (wrongpassword)
**Then** an error message "Invalid credentials" should be displayed
**And** when the user enters whitespace or empty values in either field
**Then** appropriate validation feedback should be shown
**And** the user should remain on the login page in all failure cases

### AC_003 — Login Page Elements and Interaction
**Given** the user navigates to the OrangeHRM login page
**When** the page loads completely
**Then** the username input field should be visible and accept text input
**And** the password input field should be visible and mask typed characters
**And** the Login button should be visible and clickable
**And** the OrangeHRM logo should be visible on the page
**And** when valid credentials are entered and Login is clicked
**Then** the form should submit successfully and authenticate the user
**And** when invalid credentials are entered and Login is clicked
**Then** the form should show an error without navigating away from the page

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
- Password masking verification