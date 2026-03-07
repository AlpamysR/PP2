import os
import shutil
from functools import reduce

# 4. Copy and back up files using shutil
shutil.copy("sample.txt", "sample_backup.txt")

# 5. Delete files safely
if os.path.exists("sample_backup.txt"):
    os.remove("sample_backup.txt")
    print(" 5. Deleted 'sample_backup.txt' safely using os.remove()")
else:
    print(" 5. File not found, nothing to delete.")

