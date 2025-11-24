import kagglehub
import shutil
import os
import glob

print("⬇️ Downloading dataset from Kaggle...")
path = kagglehub.dataset_download("vishnu0399/server-logs")

print("Path to dataset files:", path)

# Check for TestFileGenerator.py
generator_path = os.path.join(path, "TestFileGenerator.py")
if os.path.exists(generator_path):
    shutil.copy(generator_path, "TestFileGenerator.py")
    print("✅ Copied TestFileGenerator.py to current directory")
else:
    print("❌ TestFileGenerator.py not found")
    # List all files again to be sure
    for root, dirs, files in os.walk(path):
        for file in files:
            print(os.path.join(root, file))
