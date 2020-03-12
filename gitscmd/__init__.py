#!/usr/bin/env python3
"""gits runs git commands (or arbitrary commands) on a set of git repositories
defined in a .gits file"""
import os
import os.path
import sys
import logging
import subprocess
import shutil


GITS_SYMBOL = '\N{GREEK SMALL LETTER PSI}'
ERROR_SYMBOL = '\N{SKULL AND CROSSBONES}'
OK_SYMBOL = '\N{CHECK MARK}'

GITS_FILENAME = '.gits'


class Colors:
    """Simple container for term colors and effects"""
    RED = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GitsFileNotFoundError(Exception):
    """Signal that we didn't find a GITS_FILENAME"""
    ...


class GitsRunner:
    """Find a list of repos in GITS_FILENAME (traversed up from cwd) and run one
    or more commands on all repos."""

    def __init__(self, cwd=os.getcwd()):
        """Initialize the stuff"""
        # TODO: Maybe clone the repos if .git folders are missing?
        logging.debug('Initializing GitsRunner')
        self.gits_root = self.__find_root(cwd)
        logging.debug('Found %s at %s', GITS_FILENAME, self.gits_root)
        self.gits_file = os.path.join(self.gits_root, GITS_FILENAME)
        self.repos = self.parse_gits()

    def __find_root(self, cwd):
        """Find first parent dir with a GITS_FILENAME in it"""
        gits_file = os.path.join(cwd, GITS_FILENAME)
        if os.path.isfile(gits_file):
            return cwd

        if cwd == '/':
            raise GitsFileNotFoundError('{} not found!'.format(GITS_FILENAME))

        parent, _ = os.path.split(cwd)
        return self.__find_root(parent)

    def parse_gits(self):
        """Parse the GITS_FILENAME and return a dict of repos"""
        logging.debug('Parsing %s', GITS_FILENAME)
        repos = {}

        with open(self.gits_file) as infile:
            for line in infile:
                try:
                    name, repo = line.strip().split()
                    repos[name] = {
                        'path': os.path.join(self.gits_root, name),
                        'remote': repo
                    }
                    logging.debug('Found repo: %s', repos[name])
                except ValueError:
                    logging.warning('Expected "dir remote", got "%s"', line.strip())
                    continue

        return repos

    def exec(self, command):
        """Run command (list of cmd + args) in all repos. If the command does
        not exist, we assume it's a git subcommand.

        Examples:
            gr.exec(['ls', '-l'])      # Runs `ls -l` in all repos
            gr.exec(['git', 'status']) # Runs `git status` in all repos
            gr.exec(['remote', '-v'])  # Probably runs `git remote -v` in all repos
        """
        result = {}

        if not shutil.which(command[0]):
            command.insert(0, 'git')

        cmdstring = ' '.join(command)

        for name, meta in self.repos.items():
            logging.info('[%s]: %s', name, cmdstring)
            logging.debug('%s: %s', name, command)
            cmdres = {'output': "", 'ok': False}

            try:
                proc = subprocess.Popen(
                    command,
                    cwd=meta['path'],
                    env=os.environ,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = proc.communicate()

                outprefix = f'  {Colors.BOLD}{GITS_SYMBOL} >'

                if len(stdout) > 0:
                    cmdres['output'] = f'{outprefix}stdout:{Colors.ENDC}\n' + stdout.decode('utf8')
                if len(stderr) > 0:
                    this_output = f'{outprefix}>stderr:{Colors.ENDC}\n' + stderr.decode('utf8')
                    if len(cmdres['output']) > 0:
                        cmdres['output'] = cmdres['output'] + "\n" + this_output
                    else:
                        cmdres['output'] = this_output

                cmdres['ok'] = True
            except FileNotFoundError:
                cmdres['output'] = f'Command not found: {command[0]}\n'
            except subprocess.CalledProcessError:
                cmdres['output'] = f'Failed to run {cmdstring}\n'

            result[name] = cmdres

        return result


def print_result(result):
    """Print the result from `exec()`, with some "pretty" formatting, and
    squeeze repeating results"""
    prev_output = None

    for repo, resultset in result.items():
        prefix = f'{Colors.BOLD}{GITS_SYMBOL} {repo}:'
        this_output = resultset['output']

        if resultset['ok']:
            color = Colors.GREEN
            symbol = OK_SYMBOL
        else:
            color = Colors.RED
            symbol = ERROR_SYMBOL

        if this_output == prev_output:
            this_output = ' ---||---'
        else:
            prev_output = this_output
            this_output = '\n' + this_output

        print(f'{prefix} {color}{symbol}{Colors.ENDC}{this_output}')
