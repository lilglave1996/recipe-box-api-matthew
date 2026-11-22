# Recipe Box API — Cache Policy

## Endpoints That Should Not Be Cached

**POST /register**

This endpoint creates new user accounts and handles sensitive registration information. Its responses should not be cached or replayed.

**POST /login**

This endpoint verifies credentials and returns a JWT authentication token. Caching its response could expose a user's token or return authentication information belonging to another user.

**POST /recipes**

This endpoint creates recipes and modifies the database. Its response should reflect the newly created recipe rather than a cached result.

**PATCH /recipes/<int:recipe_id>**

This endpoint modifies an existing recipe. Its response must reflect the successful update, and authorization must be checked against the current user and recipe ownership.

**DELETE /recipes/<int:recipe_id>**

This endpoint deletes recipes. Its authorization and deletion operations must execute normally rather than reuse cached responses.

**GET /recipes/<int:recipe_id>**

I would leave individual recipe lookups uncached for now because recipe contents can change, and future authorization rules may depend on the requesting user.

## Fixed Cache Key Risk

The existing `GET /recipes` endpoint uses the fixed cache key `recipes_list`.

A fixed key means all authenticated users can share the same cached response.

Currently, my recipe listing service retrieves all recipes without user-specific filtering. However, if the endpoint is updated to show different recipes depending on ownership or visibility, the shared cache key could expose another user's private recipes.

To safely cache personalized listings, I would use a cache key that includes the authenticated user's ID and relevant request parameters, while keeping authentication and authorization checks outside the cached response.

If user-specific caching is not necessary, I would disable caching for personalized recipe listings instead.

## Cache Invalidation

Successful POST, PATCH, and DELETE requests invalidate the `recipes_list` cache entry using:

`cache.delete("recipes_list")`

Invalidation happens only after the database operation succeeds.

The cache uses `SimpleCache` with a 60-second timeout, limiting how long unchanged cached data remains available.

## Conclusion

Caching is appropriate for expensive, repeatable reads when responses are safe to share and slightly outdated information is acceptable.

Authentication responses, database writes, authorization decisions, and sensitive personalized data should not be served from a shared cache.