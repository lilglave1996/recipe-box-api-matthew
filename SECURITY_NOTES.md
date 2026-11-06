2026-11-06

- Anonymous requester can GET `/recipes` and see all recipes (returned 200 with array of recipes, including ids 1, 2, 3, 4 before delete).
- Anonymous requester can POST `/recipes` to create a new recipe (returned 201 and created recipe with id 4).
- Anonymous requester can DELETE `/recipes/4` and remove an existing recipe (returned 204; subsequent GET `/recipes` no longer shows id 4).