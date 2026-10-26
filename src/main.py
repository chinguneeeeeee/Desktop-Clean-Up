import os
import re
import shutil
import hashlib
from pathlib import Path

def get_file_hash(file_path):
    """Calculates the SHA-256 hash of a file to check for identical content."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read in 64kb chunks to handle large files (like videos) efficiently
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_base_filename(filename):
    """
    Strips duplicate indicators like ' (1)', ' (2)', or ' - Copy' from the filename.
    Example: 'document (1).pdf' -> 'document.pdf'
    """
    stem = Path(filename).stem
    suffix = Path(filename).suffix
    # Remove trailing ' (1)', ' (2)', ' - Copy', etc.
    cleaned_stem = re.sub(r'(\s*\(\d+\)|\s*-\s*Copy)$', '', stem, flags=re.IGNORECASE)
    return f"{cleaned_stem}{suffix}"

def remove_duplicates(target_path):
    """Removes files with identical content or duplicate naming patterns."""
    seen_hashes = {}
    seen_base_names = {}
    removed_count = 0

    # Gather all valid files (ignore directories and hidden files)
    files = [
        item for item in target_path.iterdir() 
        if item.is_file() and not item.name.startswith('.')
    ]
    
    # Sort files by length of name first, then alphabetically.
    # This ensures original files (e.g., "file.txt") are processed and kept 
    # BEFORE numbered copies (e.g., "file (1).txt").
    files.sort(key=lambda x: (len(x.stem), x.name))

    for item in files:
        try:
            file_hash = get_file_hash(item)
            base_name = get_base_filename(item.name).lower()

            # Check 1: Identical file contents
            if file_hash in seen_hashes:
                print(f"Removed duplicate (identical content to {seen_hashes[file_hash]}): {item.name}")
                item.unlink()
                removed_count += 1
                continue

            # Check 2: Same base filename (e.g., "file (1).txt" when "file.txt" exists)
            if base_name in seen_base_names:
                print(f"Removed duplicate (similar name to {seen_base_names[base_name]}): {item.name}")
                item.unlink()
                removed_count += 1
                continue

            # If unique, record its hash and base name
            seen_hashes[file_hash] = item.name
            seen_base_names[base_name] = item.name

        except Exception as e:
            print(f"Failed to check {item.name} for duplicates: {e}")

    if removed_count > 0:
        print(f"Total duplicates removed: {removed_count}\n")
    else:
        print("No duplicates found.\n")

def organize_folder(target_directory):
    # 1. Define file categories and their corresponding extensions
    file_categories = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv"],
        "Videos": [".mp4", ".mkv", ".flv", ".avi", ".mov"],
        "Music": [".mp3", ".wav", ".aac", ".flac"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Code": [".py", ".js", ".html", ".css", ".cpp", ".json"],
        "Executables": [".exe", ".msi", ".dmg", ".sh"]
    }

    # Convert the provided string path to a Path object
    target_path = Path(target_directory)
    
    # Check if the provided path exists and is a directory
    if not target_path.exists() or not target_path.is_dir():
        print(f"Error: The path '{target_directory}' is not a valid directory.")
        return

    print(f"Scanning and organizing files in: {target_path.resolve()}\n")
    
    # 2. Remove duplicates before organizing
    remove_duplicates(target_path)

    moved_count = 0

    # 3. Iterate through all remaining items in the target directory
    for item in target_path.iterdir():
        # Skip directories to prevent moving folders into folders
        if item.is_dir():
            continue
            
        # Skip hidden files (like .DS_Store on macOS or system files)
        if item.name.startswith('.'):
            continue

        # Get the file extension in lowercase
        file_extension = item.suffix.lower()
        
        # 4. Match the extension to a category
        destination_category = "Others"  # Default fallback folder
        for category, extensions in file_categories.items():
            if file_extension in extensions:
                destination_category = category
                break

        # 5. Define target path and create the folder if it doesn't exist
        category_folder = target_path / destination_category
        category_folder.mkdir(exist_ok=True)

        # 6. Move the file (and handle conflicts if an identical file already exists inside the subfolder)
        destination_file_path = category_folder / item.name
        
        try:
            if destination_file_path.exists():
                # If a file with the same name is already in the destination folder, compare contents
                if get_file_hash(item) == get_file_hash(destination_file_path):
                    print(f"Removed {item.name}: Identical file already exists in {destination_category}/")
                    item.unlink()
                    continue

            # Using shutil.move to safely transfer files
            shutil.move(str(item), str(destination_file_path))
            print(f"Moved: {item.name} -> {destination_category}/")
            moved_count += 1
        except Exception as e:
            print(f"Failed to move {item.name}: {e}")

    print(f"\nSuccess! Total files organized: {moved_count}")

if __name__ == "__main__":
    # Replace this string with the actual path of the folder you want to clean up
    # Example: r"C:\Users\YourName\Downloads" or "/Users/YourName/Downloads"
    folder_to_clean = input("Enter the absolute path of the folder to organize: ").strip()
    
    organize_folder(folder_to_clean)