
import sqlite3

from flask import Blueprint, g, jsonify, request
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
    }


@recipes_bp.get("")
@require_auth
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

    try:
        recipe, error = create_recipe_service(
            data, g.current_user_id
        )
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    if error:
        return jsonify({"error": error}), 400

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
    except sqlite3.IntegrityError:
        return jsonify({
            "error": "a recipe with that title already exists"
        }), 409

    if error:
        return jsonify({"error": error}), status

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

    return "", 204
