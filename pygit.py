import os
import sys
import logging
import shutil
import time
import hashlib
import argparse

logger = logging.getLogger(__name__)

def cmd_init():
    # delete .pygit if it exists
    if os.path.exists("./.pygit"):
        shutil.rmtree("./.pygit")
        logging.warning("Overwrite the old .pygit folder")

    # create necessary folders for pygit init
    os.mkdir(".pygit")
    os.mkdir(".pygit/ogjects")
    os.makedirs(".pygit/refs/heads")
    with open(".pygit/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    logger.info("pygit initlization finished!")

def cmd_add():
    pass

def cmd_commit():
    pass

def main():
    logging.basicConfig(filename="pygit.log", 
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        filemode='w')

    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        raise RuntimeError(f"Missing argument")

    if command == "init":
       cmd_init()
    else:
        raise RuntimeError(f"Unknown cmmand #{command}")


if __name__ == "__main__":
    main()
        
