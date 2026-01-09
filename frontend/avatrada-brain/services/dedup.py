import os
import hashlib

class LibraryCleaner:
    def __init__(self):
        self.root = "/home/avacado/avatrada/avatrada-brain/knowledge/library"

    def get_file_hash(self, filepath):
        """Generates SHA256 hash of file content for precise matching."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def clean(self):
        print(f"🧹 Scanning {self.root} for duplicates...")
        seen_hashes = {}
        duplicates_removed = 0
        
        # Walk recursively through the library
        for root, dirs, files in os.walk(self.root):
            for filename in files:
                if filename.endswith(('.md', '.txt')):
                    filepath = os.path.join(root, filename)
                    file_hash = self.get_file_hash(filepath)
                    
                    if file_hash in seen_hashes:
                        # Collision found! This is a duplicate.
                        original = seen_hashes[file_hash]
                        print(f"❌ Duplicate found: {filename}")
                        print(f"   Original: {original}")
                        print(f"   Deleting: {filepath}")
                        os.remove(filepath)
                        duplicates_removed += 1
                    else:
                        # Register unique file
                        seen_hashes[file_hash] = filepath

        print(f"✨ Cleanup complete. Removed {duplicates_removed} duplicate files.")
        
        # Verify current count
        remaining = 0
        for root, dirs, files in os.walk(self.root):
            remaining += len([f for f in files if f.endswith(('.md', '.txt'))])
        print(f"📚 Library now contains {remaining} unique documents.")

if __name__ == "__main__":
    LibraryCleaner().clean()
