from pathlib import Path

import streamlit as st

from .config import (
    AI_FOLDER_NAMES,
    AI_MODEL_NAME,
    IMAGE_EXTENSIONS,
    SIMILARITY_THRESHOLD,
)
from .file_utils import (
    copy_to_folder, get_category, get_file_hash,
    get_image_hash, is_inside, resolve_user_path
)
from .ai_classifier import classify_image_with_ai


def _hash_bands(image_hash, band_count: int) -> list[tuple[int, int]]:
    value = int(str(image_hash), 16)
    bit_count = image_hash.hash.size
    band_count = min(max(band_count, 1), bit_count)
    bands = []

    for band_index in range(band_count):
        start = band_index * bit_count // band_count
        end = (band_index + 1) * bit_count // band_count
        width = end - start
        shift = bit_count - end
        bands.append((band_index, (value >> shift) & ((1 << width) - 1)))

    return bands


def scan_and_organize(

    source_folder: Path,

    output_folder: Path,
    use_ai: bool,
    ai_threshold: float,
    ai_model_name: str = AI_MODEL_NAME,
    planned_files: list[Path] | None = None,

):

    """

    Scan a folder and copy its files to a new organized folder.



    Exact duplicates and similar images are moved into review folders

    in the output copy. Original files are never moved or deleted.

    """

    source_folder = resolve_user_path(source_folder)



    if not source_folder.exists() or not source_folder.is_dir():

        raise ValueError("Please provide a valid existing folder.")



    # Prevent scanning a filesystem root or a home directory accidentally.

    if source_folder == Path(source_folder.anchor):

        raise ValueError("Please select a specific folder, not a drive root.")



    output_folder = resolve_user_path(output_folder)
    if output_folder == source_folder or is_inside(source_folder, output_folder):
        raise ValueError(
            "The output folder cannot be the source folder or contain it."
        )
    if output_folder.exists():
        if not output_folder.is_dir():
            raise ValueError("The output path exists and is not a folder.")
        if any(output_folder.iterdir()):
            raise ValueError(
                "The output folder is not empty. Choose an empty or new folder."
            )
    else:
        output_folder.mkdir(parents=True, exist_ok=False)



    duplicate_folder = output_folder / "Duplicate_Review"

    similar_folder = output_folder / "Similar_Images_Review"

    uncertain_folder = output_folder / "Images_Review"



    # Do not follow symbolic links. Skip files within the output directory.

    files = list(planned_files) if planned_files is not None else []

    if planned_files is None:
        for path in source_folder.rglob("*"):
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                if is_inside(path, output_folder):
                    continue
                files.append(path)
            except OSError:
                continue



    files.sort(key=lambda path: str(path).lower())



    seen_hashes = {}

    known_image_hashes = []
    image_hash_buckets = {}

    report_rows = []



    total_files = len(files)

    progress = st.progress(0, text="Preparing to scan files...")

    status_text = st.empty()



    for index, file_path in enumerate(files, start=1):

        general_category = get_category(file_path)

        file_hash = ""

        ai_label = ""

        ai_score = None

        duplicate_of = ""

        error_message = ""

        result_status = "Organized"

        final_category = general_category



        try:

            file_hash = get_file_hash(file_path)



            # Exact duplicate check takes priority.

            if file_hash in seen_hashes:

                duplicate_of = str(seen_hashes[file_hash])

                destination = copy_to_folder(

                    file_path, duplicate_folder

                )

                result_status = "Exact Duplicate"

                final_category = "Duplicate_Review"



            else:

                # Only compare images for visual similarity.

                is_image = (

                    file_path.suffix.lower() in IMAGE_EXTENSIONS

                )



                current_image_hash = (

                    get_image_hash(file_path) if is_image else None

                )

                similar_match = None
                if current_image_hash is not None:
                    candidate_indices = set()
                    # Any pair within the threshold must share at least one band.
                    band_count = SIMILARITY_THRESHOLD + 1
                    for band_index, band_value in _hash_bands(
                        current_image_hash, band_count
                    ):
                        candidate_indices.update(
                            image_hash_buckets.get(
                                (band_index, band_value), ()
                            )
                        )

                    for candidate_index in sorted(candidate_indices):
                        prior_path, prior_hash = known_image_hashes[
                            candidate_index
                        ]
                        if (
                            current_image_hash - prior_hash
                            <= SIMILARITY_THRESHOLD

                        ):

                            similar_match = prior_path

                            break



                if similar_match is not None:

                    duplicate_of = str(similar_match)

                    destination = copy_to_folder(

                        file_path, similar_folder

                    )

                    result_status = "Similar Image"

                    final_category = "Similar_Images_Review"



                else:

                    if current_image_hash is not None:
                        image_index = len(known_image_hashes)
                        known_image_hashes.append(
                            (file_path, current_image_hash)
                        )
                        for band in _hash_bands(
                            current_image_hash, SIMILARITY_THRESHOLD + 1
                        ):
                            image_hash_buckets.setdefault(band, []).append(
                                image_index
                            )



                    if is_image and use_ai:

                        try:

                            ai_label, ai_score = classify_image_with_ai(
                                file_path, ai_model_name
                            )



                            # Low-score predictions are routed for review.

                            if ai_score < ai_threshold:

                                destination = copy_to_folder(

                                    file_path, uncertain_folder

                                )

                                result_status = "AI Review Required"

                                final_category = "Images_Review"

                            else:

                                ai_folder_name = AI_FOLDER_NAMES.get(

                                    ai_label, "Other_Images"

                                )

                                destination = copy_to_folder(

                                    file_path,

                                    output_folder / "Images" / ai_folder_name,

                                )

                                result_status = "AI Classified"

                                final_category = (

                                    f"Images/{ai_folder_name}"

                                )



                        except Exception as ai_error:

                            # Keep the file organized even if AI inference fails.

                            destination = copy_to_folder(

                                file_path,

                                output_folder / "Images" / "AI_Unclassified",

                            )

                            result_status = "AI Classification Failed"

                            final_category = "Images/AI_Unclassified"

                            error_message = str(ai_error)



                    else:

                        destination = copy_to_folder(

                            file_path, output_folder / general_category

                        )



                    # Keep the first occurrence as the reference for exact duplicates.

                    seen_hashes[file_hash] = file_path



            report_rows.append(

                {

                    "File Name": file_path.name,

                    "Original Path": str(file_path),

                    "File Type": file_path.suffix.lower() or "(no extension)",

                    "General Category": general_category,

                    "Final Category": final_category,

                    "Status": result_status,

                    "AI Prediction": ai_label,

                    "AI Relative Score": (

                        round(ai_score, 4)

                        if ai_score is not None

                        else None

                    ),

                    "Duplicate / Similar To": duplicate_of,

                    "Output Path": str(destination),

                    "Error": error_message,

                }

            )



        except Exception as error:

            report_rows.append(

                {

                    "File Name": file_path.name,

                    "Original Path": str(file_path),

                    "File Type": file_path.suffix.lower() or "(no extension)",

                    "General Category": general_category,

                    "Final Category": "Error",

                    "Status": "Error",

                    "AI Prediction": ai_label,

                    "AI Relative Score": ai_score,

                    "Duplicate / Similar To": duplicate_of,

                    "Output Path": "",

                    "Error": str(error),

                }

            )



        progress.progress(

            index / max(total_files, 1),

            text=f"Processing {index} of {total_files}: {file_path.name}",

        )

        status_text.caption(f"Scanned {index} of {total_files} files")



    progress.empty()

    status_text.empty()



    return output_folder, report_rows





# --------------------------------------------------

# SIDEBAR

# --------------------------------------------------
