import os
import shutil
from tqdm import tqdm
import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Import themed tkinter for enhanced widgets
import time

"""
source_folder = ""
destination_folder = ""
log_filename = "sync_log.txt"
"""

source_folder = "L:/Research/"
destination_folder = "D:/Backup/Research/"
log_filename = "sync_log_research.txt"


def copy_with_progress(src_path, dest_path):
    total_size = os.path.getsize(src_path)
    
    # Check if the destination file already exists
    dest_dir = os.path.dirname(dest_path)
    dest_filename = os.path.basename(dest_path)
    new_dest_path = dest_path  # Initialize with the original path
    
    counter = 1  # Starting counter for adding numerical prefix
    while os.path.exists(new_dest_path):
        # Generate the new filename with a numerical prefix
        new_filename = f"({counter})_{dest_filename}"
        new_dest_path = os.path.join(dest_dir, new_filename)
        counter += 1

    with open(src_path, 'rb') as src_file:
        with open(new_dest_path, 'wb') as dest_file:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                chunk_size = 1024 * 1024
                while True:
                    chunk = src_file.read(chunk_size)
                    if not chunk:
                        break
                    dest_file.write(chunk)
                    pbar.update(len(chunk))
    return new_dest_path  # Return the path of the copied file
                   
def list_changes(source_folder, destination_folder):
    changes = []
    num_files = sum(len(files) for _, _, files in os.walk(source_folder))
    with tqdm(total=num_files, unit='file') as pbar:
        for root, _, files in os.walk(source_folder):
            for file in files:
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, source_folder)
                dest_path = os.path.join(destination_folder, relative_path)
                if not os.path.exists(dest_path):
                    changes.append(("Copy", source_path, dest_path))
                elif os.path.getsize(source_path) != os.path.getsize(dest_path):
                    changes.append(("Update", source_path, dest_path))
                pbar.update(1)
                
        for root, _, files in os.walk(destination_folder):
            for file in files:
                dest_path = os.path.join(root, file)
                relative_path = os.path.relpath(dest_path, destination_folder)
                source_path = os.path.join(source_folder, relative_path)
                
                if not os.path.exists(source_path) and not dest_path.startswith("_"):
                    renamed_dest = os.path.join(os.path.dirname(source_path), f"_{os.path.basename(source_path)}")
                    new_basename = os.path.basename(source_path)  # Starting name for renaming
                    counter = 1  # Starting counter for adding numerical prefix

                    while os.path.exists(renamed_dest):
                        # Generate the new basename with a numerical prefix
                        new_basename = f"({counter})_" + os.path.basename(source_path)
                        renamed_dest = os.path.join(os.path.dirname(source_path), new_basename)
                        counter += 1

                    changes.append(("Rename", dest_path, renamed_dest))
                pbar.update(1)
    return changes


def append_to_log(log_file, message):
    #print("\n");
    print(message);
    with open(log_file, "a", encoding="utf-8") as log:#this is added in v10
        log.write(message + "\n")

def apply_changes(changes,skip_rename=False):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #log_filename = "D:\\4_1 metarials\\syncv6_log_oldbatch.txt"
    global log_filename
   
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"Current working directory: {os.getcwd()}")
    
    for action, source, dest in changes:
        try:
            if action == "Copy":
                print("\n")
                append_to_log(log_filename, f"{timestamp} - Copy: {source} -> {dest}")
                if os.path.getsize(source) > 1024 * 1024:
                    print(f"Copying {source} to {dest}...")
                    copy_with_progress(source, dest)
                else:
                    shutil.copy2(source, dest)
            elif action == "Update":
                print("\n")
                
                #adding timestampp
                ntimestamp = int(time.time()) 

                renamed_dest = os.path.join(os.path.dirname(dest), f"_{ntimestamp}_{os.path.basename(dest)}")
                while os.path.exists(renamed_dest):
                    renamed_dest = os.path.join(os.path.dirname(dest), f"__{os.path.basename(renamed_dest)}")
                    #renamed_dest = os.path.join(os.path.dirname(source), f"_{os.path.basename(renamed_dest)}")

                os.rename(dest, renamed_dest)  # Rename existing file to _filename
                append_to_log(log_filename, f"{timestamp} - Update: {source} -> {dest}")
                #print(f"Renamed {os.path.basename(dest)} to {os.path.basename(renamed_dest)}")
                append_to_log(log_filename, f"{timestamp} - Renamed: old#{source} -> {renamed_dest}")
                
                print(f"Updating {os.path.basename(dest)}...")
                copy_with_progress(source, dest)
                

            elif action == "Rename":
                
                if skip_rename==False:
                    print("\n")
                    renamed_dest = os.path.join(os.path.dirname(source), f"_{os.path.basename(source)}")
                    #new_basename = os.path.basename(source)  # Starting name for renaming
                    #counter = 1  # Starting counter for adding numerical prefix

                    while os.path.exists(renamed_dest):
                        # Generate the new basename with a numerical prefix
                        #new_basename = f"({counter})_" + os.path.basename(source)
                        #renamed_dest = os.path.join(os.path.dirname(source), new_basename)
                        #counter += 1
                        #New style Rename, Just add _ __ ___ ____ so how
                        renamed_dest = os.path.join(os.path.dirname(source), f"_{os.path.basename(renamed_dest)}")

                    #print(f"Renaming {os.path.basename(source)} to {os.path.basename(renamed_dest)}...")
                    os.rename(source, renamed_dest)
                    append_to_log(log_filename, f"{timestamp} - Rename: Before Rename: {source} -> After Rename: {renamed_dest}")
        
        except Exception as e:
            append_to_log(log_filename, f"{timestamp} - Error: {action} {source} -> {dest} - {e}")
    append_to_log(log_filename,"================");
    print(f"Changes applied successfully. Log updated in {log_filename}")


