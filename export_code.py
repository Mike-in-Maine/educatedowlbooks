import os

# Directories to exclude from the export
IGNORE_DIRS = {
    '__pycache__', 'migrations', 'venv', 'env', '.git', '.vscode', 
    'static', 'media', 'node_modules', '.idea'
}

# File extensions to include
INCLUDE_EXTENSIONS = {'.py', '.html', '.css', '.js', '.json'}

OUTPUT_FILE = 'project_context.txt'

def export_project():
    # Get the current working directory
    base_dir = os.getcwd()
    
    print(f"Scanning directory: {base_dir}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # Walk through the directory tree
        for root, dirs, files in os.walk(base_dir):
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                # Check extension
                _, ext = os.path.splitext(file)
                if ext in INCLUDE_EXTENSIONS and file != os.path.basename(__file__):
                    file_path = os.path.join(root, file)
                    # Get relative path for cleaner output
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    outfile.write(f"\n{'='*20}\n")
                    outfile.write(f"FILE: {rel_path}\n")
                    outfile.write(f"{'='*20}\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    
                    outfile.write("\n")

    print(f"Successfully exported project code to {OUTPUT_FILE}")

if __name__ == "__main__":
    export_project()
