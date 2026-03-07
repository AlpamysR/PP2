import os
import shutil
from functools import reduce

# 2. Read and print file contents
with open("sample.txt", "r") as f:
    contents = f.read()
    print(contents)

#3 Verify content  
with open("sample.txt", "r") as f:
    for i, line in enumerate(f, 1):
        print(f"  [{i}] {line}", end="")
print()