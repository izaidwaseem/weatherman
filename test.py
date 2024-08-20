import os
from glob import glob

folder_path = "Dubai_weather"
txt_files = glob(os.path.join(folder_path, "*.txt"))
print(f"Found files: {txt_files}")
