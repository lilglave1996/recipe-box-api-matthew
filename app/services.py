from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.orm_models import Recipe, Tag


def resolve_tags(tag_names):
    if not isinstance(tag_names, list):
        raise ValueError("tags must be a list")

    normalized_names = []
    seen = set()

    for name in tag_names:
        if not isinstance(name, str):
            raise ValueError("each tag must be a string")

        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("tag names cannot be empty")

        if normalized not in seen:
            seen.add(normalized)
            normalized_names.append(normalized)

    if not normalized_names:
        return []

    existing_tags = db.session.scalars(
        select(Tag).where(Tag.name.in_(normalized_names))
    ).all()

    tags_by_name = {
        tag.name: tag for tag in existing_tags
    }

    for name in normalized_names:
        if name not in tags_by_name:
            tag = Tag(name=name)
            db.session.add(tag)
            tags_by_name[name] = tag

    return [tags_by_name[name] for name in normalized_names]



def create_recipe_service(data, user_id):
    if not data or not data.get("title") or not data.get("ingredients"):
        return None, "title and ingredients are required"

    recipe = Recipe(
        title=data["title"],
        ingredients=data["ingredients"],
        instructions=data.get("instructions", ""),
        is_public=1 if data.get("is_public", True) else 0,
        owner_id=user_id,
        description=data.get("description"),
    )

    try:
        if "tags" in data:
            recipe.tags = resolve_tags(data["tags"])

        db.session.add(recipe)
        db.session.commit()

    except ValueError as error:
        db.session.rollback()
        return None, str(error)

    except IntegrityError:
        db.session.rollback()
        return None, "a recipe with that title already exists"

    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
        "description": recipe.description,
        "tags": sorted(tag.name for tag in recipe.tags),
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
            "description": recipe.description,
            "tags": sorted(tag.name for tag in recipe.tags),
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
        "description": recipe.description,
        "tags": sorted(tag.name for tag in recipe.tags),
    }




def update_recipe_service(recipe_id, data, user_id, role):
    recipe = db.session.get(Recipe, recipe_id)

    if recipe is None:
        return None, "recipe not found", 404

    owner = recipe.owner

    if role != "admin" and (
        owner is None or owner.id != int(user_id)
    ):
        return None, "you do not have permission to update this recipe", 403

    if not data:
        return None, "a JSON body is required", 400

    changes = {}

    for column in ("title", "ingredients", "instructions", "description"):
        if column in data:
            changes[column] = data[column]

    if "is_public" in data:
        changes["is_public"] = 1 if data["is_public"] else 0

    if not changes and "tags" not in data:
        return None, "nothing to update", 400

    try:
        for column, value in changes.items():
            setattr(recipe, column, value)

        if "tags" in data:
            recipe.tags = resolve_tags(data["tags"])

        db.session.commit()

    except ValueError as error:
        db.session.rollback()
        return None, str(error), 400

    except IntegrityError:
        db.session.rollback()
        return None, "a recipe with that title already exists", 409

    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "is_public": recipe.is_public,
        "description": recipe.description,
        "tags": sorted(tag.name for tag in recipe.tags),
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
