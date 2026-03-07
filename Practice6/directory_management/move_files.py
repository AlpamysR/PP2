import os
import shutil
from functools import reduce

# 4. Move/copy files between directories
shutil.copy("project/src/helper.py", "project/src/utils/helper.py")
shutil.move("project/data/raw/dataset.csv", "project/data/dataset_moved.csv")

# Cleanup directories
shutil.rmtree("project")
os.remove("sample.txt")