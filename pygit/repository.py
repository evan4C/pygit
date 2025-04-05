import os
import hashlib
import zlib
import logging

logger = logging.getLogger(__name__)

class Repository:
    """Represents a Pygit repository."""

    def __init__(self, path):
        self.worktree = self._find_worktree(path)
        if not self.worktree:
            logger.error(f"Not a pygit repository: {path}")
            raise Exception(f"Not a pygit repository: {path}")
        self.gitdir = os.path.join(self.worktree, ".pygit")
        self.objectdir = os.path.join(self.gitdir, "objects")
        self.refdir = os.path.join(self.gitdir, "refs")

        self.index_file = os.path.join(self.gitdir, "index")
        self.head_file = os.path.join(self.gitdir, "HEAD")

        logger.info(f"Initialized repository instance for worktree: {self.worktree}")

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
        
        # ensure hash is correct
        if len(sha1_hash) != 40 or not all(c in '0123456789abcdef' for c in sha1_hash):
            raise ValueError(f"invalid sha1-hash: {sha1_hash}")

        # calculate subdir path
        subdir_path = os.path.join(self.objectdir, sha1_hash[:2])
        object_path = os.path.join(subdir_path, sha1_hash[2:])
        logging.debug(f"Calculated object path for {sha1_hash}: {object_path}")
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
        logger.debug(f"Calculated sha1 for {obj_type} object: {sha1_hash}")

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
                logger.info(f"Successfully wrote object {sha1_hash} to {object_path}")
        except IOError as e:
            logger.error(f"Failed to write object {sha1_hash}: {e}")
            raise IOError(f"Failed to write object {sha1_hash}: {e}")

        return sha1_hash

    def read_object(self, sha1_hash):
        """Read an object from the object store given its sha1 hash"""
        
        logger.debug(f"Attempting to read object: {sha1_hash}")
        object_path = self._calculate_object_path(sha1_hash)

        if not os.path.exists(object_path):
            logger.error(f"Object not found at path: {sha1_hash}")
            raise FileNotFoundError(f"Object {sha1_hash} not found")

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

    def resolve_ref(self, ref):
        """Resolve a ref (e.g. HEAD) to a sha1 hash."""

        logger.info(f"Resolving ref: {ref}")

        if ref == "HEAD":
            with open(self.head_file, "r") as f:
                content = f.readline().strip()

            if content.startswith("ref: "):
                des_ref = content[len("ref: "):]
                logger.info(f"HEAD is a ref to {des_ref}")
                return self.resolve_ref(des_ref)
            else: 
                logger.info(f"Head is detached, pointing to: {content}")
                return content

        # other refs, like branches, tags
        ref_path = os.path.join(self.gitdir, ref)
        if os.path.exists(ref_path):
            with open(ref_path, "r") as f:
                sha1 = f.readline().strip()

                if len(sha1) == 40 and all(c in '1234567890abcdef' for c in sha1):
                    return sha1
                else:
                    return None
        else:
            return None

    def update_ref(self, ref, sha1, symbolic=False):
        """Update a ref to point to a sha1"""
        logger.debug(f"Updating ref '{ref}' to '{sha1}'")

        ref_path = os.path.join(self.gitdir, ref)

        os.makedirs(os.path.dirname(ref_path))

        with open(ref_path, "w") as f:
            if symbolic:
                f.write(f"ref: {sha1}\n")
                logger.info(f"Update symbolic ref {ref} -> {sha1}")
            else:
                f.write(f"{sha1}\n")
                logger.info(f"Updated ref {ref} -> {sha1}")
    
    def get_current_branch_ref(self):
        """Get the full ref name that HEAD currently points to"""
        logger.info("Getting current branch ref from HEAD")

        with open(self.head_file, "r") as f:
            content = f.readline().strip()
        
        if content.startswith("ref: "):
            ref_name = content[len("ref: "):]
            logger.debug(f"HEAD points to branch ref: {ref_name}")
            return ref_name
        else:
            logger.debug("HEAD is detached")
            return None
