2026-11-06

- Anonymous requester can GET `/recipes` and see all recipes (returned 200 with array of recipes, including ids 1, 2, 3, 4 before delete).
- Anonymous requester can POST `/recipes` to create a new recipe (returned 201 and created recipe with id 4).
- Anonymous requester can DELETE `/recipes/4` and remove an existing recipe (returned 204; subsequent GET `/recipes` no longer shows id 4).

POST /recipes without token → Expected: 401. Observed: 401 + error.

Conclusion: Creating recipes requires authentication.

DELETE /recipes/:id
- Anonymous → 401
- Auth non-owner → 403
- Admin → 204 + resource deleted
Conclusion: Ownership and admin-role delete checks enforced correctly.

Password storage

Table: users, column: password_hash

Sample values use pbkdf2:sha256 with high iteration count and long hex hashes.

No plaintext or human-readable passwords present.

Conclusion: Passwords are stored as PBKDF2 hashes, not plaintext.

Test: GET /recipes with clearly invalid token

Expected: 401 Unauthorized (invalid identity)

Observed: 200 OK, full recipe list including non-public recipes

Conclusion: Middleware/token validation is missing or not enforced for this route. Security issue: invalid tokens are treated as authenticated.
# Recipe API Security Audit

Date: 2026-11-16  
Auditor: Matthew Glave  

## Overview

Scope: End-to-end security behavior of the Recipe API focusing on:

- Authentication (identity: valid/missing/invalid tokens)
- Authorization (ownership vs. cross-user vs. admin)
- Sensitive data storage (password hashing)
- Regression of earlier weaknesses

All tests performed against: `http://127.0.0.1:5001`

---

## 1. Authentication Behavior

### 1.1 Unauthenticated recipe creation

**Route:** `POST /recipes`  
**Request:**

```bash
curl -i -X POST http://127.0.0.1:5001/recipes \
  -H "Content-Type: application/json" \
  -d '{"title": "Unauthorized Chili", "instructions": "should not be created"}'