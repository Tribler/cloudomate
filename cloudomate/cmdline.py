import logging
import sys
from argparse import ArgumentParser

from vps.ramnode import RamnodeOptions, RamnodeSpider
from vps.scrapy_hoster import ScrapyHoster

commands = ["options", "purchase", "list"]
providers = {
    "ramnode": ScrapyHoster('ramnode', RamnodeOptions, RamnodeSpider),
}


def execute(argv=None, settings=None):
    logging.disable(logging.DEBUG)
    logging.disable(logging.WARNING)
    logging.disable(logging.INFO)

    parser = ArgumentParser(description="Cloudomate")
    parser.add_argument("command", help="The specified command", nargs='?', choices=commands)
    parser.add_argument("provider", help="The specified provider", nargs='?', choices=providers)
    parser.add_argument("--email", help="email")
    parser.add_argument("--firstName", help="firstName")
    parser.add_argument("--lastName", help="lastName")
    parser.add_argument("--companyName", help="companyName")
    parser.add_argument("--phoneNumber", help="phoneNumber")
    parser.add_argument("--password", help="password")
    parser.add_argument("--address", help="address")
    parser.add_argument("--city", help="city")
    parser.add_argument("--state", help="state")
    parser.add_argument("--countryCode", help="countryCode")
    parser.add_argument("--zipcode", help="zipcode")
    parser.add_argument("--rootPassword", help="rootPassword")
    parser.add_argument("--ns1", help="ns1")
    parser.add_argument("--ns2", help="ns2")
    parser.add_argument("--hostname", help="hostname")

    args = parser.parse_args()
    cmdname = args.command
    provider = args.provider

    if cmdname == "list":
        _list_providers()
        sys.exit(0)

    if not provider or provider not in providers:
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
