# Command line interface

import logging
import argparse
from pygit.cmds import init, add, commit, cat
from pygit.repository import Repository

logger = logging.getLogger(__name__)

def create_parser():
    """Creates the main argument parser and subparses for pygit."""
    parser = argparse.ArgumentParser(prog="pygit", description="Pygit - A simple git clone in Python.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands.", required=True)

    # Init command
    parser_init = subparsers.add_parser("init", help="Init a new, empty repository.")
    parser_init.add_argument("path", nargs="?", default=".", help="Optional path where repo should be created.")
    parser_init.set_defaults(func=init)

    # Add command
    parser_add = subparsers.add_parser("add", help="Add file contents to the index.")
    parser_add.add_argument("files", nargs="+", help="Files to add.")
    parser_add.set_defaults(func=add)

    # Commit command
    parser_commit = subparsers.add_parser("commit", help="Record changes to the repository.")
    parser_commit.add_argument("-m", "--message", required=True, help="Commit message.")
    parser_commit.set_defaults(func=commit)
    
    # Cat command
    parser_cat = subparsers.add_parser("cat-file", help="Provide content for repository objects.")
    parser_cat.add_argument("sha1-hash", help="The hash of the object to display.")
    parser_cat.set_defaults(func=cat)

    return parser

def main():
    logging.basicConfig(filename="./pygit.log", 
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                        filemode='w')

    parser = create_parser()
    args = parser.parse_args()
    if args.command == "init":
        args.func(args)
    else:
        try:
            repo = Repository(".") # find repo starting from current dir
            args.func(repo, args)
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            exit(1)

if __name__ == "__main__":
    main()
        
