import os
import shutil
from functools import reduce

# 1. Create nested directories
os.makedirs("project/src/utils", exist_ok=True)
os.makedirs("project/data/raw", exist_ok=True)

# Create some files to work with
for name in ["main.py", "helper.py", "notes.txt", "data.csv"]:
    open(f"project/src/{name}", "w").close()
open("project/data/raw/dataset.csv", "w").close()

# 2. List files and folders
for root, dirs, files in os.walk("project"):
    level = root.replace("project", "").count(os.sep)
    indent = "  " * level
    print(f"{indent} {os.path.basename(root)}/")
    for file in files:
        print(f"{indent}  {file}")

# 3. Find files by extension
print("\n3. Finding all .py files in 'project/':")
py_files = [
    os.path.join(root, f)
    for root, _, files in os.walk("project")
    for f in files
    if f.endswith(".py")
]
for path in py_files:
    print(f"{path}")

print("\nFinding all .csv files in 'project/':")
csv_files = [
    os.path.join(root, f)
    for root, _, files in os.walk("project")
    for f in files
    if f.endswith(".csv")
]
for path in csv_files:
    print(f"{path}")
