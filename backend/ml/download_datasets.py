import os
import sys
import argparse
import subprocess

def check_kaggle_credentials():
    """
    Checks if Kaggle credentials exist in environment variables or user home folder.
    """
    home = os.path.expanduser("~")
    kaggle_json = os.path.join(home, ".kaggle", "kaggle.json")
    if os.path.exists(kaggle_json):
        return True
    if "KAGGLE_USERNAME" in os.environ and "KAGGLE_KEY" in os.environ:
        return True
    return False

def show_kaggle_instructions():
    """
    Prints a clear configuration guide for setting up Kaggle credentials.
    """
    print("\n" + "=" * 70)
    print(" WARNING: KAGGLE API CREDENTIALS NOT FOUND!")
    print("=" * 70)
    print("To download Kaggle datasets automatically, please follow these instructions:")
    print("1. Register or Log in to Kaggle: https://www.kaggle.com/")
    print("2. Navigate to Settings: https://www.kaggle.com/settings")
    print("3. Click 'Create New Token' in the API section.")
    print("4. Save the downloaded 'kaggle.json' file to:")
    print("   - macOS/Linux: ~/.kaggle/kaggle.json")
    print("   - Windows: C:\\Users\\<Username>\\.kaggle\\kaggle.json")
    print("5. Or declare env variables:")
    print("   export KAGGLE_USERNAME=your_kaggle_username")
    print("   export KAGGLE_KEY=your_kaggle_api_key")
    print("=" * 70 + "\n")

def download_plantvillage_kaggle():
    """
    Downloads PlantVillage from Kaggle: emmarex/plantdisease
    """
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets", "raw"))
    os.makedirs(raw_dir, exist_ok=True)
    
    if not check_kaggle_credentials():
        show_kaggle_instructions()
        print("Please configure Kaggle credentials before calling the download command.")
        return False
        
    try:
        import kaggle
        print("Fetching 'emmarex/plantdisease' from Kaggle...")
        kaggle.api.dataset_download_files("emmarex/plantdisease", path=raw_dir, unzip=True)
        print(f"Kaggle PlantVillage dataset downloaded successfully to {raw_dir}")
        return True
    except Exception as e:
        print(f"Failed to fetch Kaggle dataset: {e}")
        return False

def download_github_dataset(repo_url, folder_name):
    """
    Clones GitHub dataset repositories.
    """
    raw_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "datasets", "raw", folder_name))
    if os.path.exists(raw_dir):
        print(f"GitHub dataset folder already exists at: {raw_dir}")
        return True
        
    try:
        print(f"Cloning {repo_url} into {raw_dir}...")
        subprocess.check_call(["git", "clone", "--depth", "1", repo_url, raw_dir])
        print("GitHub repository cloned successfully.")
        return True
    except Exception as e:
        print(f"GitHub cloning failed: {e}")
        print(f"Please manually clone {repo_url} into {raw_dir}")
        return False

def print_manual_dataset_instructions():
    """
    Prints step-by-step instructions for non-direct or manual datasets.
    """
    print("\n" + "=" * 70)
    print(" MANUAL DATASET PLACEMENT & DOWNLOAD DIRECTIONS")
    print("=" * 70)
    print("1. Mendeley Rice Disease Dataset (hx6f852hw4):")
    print("   - Download link: https://data.mendeley.com/datasets/hx6f852hw4/1")
    print("   - Extract and place folders directly inside 'backend/ml/datasets/raw/Rice/'")
    print("\n2. Dhan-Shomadhan Rice Disease Dataset (arXiv:2309.07515):")
    print("   - Details: https://arxiv.org/abs/2309.07515")
    print("   - Place extracted class folders in 'backend/ml/datasets/raw/'")
    print("\n3. Roboflow PlantDoc Dataset:")
    print("   - Download link: https://public.roboflow.com/object-detection/plantdoc")
    print("   - Download as YOLO/Classification format and extract to raw folder.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgroCare AI Raw Dataset Downloader")
    parser.add_argument(
        "--source",
        choices=["plantvillage-kaggle", "plantvillage-github", "plantdoc-github", "manual"],
        default="plantvillage-kaggle",
        help="Select dataset download source to fetch."
    )
    
    args = parser.parse_args()
    
    if args.source == "plantvillage-kaggle":
        download_plantvillage_kaggle()
    elif args.source == "plantvillage-github":
        download_github_dataset("https://github.com/spMohanty/PlantVillage-Dataset", "plantvillage_github")
    elif args.source == "plantdoc-github":
        download_github_dataset("https://github.com/pratikkayal/PlantDoc-Dataset", "plantdoc_github")
    elif args.source == "manual":
        print_manual_dataset_instructions()
