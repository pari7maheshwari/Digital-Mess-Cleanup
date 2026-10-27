import re
from pathlib import Path
from typing import TypedDict

from .config import FILE_CATEGORIES
from .file_utils import get_category, is_inside, resolve_user_path


_CATEGORY_KEYWORDS = {
    "Images": (
        "image", "images", "photo", "photos", "picture", "pictures",
        "screenshot", "screenshots", "meme", "memes", "receipt", "receipts",
    ),
    "Documents": (
        "document", "documents", "doc", "docs", "pdf", "text", "note",
        "notes", "paperwork",
    ),
    "Spreadsheets": (
        "spreadsheet", "spreadsheets", "excel", "csv", "table", "sheet", "sheets",
    ),
    "Presentations": ("presentation", "presentations", "slides", "powerpoint"),
    "Videos": ("video", "videos", "movie", "movies", "film", "films"),
    "Audio": ("audio", "music", "song", "songs", "sound", "sounds"),
    "Archives": ("archive", "archives", "zip", "compressed"),
    "Code": ("code", "source", "program", "programming", "scripts"),
    "Other": ("other", "unknown", "miscellaneous", "misc"),
}
_ALL_FILES_KEYWORDS = ("all", "everything", "files", "file")
_ALL_CATEGORIES = {*FILE_CATEGORIES, "Other"}


class FileSnapshot(TypedDict):
    path: str
    size: int
    modified_ns: int


class CleanupPlan(TypedDict):
    source_folder: str
    output_folder: str
    goal: str
    scope_summary: str
    selected_categories: list[str]
    files: list[FileSnapshot]
    file_count: int
    category_counts: dict[str, int]
    image_count: int
    use_ai: bool
    model_name: str
    ai_threshold: float
    actions: list[str]


def interpret_cleanup_goal(goal: str) -> tuple[set[str], str]:
    """Map supported plain-language file-type terms to organizer categories."""
    words = set(re.findall(r"[a-z0-9]+", goal.casefold()))
    if not words:
        raise ValueError("Describe what kind of files you want to organize.")

    selected_categories = {
        category
        for category, keywords in _CATEGORY_KEYWORDS.items()
        if words.intersection(keywords)
    }

    if selected_categories or words.intersection(_ALL_FILES_KEYWORDS):
        if selected_categories:
            scope = ", ".join(sorted(selected_categories))
            return selected_categories, f"Only these file types: {scope}."
        return _ALL_CATEGORIES.copy(), "All file types."

    return (
        _ALL_CATEGORIES.copy(),
        "No file type was recognized, so all file types are included.",
    )


def _collect_file_snapshots(
    source_folder: Path,
    output_folder: Path,
    selected_categories: set[str],
) -> list[FileSnapshot]:
    files = []
    for path in source_folder.rglob("*"):
        try:
            if path.is_symlink() or not path.is_file():
                continue
            if is_inside(path, output_folder):
                continue
            if get_category(path) not in selected_categories:
                continue
            stat = path.stat()
            files.append(
                FileSnapshot(
                    path=str(path),
                    size=stat.st_size,
                    modified_ns=stat.st_mtime_ns,
                )
            )
        except OSError as error:
            raise OSError(f"Could not inspect {path}: {error}") from error

    return sorted(files, key=lambda item: str(item["path"]).casefold())


def create_cleanup_plan(
    source_folder: Path,
    output_folder: Path,
    goal: str,
    use_ai: bool,
    model_name: str,
    ai_threshold: float,
) -> CleanupPlan:
    source_folder = resolve_user_path(source_folder)
    output_folder = resolve_user_path(output_folder)

    if not source_folder.exists() or not source_folder.is_dir():
        raise ValueError("Please provide a valid existing folder.")
    if source_folder == Path(source_folder.anchor):
        raise ValueError("Please select a specific folder, not a drive root.")
    if output_folder == source_folder or is_inside(
        output_folder, source_folder
    ) or is_inside(source_folder, output_folder):
        raise ValueError(
            "The download folder must be outside the source folder and cannot "
            "contain the source folder."
        )
    if output_folder.parent.exists() and not output_folder.parent.is_dir():
        raise ValueError("The download folder's parent path is not a folder.")

    selected_categories, scope_summary = interpret_cleanup_goal(goal)
    files = _collect_file_snapshots(
        source_folder, output_folder, selected_categories
    )
    category_counts: dict[str, int] = {}
    image_count = 0
    for item in files:
        category = get_category(Path(str(item["path"])))
        category_counts[category] = category_counts.get(category, 0) + 1
        image_count += category == "Images"

    actions = [
        f"Create an organized copy for {len(files)} selected files.",
        "Detect exact duplicates and route them to a review folder.",
        "Find visually similar images and route them to a review folder.",
    ]
    if use_ai and image_count:
        actions.append(
            f"Classify up to {image_count} unique images with the selected "
            "vision model; send uncertain images for review."
        )
    actions.append(
        "Verify that copied files exist and that the source files remain."
    )

    return {
        "source_folder": str(source_folder),
        "output_folder": str(output_folder),
        "goal": goal.strip(),
        "scope_summary": scope_summary,
        "selected_categories": sorted(selected_categories),
        "files": files,
        "file_count": len(files),
        "category_counts": category_counts,
        "image_count": image_count,
        "use_ai": use_ai,
        "model_name": model_name,
        "ai_threshold": ai_threshold,
        "actions": actions,
    }


def validate_cleanup_plan(plan: CleanupPlan) -> list[Path]:
    source_folder = resolve_user_path(Path(plan["source_folder"]))
    output_folder = resolve_user_path(Path(plan["output_folder"]))
    selected_categories = set(plan["selected_categories"])
    current_files = _collect_file_snapshots(
        source_folder, output_folder, selected_categories
    )

    if current_files != plan["files"]:
        raise ValueError(
            "The source folder changed after the plan was created. "
            "Create a fresh plan before approving it."
        )
    if output_folder.parent.exists() and not output_folder.parent.is_dir():
        raise ValueError("The download folder's parent path is not a folder.")

    return [Path(item["path"]) for item in current_files]


def verify_cleanup_output(
    source_folder: Path,
    output_folder: Path,
    report_rows: list[dict[str, object]],
) -> dict[str, int]:
    missing_copies = [
        str(row.get("Output Path", ""))
        for row in report_rows
        if row.get("Status") != "Error"
        and (
            not row.get("Output Path")
            or not Path(str(row["Output Path"])).is_file()
            or not is_inside(Path(str(row["Output Path"])), output_folder)
        )
    ]
    missing_sources = [
        str(row.get("Original Path", ""))
        for row in report_rows
        if not Path(str(row.get("Original Path", ""))).is_file()
        or not is_inside(Path(str(row["Original Path"])), source_folder)
    ]

    if missing_copies:
        raise OSError(
            f"Verification failed: {len(missing_copies)} copied file(s) "
            "are missing from the output folder."
        )
    if missing_sources:
        raise OSError(
            f"Verification failed: {len(missing_sources)} source file(s) "
            "are missing or outside the selected source folder."
        )

    return {
        "verified_copies": len(report_rows) - sum(
            row.get("Status") == "Error" for row in report_rows
        ),
        "file_errors": sum(
            row.get("Status") == "Error" for row in report_rows
        ),
        "originals_preserved": len(report_rows),
    }
