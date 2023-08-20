import os
import shutil
from tqdm import tqdm
import datetime

def copy_with_progress(src_path, dest_path):
    total_size = os.path.getsize(src_path)
    
    with open(src_path, 'rb') as src_file:
        with open(dest_path, 'wb') as dest_file:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                chunk_size = 1024 * 1024  # Copy in 1 MB chunks
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break
                    dest_file.write(chunk)
                    pbar.update(len(chunk))

def list_changes(source_folder, destination_folder):
    changes = []
    
    for root, _, files in os.walk(source_folder):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, source_folder)
            dest_path = os.path.join(destination_folder, relative_path)
            
            if not os.path.exists(dest_path):
                changes.append(("Copy", source_path, dest_path))
            
            elif os.path.getsize(source_path) != os.path.getsize(dest_path):
                changes.append(("Update", source_path, dest_path))
    
    for root, _, files in os.walk(destination_folder):
        for file in files:
            dest_path = os.path.join(root, file)
            relative_path = os.path.relpath(dest_path, destination_folder)
            source_path = os.path.join(source_folder, relative_path)
            
            if not os.path.exists(source_path) and not dest_path.startswith("_"):
                changes.append(("Rename", dest_path, "+_"))
    
    return changes

def append_to_log(log_file, message):
    print("\n");
    print(message);
    with open(log_file, "a") as log:
        log.write(message + "\n")

def apply_changes(changes):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = "sync_log.txt"
    
    for action, source, dest in changes:
        try:
            if action == "Copy":
                append_to_log(log_filename, f"{timestamp} - Copy: {source} -> {dest}")
                if os.path.getsize(source) > 1024 * 1024:
                    print(f"Copying {source} to {dest}...")
                    copy_with_progress(source, dest)
                else:
                    shutil.copy2(source, dest)
            elif action == "Update":
                append_to_log(log_filename, f"{timestamp} - Update: {source} -> {dest}")
                renamed_dest = os.path.join(os.path.dirname(dest), f"_{os.path.basename(dest)}")
                os.rename(dest, renamed_dest)  # Rename existing file to _filename
                print(f"Renamed {os.path.basename(dest)} to {os.path.basename(renamed_dest)}")
                print(f"Updating {os.path.basename(dest)}...")
                copy_with_progress(source, dest)
            elif action == "Rename":
                renamed_dest = os.path.join(os.path.dirname(source), f"_{os.path.basename(source)}")
                print(f"Renaming {os.path.basename(source)} to {os.path.basename(renamed_dest)}...")
                os.rename(source, renamed_dest)
                append_to_log(log_filename, f"{timestamp} - Rename: Before Rename: {source} -> After Rename: {renamed_dest}")
        except Exception as e:
            append_to_log(log_filename, f"{timestamp} - Error: {action} {source} -> {dest} - {e}")
    append_to_log(log_filename,"================");
    print("Changes applied successfully. Log updated in sync_log.txt")

def create_subfolders(destination_folder, relative_path):
    subfolders = os.path.dirname(relative_path)
    subfolders = subfolders.split(os.path.sep)
    current_folder = destination_folder
    for folder in subfolders:
        current_folder = os.path.join(current_folder, folder)
        if not os.path.exists(current_folder):
            os.mkdir(current_folder)

# Usage
source_folder = "F:\\Explore\\Python\\Sync\\A1"
destination_folder = "F:\\Explore\\Python\\Sync\\A2"
changes = list_changes(source_folder, destination_folder)

print("Changes to be applied:")
for i, (action, source, dest) in enumerate(changes, start=1):
    print(f"{i}. {action}: {source} -> {dest}")

confirmation = input("\nConfirm all changes? (yes/no/step): ")
if confirmation.lower() == "yes":
    for change in changes:
        action, source, dest = change
        if action == "Copy":
            relative_path = os.path.relpath(source, source_folder)
            create_subfolders(destination_folder, relative_path)
    apply_changes(changes)
elif confirmation.lower() == "step":
    for change in changes:
        action, source, dest = change
        confirmation = input(f"Confirm {action} {os.path.basename(source)} to {os.path.basename(dest)}? (yes/no): ")
        if confirmation.lower() == "yes":
            if action == "Copy":
                relative_path = os.path.relpath(source, source_folder)
                create_subfolders(destination_folder, relative_path)
            apply_changes([change])
        else:
            print(f"{action} not applied.")
else:
    print("Changes not applied.")
input("\nPress Enter to exit ")
