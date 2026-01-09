import os

class FilenameCleaner:
    def __init__(self):
        # We want to keep files in these specific subfolders
        self.root = "/home/avacado/avatrada/avatrada-brain/knowledge/library"
        self.preferred_dirs = ["markdown", "pdfs"]

    def clean(self):
        print(f"🧹 Scanning {self.root} for filename collisions...")
        
        # Map: filename -> list of full_paths
        registry = {}
        total_files = 0
        deleted_count = 0

        # 1. Build the registry
        for root, dirs, files in os.walk(self.root):
            for f in files:
                if f.endswith(('.md', '.txt')):
                    total_files += 1
                    if f not in registry:
                        registry[f] = []
                    registry[f].append(os.path.join(root, f))

        # 2. Identify and Delete Duplicates
        for filename, paths in registry.items():
            if len(paths) > 1:
                # We have duplicates!
                print(f"⚠️  Collision: {filename}")
                
                # Determine which one to KEEP
                # Prefer paths that contain 'markdown' or 'pdfs'
                keeper = None
                for p in paths:
                    if any(sub in p for sub in self.preferred_dirs):
                        keeper = p
                        break
                
                # If no preferred dir found, just keep the first one (deepest usually)
                if not keeper:
                    keeper = paths[0]
                
                print(f"   ✅ Keeping: {keeper}")
                
                # Delete the others
                for p in paths:
                    if p != keeper:
                        print(f"   ❌ Deleting: {p}")
                        os.remove(p)
                        deleted_count += 1
        
        print("-" * 30)
        print(f"✨ Cleanup Complete.")
        print(f"🗑️  Removed {deleted_count} duplicate files.")
        print(f"📚 Library Size: {total_files - deleted_count} documents.")

if __name__ == "__main__":
    FilenameCleaner().clean()
