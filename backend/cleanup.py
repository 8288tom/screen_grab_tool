import os
import shutil

def cleanup_screenshots_directory():
    # Path to the screenshots directory
    screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')

    # Check if the screenshots directory exists
    if not os.path.exists(screenshots_dir):
        print("Screenshots directory does not exist.")
        return

    # List all items in the screenshots directory
    for item in os.listdir(screenshots_dir):
        item_path = os.path.join(screenshots_dir, item)
        if os.path.isdir(item_path):
            # Remove the directory and all its contents
            shutil.rmtree(item_path)
        else:
            # Remove the file
            os.remove(item_path)

    print("Cleanup complete: All directories and files inside ./screenshots/ have been removed.")
