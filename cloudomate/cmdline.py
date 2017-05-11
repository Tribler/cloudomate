import logging
import sys


import util.config
from vps.scrapy_hoster import ScrapyHoster
from vps.ramnode import RamnodeOptions, RamnodeSpider

commands = ["options", "purchase", "list"]
providers = {
    "ramnode": ScrapyHoster('ramnode', RamnodeOptions, RamnodeSpider),
}


def execute(argv=None, settings=None):
    logging.disable(logging.DEBUG)
    logging.disable(logging.WARNING)
    logging.disable(logging.INFO)
    if argv is None:
        argv = sys.argv
    if settings is None:
        settings = util.config.read_config()

    provider = None
    cmdname = None

    c = _pop_command_names(argv)
    if len(c) >= 1:
        cmdname = c[0]
    if len(c) >= 2:
        provider = c[1]
    if not cmdname:
        _print_commands()
        sys.exit(0)

    if cmdname not in commands:
        _print_unknown_command(cmdname)
        sys.exit(2)

    if cmdname == "list":
        _list_providers()
        sys.exit(0)

    if not provider or not provider in providers:
        _print_unknown_provider(commands, provider)
        sys.exit(2)

    if cmdname == "options":
        _options(provider)


def _print_unknown_provider(command, provider):
    _print_header()
    if provider:
        print("Unknown provider: %s\n" % provider)
    else:
        print("Please specify a provider")


def _list_providers():
    _print_header()
    print("Providers:")
    for provider in providers:
        print("  " + provider)


def _options(provider):
    _print_header()
    print("Options for %s:\n" % provider)
    p = providers[provider]
    p.options()
    print(p.get_configurations())

def _print_unknown_command(command):
    _print_header()
    print("Unknown command: %s\n" % command)
    print('Use "cloudomate" to see available commands')


def _print_commands():
    _print_header()
    print("Usage:")
    print("  cloudomate list")
    print("  cloudomate <command> <provider> [options] [args]\n")
    print("Available commands:")
    print("  purchase       Purchase a specified VPS")
    print("  options        List options")
    print("  list           List providers")


def _print_header():
    print("Cloudomate\n")


def _pop_command_names(argv):
    c = []
    i = 0
    for arg in argv[1:]:
        if not arg.startswith('-'):
            del argv[i]
            c.append(arg)
        i += 1
    return c


if __name__ == '__main__':
    execute()
