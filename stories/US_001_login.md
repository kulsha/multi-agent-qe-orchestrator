# US_001 — Login & Authentication

## Metadata
- **Story ID:** US_001
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
The login page must also handle edge cases such as empty fields,
whitespace-only input, and special characters in credentials.
After a successful login, the user must be redirected to the HR dashboard.
After a failed login, the user must remain on the login page with a clear
error message.

---

## Acceptance Criteria

### AC_001 — Successful Login with Valid Credentials
**Given** the user is on the OrangeHRM login page
**When** the user enters a valid username (Admin) and valid password (admin123)
**Then** the user should be redirected to the HR Dashboard
**And** the dashboard URL should contain /dashboard
**And** the user's name should be visible in the top navigation bar

### AC_002 — Login Fails with Invalid Password
**Given** the user is on the OrangeHRM login page
**When** the user enters a valid username (Admin) and an incorrect password
**Then** the login should fail
**And** an error message "Invalid credentials" should be displayed
**And** the user should remain on the login page

### AC_003 — Login Fails with Invalid Username
**Given** the user is on the OrangeHRM login page
**When** the user enters an invalid username and any password
**Then** the login should fail
**And** an error message "Invalid credentials" should be displayed
**And** the user should remain on the login page

### AC_004 — Login Fails with Empty Username Field
**Given** the user is on the OrangeHRM login page
**When** the user submits the login form with the username field empty
**Then** a validation message "Required" should appear below the username field
**And** no API call to the authentication endpoint should be made

### AC_005 — Login Fails with Empty Password Field
**Given** the user is on the OrangeHRM login page
**When** the user submits the login form with the password field empty
**Then** a validation message "Required" should appear below the password field
**And** no API call to the authentication endpoint should be made

### AC_006 — Login Fails with Both Fields Empty
**Given** the user is on the OrangeHRM login page
**When** the user clicks the Login button without entering any credentials
**Then** validation messages "Required" should appear below both fields
**And** the user should remain on the login page

### AC_007 — Password Field Masks Input
**Given** the user is on the OrangeHRM login page
**When** the user types into the password field
**Then** the input should be masked with dots or asterisks
**And** the field type should be "password"

### AC_008 — Login Page UI Elements Are Present
**Given** the user navigates to the OrangeHRM login page
**When** the page loads completely
**Then** the following elements should be visible:
- Username input field
- Password input field
- Login button
- OrangeHRM logo

---

## Test Data

| Field    | Valid Value | Invalid Value | Edge Case          |
|----------|-------------|---------------|--------------------|
| Username | Admin       | invaliduser   | (empty), whitespace |
| Password | admin123    | wrongpassword | (empty), whitespace |

---

## Out of Scope
- Password reset flow
- Multi-factor authentication
- Session timeout behaviour
- SSO / LDAP login