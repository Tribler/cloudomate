import logging
import sys
from argparse import ArgumentParser

from cloudomate.util.config import Config
from cloudomate.vps.ramnode import Ramnode

commands = ["options", "purchase", "list"]
providers = {
    "ramnode": Ramnode(),
}


def execute(cmd=sys.argv[1:]):
    logging.disable(logging.DEBUG)
    logging.disable(logging.WARNING)
    logging.disable(logging.INFO)

    parser = ArgumentParser(description="Cloudomate")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_list(subparsers)
    add_parser_options(subparsers)
    add_parser_purchase(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_list(subparsers):
    parser_list = subparsers.add_parser("list", help="List providers")
    parser_list.set_defaults(func=list_providers)


def add_parser_options(subparsers):
    parser_options = subparsers.add_parser("options", help="List provider configurations")
    parser_options.add_argument("provider", help="The specified provider", nargs="?", choices=providers)
    parser_options.set_defaults(func=options)


def add_parser_purchase(subparsers):
    parser_purchase = subparsers.add_parser("purchase", help="Purchase VPS")
    parser_purchase.set_defaults(func=purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers)
    parser_purchase.add_argument("configuration", help="The configuration number (see options)", type=int)
    parser_purchase.add_argument("-f", help="Don't prompt for user confirmation", dest="noconfirm", action="store_true")
    parser_purchase.add_argument("-e", "--email", help="email")
    parser_purchase.add_argument("-fn", "--firstname", help="first name")
    parser_purchase.add_argument("-ln", "--lastname", help="last name")
    parser_purchase.add_argument("-cn", "--companyname", help="company name")
    parser_purchase.add_argument("-pn", "--phone", help="phone number", metavar="phonenumber")
    parser_purchase.add_argument("-pw", "--password", help="password")
    parser_purchase.add_argument("-a", "--address", help="address")
    parser_purchase.add_argument("-c", "--city", help="city")
    parser_purchase.add_argument("-s", "--state", help="state")
    parser_purchase.add_argument("-cc", "--countrycode", help="country code")
    parser_purchase.add_argument("-z", "--zipcode", help="zipcode")
    parser_purchase.add_argument("-rp", "--rootpw", help="root password")
    parser_purchase.add_argument("-ns1", "--ns1", help="ns1")
    parser_purchase.add_argument("-ns2", "--ns2", help="ns2")
    parser_purchase.add_argument("--hostname", help="hostname")


def options(args):
    provider = args.provider
    if not provider or provider not in providers:
        _print_unknown_provider(provider)
        _list_providers()
        sys.exit(2)
    _options(args.provider)


def purchase(args):
    if "provider" not in vars(args):
        sys.exit(2)
    provider = args.provider
    if not provider or provider not in providers:
        _print_unknown_provider(provider)
        _list_providers()
        sys.exit(2)
    config = _get_config(args)
    if not _check_provider(provider, config):
        print("Missing option")
        sys.exit(2)
    _purchase(provider, args.configuration, config)


def _check_provider(provider, config):
    p = providers[provider]
    return config.verify_config(p.required_settings)


def _get_config(args):
    config = Config()
    config.read_config()
    _merge_arguments(config, vars(args))
    return config


def _merge_arguments(config, args):
    for key in args:
        if args[key] is not None:
            config.put(key, args[key])


def _purchase(provider, cid, config):
    p = providers[provider]
    configurations = p.options()
    if not 0 <= cid < len(configurations):
        print('Specified configuration %s is not in range 0-%s' % (cid, len(configurations)))
        sys.exit(1)
    configuration = configurations[cid]
    row_format = "{:15}" * 6
    print("Selected configuration:")
    print(row_format.format("Name", "CPU", "RAM", "Storage", "Bandwidth", "Price"))
    print(row_format.format(configuration["name"], configuration["cpu"], configuration["ram"], configuration["storage"],
                            configuration["bandwidth"], configuration["price"]))
    if config.get("noconfirm") is not None:
        choice = True
    else:
        choice = _confirmation("Are you sure?", default="no")
    if choice:
        _register(provider, configuration)
    else:
        return False


def _confirmation(message, default="y"):
    valid_options = {"yes": True, "ye": True, "y": True, "no": False, "n": False}
    if default in valid_options and valid_options[default] is True:
        prompt = "Y/n"
    elif default in valid_options and valid_options[default] is False:
        prompt = "y/N"
    else:
        prompt = "y/n"

    while True:
        try:
            choice = raw_input("%s (%s) " % (message, prompt)).lower()
        except EOFError:
            sys.exit(2)
        if default is not None and choice == '':
            return valid_options[default]
        elif choice in valid_options:
            return valid_options[choice]
        print("Please respond with y[es] or n[o]")


def list_providers(args):
    _list_providers()


def _print_unknown_provider(provider):
    if provider:
        print("Unknown provider: %s\n" % provider)
    else:
        print("Please specify a provider")


def _list_providers():
    print("Providers:")
    for provider in providers:
        print("  %s     %s" % (provider, providers[provider].website_name))


def _options(provider):
    print("Options for %s:\n" % provider)
    p = providers[provider]
    p.options()
    p.print_configurations()


def _register(provider, configuration):
    print("Register for %s:\n" % provider)
    p = providers[provider]
    p.register(configuration)


if __name__ == '__main__':
    execute()
