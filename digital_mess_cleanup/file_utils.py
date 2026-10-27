import ctypes
import hashlib
import os
import shutil
import tempfile
from ctypes import wintypes
from pathlib import Path

import imagehash
from PIL import Image, ImageOps, UnidentifiedImageError

from .config import FILE_CATEGORIES


def get_category(file_path: Path) -> str:

    """Return the general category for a file."""

    extension = file_path.suffix.lower()



    for category, extensions in FILE_CATEGORIES.items():

        if extension in extensions:

            return category



    return "Other"





def get_file_hash(file_path: Path) -> str:

    """Calculate a SHA-256 hash without loading the whole file into memory."""

    sha256 = hashlib.sha256()



    with file_path.open("rb") as file:

        for chunk in iter(lambda: file.read(1024 * 1024), b""):

            sha256.update(chunk)



    return sha256.hexdigest()





def get_image_hash(file_path: Path):

    """Calculate a perceptual hash for an image."""

    try:

        with Image.open(file_path) as image:

            image = ImageOps.exif_transpose(image).convert("RGB")

            return imagehash.phash(image)

    except (OSError, ValueError, UnidentifiedImageError):

        return None





def create_unique_folder(folder: Path) -> Path:

    """Create a new folder without overwriting an existing folder."""

    candidate = folder

    counter = 1



    while candidate.exists():

        candidate = folder.with_name(f"{folder.name}_{counter}")

        counter += 1



    candidate.mkdir(parents=True, exist_ok=False)

    return candidate





def get_unique_destination(folder: Path, filename: str) -> Path:

    """Avoid overwriting a file when two files have the same name."""

    destination = folder / filename



    if not destination.exists():

        return destination



    original = Path(filename)

    counter = 1



    while True:

        candidate = folder / (

            f"{original.stem}_{counter}{original.suffix}"

        )

        if not candidate.exists():

            return candidate

        counter += 1





def copy_to_folder(source: Path, folder: Path) -> Path:

    """Copy a file into a destination folder safely."""

    folder.mkdir(parents=True, exist_ok=True)

    destination = get_unique_destination(folder, source.name)

    shutil.copy2(source, destination)

    return destination





def is_inside(path: Path, parent: Path) -> bool:

    """Check whether path is inside parent."""

    try:

        path.resolve().relative_to(parent.resolve())

        return True

    except (ValueError, OSError):

        return False


def get_desktop_folder() -> Path:
    """Return the Windows-configured Desktop path, including redirected folders."""
    if os.name == "nt":
        known_folder = _get_windows_known_folder(
            0xB4BFCC3A,
            0xDB2C,
            0x424C,
            (0xB0, 0x29, 0x7F, 0xE9, 0x9A, 0x87, 0xC6, 0x41),
        )
        if known_folder is not None:
            return known_folder

    return Path.home() / "Desktop"


def get_downloads_folder() -> Path:
    """Return the Windows-configured Downloads path."""
    if os.name == "nt":
        known_folder = _get_windows_known_folder(
            0x374DE290,
            0x123F,
            0x4565,
            (0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B),
        )
        if known_folder is not None:
            return known_folder

    return Path.home() / "Downloads"


def _get_windows_known_folder(
    data1: int, data2: int, data3: int, data4: tuple[int, ...]
) -> Path | None:
    class Guid(ctypes.Structure):
        _fields_ = [
            ("data1", wintypes.DWORD),
            ("data2", wintypes.WORD),
            ("data3", wintypes.WORD),
            ("data4", ctypes.c_ubyte * 8),
        ]

    folder_id = Guid(
        data1,
        data2,
        data3,
        (ctypes.c_ubyte * 8)(*data4),
    )
    path_pointer = wintypes.LPWSTR()
    shell32 = ctypes.windll.shell32
    shell32.SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(Guid),
        wintypes.DWORD,
        wintypes.HANDLE,
        ctypes.POINTER(wintypes.LPWSTR),
    ]
    shell32.SHGetKnownFolderPath.restype = ctypes.c_long
    result = shell32.SHGetKnownFolderPath(
        ctypes.byref(folder_id), 0, None, ctypes.byref(path_pointer)
    )
    if result != 0 or not path_pointer.value:
        return None

    try:
        return Path(path_pointer.value)
    finally:
        ole32 = ctypes.windll.ole32
        ole32.CoTaskMemFree.argtypes = [ctypes.c_void_p]
        ole32.CoTaskMemFree(path_pointer)


def resolve_user_path(path: Path) -> Path:
    """Expand user and Windows environment variables in a supplied path."""
    return Path(os.path.expandvars(str(path))).expanduser().resolve()


def copy_folder_to_location(source: Path, destination: Path) -> Path:
    """Copy a folder to the requested path, adding a suffix when it exists."""
    source = resolve_user_path(source)
    destination = resolve_user_path(destination)

    if not source.is_dir():
        raise ValueError(f"The organized folder does not exist: {source}")
    if destination == source or is_inside(destination, source):
        raise ValueError(
            "The copy destination cannot be the organized folder or inside it."
        )
    if is_inside(source, destination):
        raise ValueError(
            "The copy destination cannot contain the organized folder."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination_base = destination
    suffix = 1
    while destination.exists():
        destination = destination_base.with_name(
            f"{destination_base.name}_{suffix}"
        )
        suffix += 1

    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{destination.name}.partial-",
            dir=destination.parent,
        )
    )
    staging.rmdir()
    try:
        shutil.copytree(source, staging, copy_function=shutil.copy2)
        expected_files = {
            path.relative_to(source): path.stat().st_size
            for path in source.rglob("*")
            if path.is_file()
        }
        copied_files = {
            path.relative_to(staging): path.stat().st_size
            for path in staging.rglob("*")
            if path.is_file()
        }
        if copied_files != expected_files:
            raise OSError(
                "Folder copy verification failed: copied files or file sizes "
                "do not match the source."
            )
        try:
            staging.rename(destination)
        except FileExistsError:
            while True:
                destination = destination_base.with_name(
                    f"{destination_base.name}_{suffix}"
                )
                suffix += 1
                if not destination.exists():
                    try:
                        staging.rename(destination)
                        break
                    except FileExistsError:
                        continue
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    return destination





# --------------------------------------------------

# AI MODEL

# --------------------------------------------------
