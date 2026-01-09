import os

def list_files(directory):
    try:
        # Default to current dir if empty string provided
        path = directory if directory and directory.strip() else "."
        items = os.listdir(path)
        return {"directory": os.path.abspath(path), "items": items}
    except Exception as e:
        return {"error": str(e)}

def read_local_file(file_path):
    try:
        with open(file_path, 'r', errors='ignore') as f:
            return {"file": file_path, "content": f.read()}
    except Exception as e:
        return {"error": str(e)}

tools_list = [list_files, read_local_file]
