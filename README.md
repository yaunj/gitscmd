gits
====

Run arbitrary commands on multiple git repos.

Install
-------

    python3 setup.py install

Usage
-----

Create a `.gits` file containing a list of repositories. The format is: local
path to repo, followed by whitespace, and the remote for the repo. The remote is
not used for anything yet, but should probably add support for initial cloning.

Example:

    path/to/repo/relative/from/here   https://github.com/someuser/repo.git
    other/repo/also                   https://github.com/other/code.git

From anywhere in the path under the `.gits` file, you can now run commands on
all repositories. gits will look for a `.gits` file in the current working dir,
and traverse its way up the path until it finds one.

    gits git status      # runs git status in all repos
    gits touch filename  # creates filename in all repos

gits will check if the command exists, and if it doesn't, it'll assume it's a
git sub command:

    gits add filename  # probably runs git add filename in all repos
    gits status        # probably runs git commit in all repos
