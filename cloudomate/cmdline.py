import subprocess
import sys
from argparse import ArgumentParser

from cloudomate.util.config import UserOptions
from cloudomate.vps.blueangelhost import BlueAngelHost
from cloudomate.vps.ccihosting import CCIHosting
from cloudomate.vps.crowncloud import CrownCloud
from cloudomate.vps.legionbox import LegionBox
from cloudomate.vps.linevast import LineVast
from cloudomate.vps.pulseservers import Pulseservers
from cloudomate.vps.rockhoster import RockHoster
from cloudomate.vps.undergroundprivate import UndergroundPrivate
from cloudomate.wallet import Wallet

commands = ["options", "purchase", "list"]
providers = {
    "rockhoster": RockHoster(),
    'pulseservers': Pulseservers(),
    "crowncloud": CrownCloud(),
    "blueangelhost": BlueAngelHost(),
    "ccihosting": CCIHosting(),
    "linevast": LineVast(),
    "underground": UndergroundPrivate(),
    "legionbox": LegionBox(),
}


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Cloudomate")

    subparsers = parser.add_subparsers(dest="command")
    add_parser_list(subparsers)
    add_parser_options(subparsers)
    add_parser_purchase(subparsers)
    add_parser_status(subparsers)
    add_parser_setrootpw(subparsers)
    add_parser_get_ip(subparsers)
    add_parser_ssh(subparsers)
    add_parser_info(subparsers)

    args = parser.parse_args(cmd)
    args.func(args)


def add_parser_list(subparsers):
    parser_list = subparsers.add_parser("list", help="List providers")
    parser_list.set_defaults(func=list_providers)


def add_parser_options(subparsers):
    parser_options = subparsers.add_parser("options", help="List provider configurations")
    parser_options.add_argument("provider", help="The specified provider", choices=providers)
    parser_options.set_defaults(func=options)


def add_parser_purchase(subparsers):
    parser_purchase = subparsers.add_parser("purchase", help="Purchase VPS")
    parser_purchase.set_defaults(func=purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers)
    parser_purchase.add_argument("option", help="The VPS option number (see options)", type=int)
    parser_purchase.add_argument("-c", "--config", help="Set custom config file")
    parser_purchase.add_argument("-f", help="Don't prompt for user confirmation", dest="noconfirm", action="store_true")
    parser_purchase.add_argument("-e", "--email", help="email")
    parser_purchase.add_argument("-fn", "--firstname", help="first name")
    parser_purchase.add_argument("-ln", "--lastname", help="last name")
    parser_purchase.add_argument("-cn", "--companyname", help="company name")
    parser_purchase.add_argument("-pn", "--phonenumber", help="phone number", metavar="phonenumber")
    parser_purchase.add_argument("-pw", "--password", help="password")
    parser_purchase.add_argument("-a", "--address", help="address")
    parser_purchase.add_argument("-ct", "--city", help="city")
    parser_purchase.add_argument("-s", "--state", help="state")
    parser_purchase.add_argument("-cc", "--countrycode", help="country code")
    parser_purchase.add_argument("-z", "--zipcode", help="zipcode")
    parser_purchase.add_argument("-rp", "--rootpw", help="root password")
    parser_purchase.add_argument("-ns1", "--ns1", help="ns1")
    parser_purchase.add_argument("-ns2", "--ns2", help="ns2")
    parser_purchase.add_argument("--hostname", help="hostname")


def add_parser_status(subparsers):
    parser_status = subparsers.add_parser("status", help="Get the status of the services.")
    parser_status.add_argument("provider", help="The specified provider", nargs="?", choices=providers)
    parser_status.add_argument("-e", "--email", help="The login email address")
    parser_status.add_argument("-pw", "--password", help="The login password")
    parser_status.set_defaults(func=status)


def add_parser_get_ip(subparsers):
    parser_get_ip = subparsers.add_parser("getip", help="Get the IP address of the specified service.")
    parser_get_ip.add_argument("provider", help="The specified provider", nargs="?", choices=providers)
    parser_get_ip.add_argument("-n", "--number", help="The number of the service get the IP address for")
    parser_get_ip.add_argument("-e", "--email", help="The login email address")
    parser_get_ip.add_argument("-pw", "--password", help="The login password")
    parser_get_ip.set_defaults(func=get_ip)


def add_parser_ssh(subparsers):
    parser_ssh = subparsers.add_parser("ssh", help="SSH into an active service.")
    parser_ssh.add_argument("provider", help="The specified provider", nargs="?", choices=providers)
    parser_ssh.add_argument("-n", "--number", help="The number of the service to SSH into")
    parser_ssh.add_argument("-e", "--email", help="The login email address")
    parser_ssh.add_argument("-pw", "--password", help="The login password")
    parser_ssh.add_argument("-p", "--rootpw", help="The root password used to login")
    parser_ssh.add_argument("-u", "--user", help="The user password used to login", default="root")
    parser_ssh.set_defaults(func=ssh)


