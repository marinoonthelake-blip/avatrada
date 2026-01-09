import json
import os
import logging

class ExclusionListManager:
    """
    Manages a static list of restricted symbols for compliance.
    """
    def __init__(self, file_path: str = "src/restricted_symbols.json"):
        self.file_path = file_path
        self.restricted_set = set()
        self.logger = logging.getLogger("ExclusionList")
        self.load_list()

    def load_list(self):
        """Loads the restricted symbols from the JSON file."""
        # Check both relative and absolute paths for robustness in different environments
        possible_paths = [self.file_path, os.path.join("/app", self.file_path)]

        target_path = None
        for path in possible_paths:
            if os.path.exists(path):
                target_path = path
                break

        if not target_path:
            self.logger.warning(f"Exclusion list file not found in: {possible_paths}")
            return

        try:
            with open(target_path, 'r') as f:
                data = json.load(f)
                symbols = data.get("restricted_symbols", [])
                self.restricted_set = {s.upper() for s in symbols}
                self.logger.info(f"Loaded {len(self.restricted_set)} restricted symbols from {target_path}.")
        except Exception as e:
            self.logger.error(f"Failed to parse exclusion list: {e}")

    def is_restricted(self, symbol: str) -> bool:
        """Checks if a symbol is on the restricted list."""
        return symbol.upper() in self.restricted_set

exclusion_list = ExclusionListManager()
