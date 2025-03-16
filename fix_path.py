import os

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory {path} created")
    else:
        print(f"Directory {path} already exists")