def create_subfolders(destination_folder, relative_path):
    subfolders = os.path.dirname(relative_path)
    subfolders = subfolders.split(os.path.sep)
    current_folder = destination_folder
    for folder in subfolders:
        current_folder = os.path.join(current_folder, folder)
        if not os.path.exists(current_folder):
            os.mkdir(current_folder)




def select_source_folder():
    global source_folder
    source_folder = filedialog.askdirectory()
    source_folder_label.config(text=source_folder)

def select_destination_folder():
    global destination_folder
    destination_folder = filedialog.askdirectory()
    destination_folder_label.config(text=destination_folder)

def confirm_changes():
    confirm_button.config(state="disabled")  # Disable the button
    #confirm_button.config(state="disabled")
    source_button.config(state="disabled")
    destination_button.config(state="disabled")
    #source_folder = "F:\\Explore\\Python\\Sync\\A1"
    #destination_folder = "F:\\Explore\\Python\\Sync\\A2"
    #destination_folder = "D:\\4_1 metarials\\L4T1_old_batch\\Senior BATCH"

    if not os.path.exists(source_folder):
        tk.messagebox.showerror("Error", "Source folder does not exist. Please select a valid folder.")
        return
    if not os.path.exists(destination_folder):
        tk.messagebox.showerror("Error", "Destination folder does not exist. Please select a valid folder.")
        return
    

    changes = list_changes(source_folder, destination_folder)
    for i, (action, source, dest) in enumerate(changes, start=1):
        print(f"{i}. {action}: {source} -> {dest}")
    confirmation = input("\nConfirm all changes? (yes/no/step): ")
    if confirmation.lower() == "yes":
        sk_rename = input("\nRename File Which Dont exist? (yes/no): ")
        if sk_rename.lower() == 'yes':
            skip_rename = False
        else:
            skip_rename = True
            
        for change in changes:
            action, source, dest = change
            if action == "Copy":
                relative_path = os.path.relpath(source, source_folder)
                create_subfolders(destination_folder, relative_path)
        apply_changes(changes,skip_rename)
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
    #confirm_button.config(state="normal")  # Enable the button after processing

# Create the main GUI window
# Create the main GUI window
root = tk.Tk()
root.title("File Synchronization Tool")
root.geometry("600x400")  # Set the window dimensions

# Create a style object for themed widgets
style = ttk.Style()
style.theme_use("clam")  # Choose a theme ("clam" is one of the built-in themes)

# Create a frame with padding and background color
frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

# Create themed labels and buttons
source_label = ttk.Label(frame, text="Source Folder:")
source_folder_label = ttk.Label(frame, text=source_folder)
source_button = ttk.Button(frame, text="Select Source Folder", command=select_source_folder)

destination_label = ttk.Label(frame, text="Destination Folder:")
destination_folder_label = ttk.Label(frame, text=destination_folder)
destination_button = ttk.Button(frame, text="Select Destination Folder ", command=select_destination_folder)
#destination_button.config(state="disabled")


#source_button = tk.Button(root, text="Select Source Folder \L4T1", command=select_source_folder)
#destination_button = tk.Button(root, text="Select Destination Folder:D:\\4_1 metarials\L4T1", command=select_destination_folder)


confirm_button = ttk.Button(frame, text="Confirm Changes", command=confirm_changes)

# Organize widgets using grid layout
source_label.grid(row=0, column=0, sticky="w", pady=5)
source_folder_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
source_button.grid(row=2, column=0, columnspan=2, sticky="w")

destination_label.grid(row=3, column=0, sticky="w", pady=5)
destination_folder_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 10))
destination_button.grid(row=5, column=0, columnspan=2, sticky="w")

confirm_button.grid(row=6, columnspan=2, pady=20)

# Set the style for the confirm button
style.configure("TButton", font=("Helvetica", 12), padding=10)

# Apply styling to the main window
root.configure(bg="white")

# Run the GUI main loop
root.mainloop()