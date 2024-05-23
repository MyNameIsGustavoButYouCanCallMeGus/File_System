    import os
    import json
    import hashlib
    import time
    import sys

    def create_file(path):
        with open(path, 'w') as f:
            f.write('')
        print(f"File created: {path}")


    def delete_file(path):
        if os.path.isfile(path):
            os.remove(path)
            print(f"File deleted: {path}")
        else:
            print(f"File not found: {path}")


    def create_directory(path):
        os.makedirs(path, exist_ok=True)
        print(f"Directory created: {path}")


    def delete_directory(path):
        if os.path.isdir(path):
            os.rmdir(path)
            print(f"Directory deleted: {path}")
        else:
            print(f"Directory not found: {path}")


    def write_file(path, content):
        with open(path, 'w') as f:
            f.write(content)
        print(f"Content written to {path}")


    def read_file(path):
        with open(path, 'r') as f:
            content = f.read()
        print(f"Content read from {path}")
        return content


    def list_directory(path):
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print(f"{subindent}{f}")


    # Система контроля версий

    def init_repo(path):
        repo_path = os.path.join(path, '.waltz')
        os.makedirs(repo_path, exist_ok=True)
        with open(os.path.join(repo_path, 'history.json'), 'w') as f:
            json.dump([], f)
        print(f"Initialized empty Waltz repository in {repo_path}")


    def get_file_hash(path):
        with open(path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()


    def commit_changes(path, message):
        repo_path = os.path.join(path, '.waltz')
        history_file = os.path.join(repo_path, 'history.json')

        with open(history_file, 'r') as f:
            history = json.load(f)

        snapshot = {}
        for root, _, files in os.walk(path):
            if '.waltz' in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                snapshot[rel_path] = get_file_hash(file_path)

        commit = {
            'timestamp': time.time(),
            'message': message,
            'snapshot': snapshot
        }

        history.append(commit)

        with open(history_file, 'w') as f:
            json.dump(history, f)

        print(f"Commit successful: {message}")


    def log_history(path):
        repo_path = os.path.join(path, '.waltz')
        history_file = os.path.join(repo_path, 'history.json')

        with open(history_file, 'r') as f:
            history = json.load(f)

        for commit in history:
            print(f"Timestamp: {time.ctime(commit['timestamp'])}")
            print(f"Message: {commit['message']}")
            print("-" * 40)


    def checkout_version(path, index):
        repo_path = os.path.join(path, '.waltz')
        history_file = os.path.join(repo_path, 'history.json')

        with open(history_file, 'r') as f:
            history = json.load(f)

        if index < 0 or index >= len(history):
            print("Invalid commit index")
            return

        commit = history[index]
        snapshot = commit['snapshot']

        for file in snapshot:
            file_path = os.path.join(path, file)
            if os.path.exists(file_path):
                os.remove(file_path)
            if snapshot[file] is not None:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(snapshot[file])

        print(f"Checked out to commit {index} - {commit['message']}")


    def diff_versions(path, index1, index2):
        repo_path = os.path.join(path, '.waltz')
        history_file = os.path.join(repo_path, 'history.json')

        with open(history_file, 'r') as f:
            history = json.load(f)

        if index1 < 0 or index1 >= len(history) or index2 < 0 or index2 >= len(history):
            print("Invalid commit index")
            return

        snapshot1 = history[index1]['snapshot']
        snapshot2 = history[index2]['snapshot']

        added = []
        removed = []
        modified = []

        all_files = set(snapshot1.keys()).union(set(snapshot2.keys()))

        for file in all_files:
            if file not in snapshot1:
                added.append(file)
            elif file not in snapshot2:
                removed.append(file)
            elif snapshot1[file] != snapshot2[file]:
                modified.append(file)

        print(f"Files added: {added}")
        print(f"Files removed: {removed}")
        print(f"Files modified: {modified}")

    def main():
        commands = {
            'init': init_repo,
            'add': create_file,
            'commit': commit_changes,
            'log': log_history,
            'checkout': checkout_version,
            'diff': diff_versions,
            'create_file': create_file,
            'delete_file': delete_file,
            'create_directory': create_directory,
            'delete_directory': delete_directory,
            'write_file': write_file,
            'read_file': read_file,
            'list_directory': list_directory,
        }

        if len(sys.argv) < 2:
            print("Usage: waltz <command> [<args>]")
            return

        command = sys.argv[1]
        args = sys.argv[2:]

        if command in commands:
            commands[command](*args)
        else:
            print(f"Unknown command: {command}")


    if __name__ == "__main__":
        main()
