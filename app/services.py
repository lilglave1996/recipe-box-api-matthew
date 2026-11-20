from sqlalchemy import select
from app.extensions import db
from app.orm_models import Recipe
from app.models import (
    insert_recipe,
    find_recipe,
    update_recipe_record,
    delete_recipe_record,
)


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


def list_recipes_service():
    statement = select(Recipe).order_by(Recipe.id)
    recipes = db.session.scalars(statement).all()

    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "is_public": recipe.is_public,
        }
        for recipe in recipes
    ]


def get_recipe_service(recipe_id):
    statement = select(Recipe).where(Recipe.id == recipe_id)
    recipe = db.session.scalars(statement).one_or_none()

    if recipe is None:
        return None

    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
    }


def update_recipe_service(recipe_id, data, user_id, role):
    recipe = find_recipe(recipe_id)

    if recipe is None:
        return None, "recipe not found", 404

    if recipe["owner_id"] != user_id and role != "admin":
        return None, "you do not have permission to update this recipe", 403

    if not data:
        return None, "a JSON body is required", 400

    changes = {}

    for column in ("title", "ingredients", "instructions"):
        if column in data:
            changes[column] = data[column]

    if "is_public" in data:
        changes["is_public"] = 1 if data["is_public"] else 0

    if not changes:
        return None, "nothing to update", 400

    updated_recipe = update_recipe_record(recipe_id, changes)

    if updated_recipe is None:
        return None, "recipe not found", 404

    return updated_recipe, None, 200


def delete_recipe_service(recipe_id, user_id, role):
    recipe = find_recipe(recipe_id)

    if recipe is None:
        return "recipe not found", 404

    if recipe["owner_id"] != user_id and role != "admin":
        return "you do not have permission to delete this recipe", 403

    delete_recipe_record(recipe_id)

    return None, 204
