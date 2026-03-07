import os
import shutil
from functools import reduce

# 1. Create a text file and write sample data
with open("sample.txt", "w") as f:
    f.write("Line 1: Hello, World!\n")
    f.write("Line 2: Python is great.\n")
    f.write("Line 3: File handling is easy.\n")

# 3. Append new lines
with open("sample.txt", "a") as f:
    f.write("Line 4: This line was appended.\n")
    f.write("Line 5: Appending is useful!\n")