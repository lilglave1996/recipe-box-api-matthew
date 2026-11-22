
from sqlalchemy.exc import IntegrityError

from flask import Blueprint, current_app, g, jsonify, request
from app.extensions import cache
from app.security import require_auth
from app.services import (
    create_recipe_service,
    list_recipes_service,
    get_recipe_service,
    update_recipe_service,
    delete_recipe_service,
)


recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")


def recipe_response(recipe):
    return {
        "id": recipe["id"],
        "title": recipe["title"],
        "ingredients": recipe["ingredients"],
        "instructions": recipe["instructions"],
        "is_public": bool(recipe["is_public"]),
        "description": recipe["description"],
    }


@recipes_bp.get("")
@require_auth
@cache.cached(key_prefix="recipes_list")
def list_recipes():
    recipes = list_recipes_service()
    return jsonify([recipe_response(recipe) for recipe in recipes])


@recipes_bp.get("/<int:recipe_id>")
@require_auth
def get_recipe(recipe_id):
    recipe = get_recipe_service(recipe_id)

    if recipe is None:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify(recipe_response(recipe))


@recipes_bp.post("")
@require_auth
def create_recipe():
    data = request.get_json(silent=True)

    recipe, error = create_recipe_service(
        data, g.current_user_id
    )

    if error:
        if error == "a recipe with that title already exists":
            return jsonify({"error": error}), 409

        return jsonify({"error": error}), 400
    cache.delete("recipes_list")
    return jsonify(recipe_response(recipe)), 201


@recipes_bp.patch("/<int:recipe_id>")
@require_auth
def update_recipe(recipe_id):
    data = request.get_json(silent=True)

    try:
        recipe, error, status = update_recipe_service(
            recipe_id,
            data,
            g.current_user_id,
            g.current_role,
        )
    except IntegrityError:
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    if error:
        return jsonify({"error": error}), status

    cache.delete("recipes_list")
    return jsonify(recipe_response(recipe)), 200


@recipes_bp.delete("/<int:recipe_id>")
@require_auth
def delete_recipe(recipe_id):
    error, status = delete_recipe_service(
        recipe_id,
        g.current_user_id,
        g.current_role,
    )

    if error:
        return jsonify({"error": error}), status

    cache.delete("recipes_list")
    return "", 204