def add_parser_info(subparsers):
    parser_info = subparsers.add_parser("info", help="Get information of the specified service.")
    parser_info.add_argument("provider", help="The specified provider", nargs="?", choices=providers)
    parser_info.add_argument("-n", "--number", help="The number of the service to change the password for")
    parser_info.add_argument("-e", "--email", help="The login email address")
    parser_info.add_argument("-pw", "--password", help="The login password")
    parser_info.set_defaults(func=info)


def add_parser_setrootpw(subparsers):
    parser_setrootpw = subparsers.add_parser("setrootpw", help="Set the root password of the last activated service.")
    parser_setrootpw.add_argument("provider", help="The specified provider", choices=providers)
    parser_setrootpw.add_argument("-n", "--number", help="The number of the service to change the password for")
    parser_setrootpw.add_argument("-e", "--email", help="The login email address")
    parser_setrootpw.add_argument("-pw", "--password", help="The login password")
    parser_setrootpw.add_argument("-p", "--rootpw", help="The new root password", required=True)
    parser_setrootpw.set_defaults(func=set_rootpw)


def set_rootpw(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    provider.set_rootpw(user_settings)


def get_ip(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    ip = provider.get_ip(user_settings)
    print(ip)


def info(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    print("Info for " + provider.name)
    _print_info_dict(provider.info(user_settings))


def status(args):
    provider = _get_provider(args)
    print("Getting status for %s." % provider.name)
    user_settings = _get_user_settings(args, provider.name)
    provider.get_status(user_settings)


def options(args):
    provider = _get_provider(args)
    _options(provider)


def purchase(args):
    if "provider" not in vars(args):
        sys.exit(2)
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    if not _check_provider(provider, user_settings):
        print("Missing option")
        sys.exit(2)
    _purchase(provider, args.option, user_settings)


def _check_provider(provider, config):
    return config.verify_options(provider.required_settings)


def _get_user_settings(args, provider=None):
    user_settings = UserOptions()
    if 'config' in vars(args):
        user_settings.read_settings(filename=args.config, provider=provider)
    else:
        user_settings.read_settings(provider=provider)
    _merge_arguments(user_settings, vars(args))
    return user_settings


def _merge_arguments(config, args):
    for key in args:
        if args[key] is not None:
            config.put(key, args[key])


def _purchase(p, vps_option, user_settings):
    configurations = p.options()
    if not 0 <= vps_option < len(configurations):
        print('Specified configuration %s is not in range 0-%s' % (vps_option, len(configurations)))
        sys.exit(1)
    vps_option = configurations[vps_option]
    row_format = "{:15}" * 6
    print("Selected configuration:")
    print(row_format.format("Name", "CPU", "RAM", "Storage", "Bandwidth", "Est.Price"))
    print(row_format.format(
        vps_option.name,
        str(vps_option.cpu),
        str(vps_option.ram),
        str(vps_option.storage),
        str(vps_option.bandwidth),
        str(vps_option.price)))
    if user_settings.get("noconfirm") is not None and user_settings.get("noconfirm") is True:
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")
    if choice:
        _register(p, vps_option, user_settings)
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


# noinspection PyUnusedLocal
def list_providers(args=None):
    _list_providers()


def _print_unknown_provider(provider):
    if provider:
        print("Unknown provider: %s\n" % provider)
    else:
        print("Please specify a provider")


def _list_providers():
    print("Providers:")
    for provider in providers:
        print("   {:15}{:30}".format(provider, providers[provider].website))


def _options(p):
    print("Options for %s:\n" % p.name)
    p.options()
    p.print_configurations()


def _register(p, vps_option, user_settings):
    # For now use standard wallet implementation through Electrum
    wallet = Wallet()
    p.purchase(user_settings=user_settings, vps_option=vps_option, wallet=wallet)


def _get_provider(args):
    provider = args.provider
    if not provider or provider not in providers:
        _print_unknown_provider(provider)
        _list_providers()
        sys.exit(2)
    return providers[provider]


def ssh(args):
    provider = _get_provider(args)
    user_settings = _get_user_settings(args, provider.name)
    ip = provider.get_ip(user_settings)
    user = user_settings.get('user')
    try:
        subprocess.call(['sshpass', '-p', user_settings.get('rootpw'), 'ssh', '-o', 'StrictHostKeyChecking=no',
                         user + '@' + ip])
    except OSError, e:
        print(e)
        print('Install sshpass to use this command')


def _print_info_dict(info_dict):
    row_format = "{:<25}{:<30}"
    for key in info_dict:
        print(row_format.format(key, info_dict[key]))


if __name__ == '__main__':
    execute()
