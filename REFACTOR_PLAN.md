Refactor Plan
Current responsibilities in app.py
Setting up the Flask application and loading configuration.
Managing SQLite database connections and closing them.
Handling user registration and password hashing.
Handling user login and generating JWT tokens.
Validating JWT tokens and checking authentication.
Handling recipe requests (listing, viewing, creating, updating, and deleting).
Checking recipe ownership and admin permissions.
Validating request data and formatting JSON responses.
Responsibility count: 8
Counting rule: Each distinct job currently handled by app.py counts as one responsibility. Related functions performing the same job are grouped together.
Target layout
app/
├── config.py
├── auth/
│ ├── routes.py
│ └── services.py
├── recipes/
│ ├── routes.py
│ └── services.py
└── data/
└── database.py
config.py: Stores application configuration and environment settings.
auth/routes.py: Handles registration and login endpoints.
auth/services.py: Handles password hashing, JWT tokens, and authentication.
recipes/routes.py: Handles recipe endpoints and HTTP responses.
recipes/services.py: Handles recipe operations, validation, and ownership permissions.
data/database.py: Manages SQLite connections and database queries.
Each module will have its own responsibility to make the application easier to maintain and expand.
This is only a proposed structure. No code has been moved yet.
Public-contract acceptance list
Each item represents an existing request scenario that should continue working after refactoring.
GET / returns the Recipe Box API welcome message with status 200.
POST /register with valid user information creates a user and returns status 201.
POST /register with missing required information returns status 400.
POST /register with an existing username or email returns status 409.
POST /login with valid credentials returns a JWT token and status 200.
POST /login with missing credentials returns status 400.
POST /login with invalid credentials returns status 401.
GET /recipes with a valid token returns the recipe list and status 200.
GET /recipes/int:recipe_id with a valid token returns the requested recipe and status 200.
GET /recipes/int:recipe_id for a nonexistent recipe returns status 404.
POST /recipes with valid information and authentication creates a recipe and returns status 201.
POST /recipes with missing title or ingredients returns status 400 when authenticated.
POST /recipes with a duplicate title returns status 409 when authenticated.
PATCH /recipes/int:recipe_id allows the recipe owner or an admin to update a recipe and returns status 200.
PATCH /recipes/int:recipe_id without permission returns status 403.
PATCH /recipes/int:recipe_id with no valid update fields returns status 400.
DELETE /recipes/int:recipe_id allows the recipe owner or an admin to delete a recipe and returns status 204.
DELETE /recipes/int:recipe_id without permission returns status 403.
DELETE /recipes/int:recipe_id for a nonexistent recipe returns status 404.
Requests to protected recipe endpoints without an Authorization header return status 401.
Requests with an invalid or expired JWT token return status 401.
Acceptance-item count: 21
Counting rule Each bullet represents one request scenario with a specific endpoint, condition, and expected HTTP response. Different success, validation, authentication, and permission outcomes count as separate scenarios.
Refactor boundary
The internal structure of the application can change by moving routes, authentication logic, and database operations into separate modules.
The public API must remain unchanged. This includes endpoint paths, HTTP methods, status codes, JSON response bodies, authentication requirements, and database-visible effects.
Users should be able to register, log in, and manage recipes the same way before and after refactoring.
Evidence
Current application: app.py contains the Flask setup, database connections, user registration, login, JWT authentication, and recipe management endpoints.
Current database: recipes.db
Git branch: main
Git status: Working tree clean and up to date with origin/main.
Latest commit: 35339e4 - Add security audit for recipe API.
Refactoring status: No code has been moved or refactored yet.