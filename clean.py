import os
import argparse
import glob
import shutil

def is_excluded(path, exclude_patterns):
    return any(glob.fnmatch.fnmatch(path, pattern) for pattern in exclude_patterns)

def remove_item(path, exclude_patterns):
    if is_excluded(path, exclude_patterns):
        print(f"Excluded: {path}")
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Removed directory: {path}")
    elif os.path.isfile(path):
        os.remove(path)
        print(f"Removed file: {path}")

def remove_egg_info(exclude_patterns):
    for item in os.listdir('.'):
        if item.endswith('.egg-info'):
            remove_item(item, exclude_patterns)

def remove_compiled_files(exclude_patterns):
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                remove_item(os.path.join(root, file), exclude_patterns)
        for dir in dirs:
            if dir == '__pycache__':
                remove_item(os.path.join(root, dir), exclude_patterns)

def remove_build_artifacts(exclude_patterns):
    for dir_name in ['build', 'dist']:
        remove_item(dir_name, exclude_patterns)

def remove_data(patterns, exclude_patterns):
    for pattern in patterns:
        for path in glob.glob(pattern):
            remove_item(path, exclude_patterns)

def main():
    parser = argparse.ArgumentParser(description="Cleanup build artifacts.")
    parser.add_argument("-r", '--remove', nargs='*', type=str, help="Remove data", default=[])
    parser.add_argument("-e", '--exclude', nargs='*', type=str, help="Exclude data", default=[])
    args = parser.parse_args()

    exclude_patterns = args.exclude

    remove_egg_info(exclude_patterns)
    remove_compiled_files(exclude_patterns)
    remove_build_artifacts(exclude_patterns)
    remove_data(args.remove, exclude_patterns)

    print("Cleanup complete.")

if __name__ == "__main__":
    main()