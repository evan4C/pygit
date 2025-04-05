# reading/writing the index file in the staging area, index file includes file mode, sha1 hash, file path.
import os 
import logging
import collections
import stat

logger = logging.getLogger(__name__)

IndexEntry = collections.namedtuple("IndexEntry", ["mode", "sha1", "path"])

class Index:
    """Manage the pygit index file (.pygit/index)"""

    def __init__(self, repo):
        self.repo = repo
        self.index_path = repo.index_file
        self.entries = {}
    
    def load(self):
        """Load index entries from the index file"""

        self.entries = {}
        if not os.path.exists(self.index_path):
            logger.info(f"Index file not found at {self.index_path}")
            return 
        
        logger.debug(f"Loading index from {self.index_path}")
        with open(self.index_path, "r") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue # skip empty line

                parts = line.split(" ", 2)
                if len(parts) != 3:
                    logger.warning(f"Skipping malformed line {line_num+1} in index: '{line}'")

                mode_str, sha1, path = parts
                mode = int(mode_str, 8)

                entry = IndexEntry(mode, sha1, path)
                self.entries[path] = entry

        logger.info(f"Loaded {len(self.entries)} entries in index")

    def save(self):
        """Save the current index entries to the index file"""
        logger.info(f"Saving {len(self.entries)} entries to index {self.index_path}")

        sorted_paths = sorted(self.entries.keys())
        with open(self.index_path, "w") as f:
            for path in sorted_paths:
                entry = self.entries[path]
                mode_oct = oct(entry.mode)[2:]
                f.write(f"{mode_oct} {entry.sha1} {entry.path}\n")

        logger.info(f"Successfully saved index to {self.index_path}")

    def add(self, path, sha1, mode):
        """Add an entry in the index"""

        logger.info("Adding an entry in the index")
        if not isinstance(mode, int):
            mode = int(mode)
        
        entry = IndexEntry(mode, sha1, path)
        self.entries[path] = entry

    def get_entries(self):
        """Return a list of index entries"""

        return [self.entries[path] for path in sorted(self.entries.keys())]
