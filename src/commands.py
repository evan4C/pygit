# command implementations

import os
import shutil

def cmd_init(args):
    # delete .pygit if it exists
    if os.path.exists(f"{args.path}/.pygit"):
        shutil.rmtree(f"{args.path}/.pygit")
        print("Overwrite the old .pygit folder")

    # create necessary folders for pygit init
    os.mkdir(f"{args.path}/.pygit")
    os.mkdir(f"{args.path}/.pygit/objects")
    os.makedirs(f"{args.path}/.pygit/refs/heads")
    with open(f"{args.path}/.pygit/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("pygit initlization finished!")

def cmd_cat(repo, args):
    type, content = repo.read_object(args.sha1_hash)
    print(f"object type is {type} and the content is {content}.")


def cmd_add():
    pass

def cmd_commit():
    pass
