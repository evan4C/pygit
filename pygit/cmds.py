# command implementations

import os
import shutil
import time
import stat
from pygit.repository import Repository
from pygit.index import Index
import logging

logger=logging.getLogger(__name__)

def init(args):
    # delete .pygit if it exists
    if os.path.exists(f"{args.path}/.pygit"):
        shutil.rmtree(f"{args.path}/.pygit")
        logger.info("Overwrite the old .pygit folder")

    # create necessary folders for pygit init
    os.makedirs(f"{args.path}/.pygit")
    os.makedirs(f"{args.path}/.pygit/objects")
    os.makedirs(f"{args.path}/.pygit/refs/heads")
    with open(f"{args.path}/.pygit/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    logger.info("pygit initlization finished!")

def cat(repo, args):
    obj_type, content_bytes = repo.read_object(args.sha1_hash)
    content = content_bytes.decode("utf-8")
    print(f"Object type: {obj_type}")
    print("-" * 20)
    print(content)
    print("-" * 20)
    logger.info(f"Display object {args.sha1_hash}")

def add(repo: Repository, args):
    """Add file contents to the index""" 
    logger.info(f"Executing 'add' command for files: {args.files}")
    index = Index(repo)
    index.load()

    added_files = 0
    for file_path in args.files:
        abs_path = os.path.abspath(file_path)

        if not abs_path.startswith(repo.worktree):
            logger.error(f"Add failed: Path {abs_path} is outside worktree {repo.worktree}")
            continue # skip this file
        
        rel_path = os.path.relpath(abs_path, repo.worktree).replace(os.sep, '/')
        
        if not os.path.exists(abs_path):
            if rel_path in index.entries:
                del index.entries[rel_path]
                logger.info(f"Remove deleted file {rel_path} from index")
            continue
        
        if os.path.isdir(abs_path):
            logger.warning(f"Skipping dir add for: {abs_path}")
            continue

        # read file contents as bytes
        with open(abs_path, "rb") as f:
            content_bytes = f.read()
        
        # write blob object
        sha1 = repo.write_object(content_bytes, "blob")

        # get file mode
        st = os.stat(abs_path)
        # git store 100644 for regular files or 100755 for executable files
        is_executable = bool(st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        mode = 0o100755 if is_executable else 0o100644

        # add entry to index
        index.add(rel_path, sha1, mode)
        added_files += 1 

    # save the updated index
    if added_files > 0:
        index.save()
        logger.info(f"add command finished, added {added_files} files")

def commit(repo: Repository, args):
    """Record changes to the repository""" 

    logger.info(f"Executing commit command with message: {args.message}")
    index = Index(repo)
    index.load()
    entries = index.get_entries

    if not entries:
        logger.warning("Commit attempted with an empty index")
        return


    # build tree object
    tree_content = b""
    for entry in entries:
        # format: <mode> <path>\0<sha1_bytes>
        path_bytes = entry.path.encode("tef-8")
        sha1_bytes = bytes.fromhex(entry.sha1)
        mode_bytes = str(oct(entry.mode[2:]).encode("utf-8"))

        tree_content += mode_bytes + b" " + path_bytes + b"\0" + sha1_bytes
        logger.info(f"Adding to tree: mode={mode_bytes.decode()}, path={entry.path}, sha1={entry.sha1}")

        tree_sha1 = repo.write_object(tree_content, "tree")
        logger.info(f"created tree object: {tree_sha1}")

    # determine parent commit
    parent_sha1 = repo.resolve_ref("HEAD")
    if parent_sha1:
        parent_type, _ = repo.read_object(parent_sha1)
        if parent_type != "commit":
            logger.error(f"Parent object {parent_sha1} is not a commit")
            return

    # format commit object and create commit content bytes
    author_name = "dummy user" 
    author_email = "dummy@example.com"
    time_stamp = int(time.time())
    timezone = time.strftime("%z", time.localtime(time_stamp))

    commit_content_lines = []
    commit_content_lines.append(f"tree {tree_sha1}")
    if parent_sha1:
        commit_content_lines.append(f"parent {parent_sha1}")
    commit_content_lines.append(f"author: {author_name} <{author_email}> {time_stamp} {timezone}") 
    commit_content_lines.append(f"committer: {author_name} <{author_email}> {time_stamp} {timezone}") 
    commit_content_lines.append("") # empty line before real message
    commit_content_lines.append(args.message)

    commit_content = "\n".join(commit_content_lines) + "\n"
    commit_content_bytes = commit_content.encode("utf-8")

    # write commit object
    commit_sha1 = repo.write_object(commit_content_bytes, "commit")
    logger.info(f"created commit object: {commit_sha1}")

    # update HEAD/Branch ref
    current_branch_ref = repo.get_current_branch_ref()
    if current_branch_ref:
        repo.update_ref(current_branch_ref, commit_sha1)
        branch_name = current_branch_ref.split('/')[-1]
        logger.info(f"updated branch {branch_name} to commit {commit_sha1}")
    else:
        # detached HEAD or first commit on the currently non-exist default branch
        default_ref = "refs/heads/main"
        repo.update_ref(default_ref, commit_sha1)
        # also update HEAD to point to this branch now
        repo.update_ref("HEAD", default_ref, symbolic=True)
        branch_name = default_ref.split('/')[-1]
        logger.info(f"created initial commit {commit_sha1} on branch {branch_name} and updated HEAD")


