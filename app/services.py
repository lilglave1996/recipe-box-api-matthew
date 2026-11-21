from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.orm_models import Recipe


def create_recipe_service(data, user_id):
    if not data or not data.get("title") or not data.get("ingredients"):
        return None, "title and ingredients are required"

    recipe = Recipe(
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data.get("instructions", ""),
        is_public=1 if data.get("is_public", True) else 0,
        owner_id=user_id,
    )

    try:
        db.session.add(recipe)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return None, "a recipe with that title already exists"

    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
    }, None


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
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return None, "recipe not found", 404

    if int(recipe.owner_id) != user_id and role != "admin":
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

    for column, value in changes.items():
        setattr(recipe, column, value)

    db.session.commit()

    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
    }, None, 200


def delete_recipe_service(recipe_id, user_id, role):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return "recipe not found", 404

    if (
        str(recipe.owner_id) != str(user_id)
        and role != "admin"
    ):
        return "you do not have permission to delete this recipe", 403

    db.session.delete(recipe)
    db.session.commit()

    return None, 204
