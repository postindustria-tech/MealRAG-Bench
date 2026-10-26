#!/usr/bin/env python3
"""Fetch TheMealDB recipes and write one retrieval-ready Markdown document each."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen

import yaml


API_BASE = "https://www.themealdb.com/api/json/v1/1/"
SOURCE = "TheMealDB"
LETTERS = "abcdefghijklmnopqrstuvwxyz"


def clean_text(value: Any) -> str:
    """Return a stripped string, treating API nulls as empty strings."""
    return str(value or "").strip()


def slugify(title: str) -> str:
    """Create a stable, filesystem-friendly title slug."""
    value = title.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "recipe"


def normalize_instructions(instructions: str) -> str:
    """Normalize line endings and accidental runs of blank lines only."""
    normalized = instructions.replace("\r\n", "\n").replace("\r", "\n").strip()
    return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", normalized)


def recipe_ingredients(meal: dict[str, Any]) -> list[tuple[str, str]]:
    """Return (ingredient, measure) pairs in their original API wording."""
    ingredients = []
    for number in range(1, 21):
        ingredient = clean_text(meal.get(f"strIngredient{number}"))
        if ingredient:
            ingredients.append((ingredient, clean_text(meal.get(f"strMeasure{number}"))))
    return ingredients


def parse_tags(value: Any) -> list[str]:
    return [tag.strip() for tag in clean_text(value).split(",") if tag.strip()]


def convert_recipe(meal: dict[str, Any]) -> dict[str, Any] | None:
    """Convert one API record to metadata and Markdown, or reject an invalid record."""
    recipe_id = clean_text(meal.get("idMeal"))
    title = clean_text(meal.get("strMeal"))
    instructions = normalize_instructions(clean_text(meal.get("strInstructions")))
    ingredients = recipe_ingredients(meal)

    if not recipe_id or not title or not instructions or len(ingredients) < 2:
        return None

    metadata = {
        "id": recipe_id,
        "title": title,
        "category": clean_text(meal.get("strCategory")),
        "area": clean_text(meal.get("strArea")),
        "tags": parse_tags(meal.get("strTags")),
        "ingredient_names": [ingredient for ingredient, _ in ingredients],
        "source": SOURCE,
        "source_url": f"https://www.themealdb.com/meal/{recipe_id}",
    }
    ingredient_lines = [f"- {measure} {ingredient}".strip() if measure else f"- {ingredient}"
                        for ingredient, measure in ingredients]
    frontmatter = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False).strip()
    ingredients_markdown = "\n".join(ingredient_lines)
    markdown = (
        f"---\n{frontmatter}\n---\n\n"
        f"# {title}\n\n"
        "## Ingredients\n\n"
        f"{ingredients_markdown}\n\n"
        "## Instructions\n\n"
        f"{instructions}\n"
    )
    filename = f"{recipe_id}-{slugify(title)}.md"
    manifest = {key: metadata[key] for key in (
        "id", "title", "category", "area", "tags", "ingredient_names"
    )}
    manifest["file"] = filename
    # Keep the manifest layout predictable and aligned with the documented example.
    manifest = {"id": manifest["id"], "file": manifest["file"], **{
        key: manifest[key] for key in ("title", "category", "area", "tags", "ingredient_names")
    }}
    return {"id": recipe_id, "filename": filename, "markdown": markdown, "manifest": manifest}


def fetch_json(letter: str) -> dict[str, Any]:
    query = urlencode({"f": letter})
    with urlopen(f"{API_BASE}search.php?{query}", timeout=30) as response:  # nosec B310: fixed HTTPS API
        return json.load(response)


def fetch_all(fetcher: Callable[[str], dict[str, Any]] = fetch_json) -> dict[str, dict[str, Any]]:
    """Fetch letters a-z and deduplicate meals by their source ID."""
    meals: dict[str, dict[str, Any]] = {}
    for letter in LETTERS:
        response = fetcher(letter)
        for meal in response.get("meals") or []:
            recipe_id = clean_text(meal.get("idMeal"))
            if recipe_id and recipe_id not in meals:
                meals[recipe_id] = meal
    return meals


def sort_key(item: tuple[str, dict[str, Any]]) -> tuple[int, str, str]:
    recipe_id, meal = item
    return (int(recipe_id) if recipe_id.isdigit() else sys.maxsize, recipe_id, clean_text(meal.get("strMeal")))


def validate_dataset(recipes_dir: Path, manifest_path: Path) -> None:
    """Check the generated on-disk dataset invariants and raise ValueError on failure."""
    seen_ids: set[str] = set()
    files = sorted(recipes_dir.glob("*.md"))
    if len({path.name for path in files}) != len(files):
        raise ValueError("Duplicate recipe filenames")

    for path in files:
        content = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", content, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Missing YAML frontmatter: {path.name}")
        try:
            metadata = yaml.safe_load(match.group(1))
        except yaml.YAMLError as error:
            raise ValueError(f"Invalid YAML frontmatter: {path.name}") from error
        if not isinstance(metadata, dict) or not isinstance(metadata.get("id"), str):
            raise ValueError(f"Invalid metadata: {path.name}")
        if metadata["id"] in seen_ids:
            raise ValueError(f"Duplicate recipe ID: {metadata['id']}")
        seen_ids.add(metadata["id"])
        if "## Ingredients" not in content or "## Instructions" not in content:
            raise ValueError(f"Missing recipe sections: {path.name}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_files = [entry.get("file") for entry in manifest]
    if len(manifest_files) != len(set(manifest_files)):
        raise ValueError("Duplicate manifest filenames")
    if {path.name for path in files} != set(manifest_files):
        raise ValueError("Manifest does not correspond to generated Markdown files")
    if {entry.get("id") for entry in manifest} != seen_ids:
        raise ValueError("Manifest IDs do not correspond to generated Markdown files")


def write_dataset(meals: dict[str, dict[str, Any]], output_dir: Path, limit: int | None = None) -> dict[str, int]:
    """Convert, write, and validate a deterministic dataset from fetched records."""
    ordered_meals = [meal for _, meal in sorted(meals.items(), key=sort_key)]
    valid_recipes = [recipe for meal in ordered_meals if (recipe := convert_recipe(meal)) is not None]
    # Limit valid documents after stable sorting so --limit N consistently writes N recipes
    # whenever at least N source records pass the documented filters.
    converted = valid_recipes[:limit] if limit is not None else valid_recipes

    recipes_dir = output_dir / "recipes"
    output_dir.mkdir(parents=True, exist_ok=True)
    recipes_dir.mkdir(parents=True, exist_ok=True)
    # This directory is owned by this importer; removing old Markdown avoids stale documents.
    for path in recipes_dir.glob("*.md"):
        path.unlink()
    for recipe in converted:
        (recipes_dir / recipe["filename"]).write_text(recipe["markdown"], encoding="utf-8")

    manifest_path = output_dir / "recipes.json"
    manifest_path.write_text(
        json.dumps([recipe["manifest"] for recipe in converted], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    validate_dataset(recipes_dir, manifest_path)

    categories = {item["manifest"]["category"] for item in converted if item["manifest"]["category"]}
    areas = {item["manifest"]["area"] for item in converted if item["manifest"]["area"]}
    ingredients = {name for item in converted for name in item["manifest"]["ingredient_names"]}
    return {
        "fetched": len(meals), "valid": len(valid_recipes), "skipped": len(ordered_meals) - len(valid_recipes),
        "written": len(converted), "categories": len(categories), "areas": len(areas), "ingredients": len(ingredients),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Download TheMealDB recipes as Markdown documents.")
    parser.add_argument("--limit", type=int, help="Write the first N valid recipes after stable ID sorting.")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "downloaded")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    try:
        summary = write_dataset(fetch_all(), args.output_dir, args.limit)
    except Exception as error:
        print(f"Recipe import failed: {error}", file=sys.stderr)
        return 1

    print(f"Fetched: {summary['fetched']}")
    print(f"Valid: {summary['valid']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Written: {summary['written']}")
    print()
    print(f"Categories: {summary['categories']}")
    print(f"Areas: {summary['areas']}")
    print(f"Unique ingredients: {summary['ingredients']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
