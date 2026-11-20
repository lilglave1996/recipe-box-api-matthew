
from app.models import insert_recipe


def create_recipe_service(data, user_id):
    if not data or not data.get("title") or not data.get("ingredients"):
        return None, "title and ingredients are required"

    title = data["title"]
    ingredients = data["ingredients"]
    instructions = data.get("instructions", "")
    is_public = 1 if data.get("is_public", True) else 0

    recipe = insert_recipe(
        title,
        ingredients,
        instructions,
        is_public,
        user_id,
    )

    return recipe, None
