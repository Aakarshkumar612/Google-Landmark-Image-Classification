import os

# Define the folder structure
folders = [
    'data/train',
    'data/test',
    'notebooks',
    'scripts',
    'models'
]

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Successfully created: {folder}")
    else:
        print(f"Folder already exists: {folder}")

print("\nAll systems go! Project structure is ready.")