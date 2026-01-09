import os

class KnowledgeEngine:
    def __init__(self):
        self.root = "/home/avacado/avatrada/avatrada-brain/knowledge"
        self.env_path = "/home/avacado/avatrada/avatrada-brain/.env"
        self.paths = {
            "doctrines": os.path.join(self.root, "doctrines"),
            "library": os.path.join(self.root, "library"),
            "states": os.path.join(self.root, "states")
        }
        self.instruction_path = os.path.join(self.root, "instructions.md")

    def _read_file(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def _read_recursive(self, directory):
        content = ""
        count = 0
        if not os.path.exists(directory): return content, count
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(('.md', '.txt')):
                    count += 1
                    with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                        content += f"\n--- SOURCE: {os.path.relpath(os.path.join(root, f), self.root)} ---\n"
                        content += file.read() + "\n"
        return content, count

    def load_context(self):
        # 1. Identity
        instr_text = self._read_file(self.instruction_path)
        
        # 2. Configuration (NEW: Reads the .env file)
        env_content = self._read_file(self.env_path)
        env_block = ""
        if env_content:
            env_block = f"\n\n=== CRITICAL SYSTEM CONFIGURATION (.env) ===\n{env_content}\n==========================================\n"

        # 3. Knowledge
        doct_text, doct_count = self._read_recursive(self.paths["doctrines"])
        lib_text, lib_count = self._read_recursive(self.paths["library"])
        stat_text, stat_count = self._read_recursive(self.paths["states"])
        
        counts = {"doctrines": doct_count, "library": lib_count, "states": stat_count}
        
        # We append the ENV block to the "States" (Reality) section
        return instr_text, doct_text, lib_text + stat_text + env_block, counts

def get_knowledge(): return KnowledgeEngine()
