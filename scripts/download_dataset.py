import kagglehub
import os
import shutil

def download_dataset():
    print("Downloading dataset...")
    try:
        # Download latest version
        path = kagglehub.dataset_download("mehaksingal/personal-financial-dataset-for-india")
        print("Path to dataset files:", path)
        
        # List files
        files = os.listdir(path)
        print(f"Files found: {files}")
        
        # Copy to data/kaggle_dataset if possible
        dest_dir = os.path.join("data", "kaggle_dataset")
        os.makedirs(dest_dir, exist_ok=True)
        
        for file in files:
            src = os.path.join(path, file)
            dst = os.path.join(dest_dir, file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"Copied file {file}")
            elif os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"Copied directory {file}")
                
    except Exception as e:
        print(f"Error downloading dataset: {e}")

if __name__ == "__main__":
    download_dataset()
