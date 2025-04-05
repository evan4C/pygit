import os
import hashlib
import zlib


class Repository:
    """Represents a Pygit repository."""

    def __init__(self, path):
        self.worktree = self._find_worktree(path)
        if not self.worktree:
            raise Exception(f"Not a pygit repository: {path}")
        self.gitdir = os.path.join(self.worktree, ".pygit")
        self.objectdir = os.path.join(self.gitdir, "objects")
        self.refdir = os.path.join(self.gitdir, "refs")
        self.headdir = os.path.join(self.gitdir, "heads")
        self.index_file = os.path.join(self.gitdir, "index")
        self.head_file = os.path.join(self.gitdir, "HEAD")

    def _find_worktree(self, path):
        """Searches upwards from path for a directory containing .pygit"""

        abs_path = os.path.abspath(path)
        pygit_path = os.path.join(abs_path, ".pygit")

        if os.path.isdir(pygit_path):
            return abs_path
        
        parent_path = os.path.dirname(abs_path)
        if parent_path == abs_path:
            return None

        return self._find_worktree(parent_path)

    def _calculate_object_path(self, sha1_hash):
        """Calculates the full path of an object with a given hash."""
        
        # calculate subdir path
        subdir_path = os.path.join(self.objectdir, sha1_hash[:2])
        object_path = os.path.join(subdir_path, sha1_hash)
        return object_path

    def write_object(self, content_bytes, obj_type):
        """Write object data (blob, commit, tree) to the object store."""
        valid_types = {"blob", "commit", "tree"}
        if obj_type not in valid_types:
            raise ValueError(f"Invalid object type: {obj_type}")

        # Construct header
        header = f"{obj_type} {len(content_bytes)}\0"

        # Combine head and data
        header_bytes = header.encode("utf-8")
        full_data = header_bytes + content_bytes

        # Calculate the sha1-hash
        sha1_hash = hashlib.sha1(full_data).hexdigest()

        # Determine the path
        object_path = self._calculate_object_path(sha1_hash)

        # Check existance
        if os.path.exists(object_path):
            return sha1_hash

        # Create subdirectory
        object_subdir = os.path.dirname(object_path)
        os.makedirs(object_subdir, exist_ok=True)

        # Compress data
        cmp_data = zlib.compress(full_data)

        # Write file
        try:
            with open(object_path, "wb") as f:
                f.write(cmp_data)
        except IOError as e:
            raise IOError(f"Failed to write object {sha1_hash}: {e}")

        return sha1_hash

    def read_object(self, sha1_hash):
        """Read an object from the object store given its sha1 hash"""

        object_path = self._calculate_object_path(sha1_hash)

        with open(object_path, "rb") as f:
            cmp_data = f.read()

        decmp_data = zlib.decompress(cmp_data)

        null_byte_index = decmp_data.find(b'\0')

        header_bytes = decmp_data[:null_byte_index]
        content_bytes = decmp_data[null_byte_index+1:]

        type_bytes, len_bytes = header_bytes.split(b' ')
        obj_type = type_bytes.decode("utf-8")
        obj_len = int( len_bytes.decode("utf-8") )

        # validate the content length
        actual_len = len(content_bytes)
        if obj_len != actual_len:
            raise Exception("object length is invalid!")

        return obj_type, content_bytes



