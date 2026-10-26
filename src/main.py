import os
import shutil
from pathlib import Path

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

    print(f"Organizing files in: {target_path.resolve()}\n")
    moved_count = 0

    # 2. Iterate through all items in the target directory
    for item in target_path.iterdir():
        # Skip directories to prevent moving folders into folders
        if item.is_dir():
            continue
            
        # Skip hidden files (like .DS_Store on macOS or system files)
        if item.name.startswith('.'):
            continue

        # Get the file extension in lowercase
        file_extension = item.suffix.lower()
        
        # 3. Match the extension to a category
        destination_category = "Others"  # Default fallback folder
        for category, extensions in file_categories.items():
            if file_extension in extensions:
                destination_category = category
                break

        # 4. Define target path and create the folder if it doesn't exist
        category_folder = target_path / destination_category
        category_folder.mkdir(exist_ok=True)

        # 5. Move the file
        destination_file_path = category_folder / item.name
        
        try:
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
