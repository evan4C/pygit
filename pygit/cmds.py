# command implementations

import os
import shutil

def init(args):
    # delete .pygit if it exists
    if os.path.exists(f"{args.path}/.pygit"):
        shutil.rmtree(f"{args.path}/.pygit")
        print("Overwrite the old .pygit folder")

    # create necessary folders for pygit init
    os.makedirs(f"{args.path}/.pygit")
    os.makedirs(f"{args.path}/.pygit/objects")
    os.makedirs(f"{args.path}/.pygit/refs/heads")
    with open(f"{args.path}/.pygit/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("pygit initlization finished!")

def cat(repo, args):
    type, content_bytes = repo.read_object(args.sha1_hash)
    content = content_bytes.decode("utf-8")
    print(f"object type is {type} and the content is {content}.")


def add():
    pass

def commit():
    pass
