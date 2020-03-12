"""Command line entrypoint for gits"""
import sys
import logging

import gitscmd


def print_usage(opts):
    """Print usage of the program"""
    print('USAGE: {} [opts] command'.format(sys.argv[0]), file=sys.stderr)
    for opt, tpl in opts.items():
        print('{:>10} - set {} to {}'.format(opt, tpl[0], tpl[1]), file=sys.stderr)

    sys.exit(0)


def parse_args():
    """Parse arguments, but only look for known options, and only before the
    command to run, so we don't shadow options for e.g. ls"""

    result = {'loglevel': 'WARNING', 'help': False, 'all_output': False, 'command': None}
    opts = {
        '-a': ('all_output', True), '--all-output': ('all_output', True),
        '-v': ('loglevel', 'INFO'), '--verbose': ('loglevel', 'INFO'),
        '-d': ('loglevel', 'DEBUG'), '--debug': ('loglevel', 'DEBUG'),
        '-h': ('help', True), '--help': ('help', True),
    }

    while len(sys.argv) > 1 and sys.argv[1] in opts:
        opt = sys.argv.pop(1)
        key, value = opts[opt]

        if key == 'help':
            print_usage(opts)

        if value is None:
            # Get value from cmdline
            value = sys.argv.pop(1)

        result[key] = value

    if len(sys.argv) <= 1:
        print(f'ERROR: Missing command to run {gitscmd.ERROR_SYMBOL}', file=sys.stderr)
        print_usage(opts)

    result['command'] = sys.argv[1:]

    return result


def main():
    """Entrypoint"""
    args = parse_args()
    logging.basicConfig(level=args['loglevel'])

    try:
        runner = gitscmd.GitsRunner()
        result = runner.exec(args['command'])
        gitscmd.print_result(result, squeeze_output=not args['all_output'])
    except KeyboardInterrupt:
        print("Aborted.", file=sys.stderr)
    except gitscmd.GitsFileNotFoundError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("Something went wrong:", e, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
