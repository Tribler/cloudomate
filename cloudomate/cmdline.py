from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import subprocess
import sys
from argparse import ArgumentParser
from builtins import dict
from builtins import input
from builtins import round
from builtins import str
from os import path

from CaseInsensitiveDict import CaseInsensitiveDict
from future import standard_library

from cloudomate import wallet as wallet_util
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.hoster.vps.twosync import TwoSync
from cloudomate.hoster.vps.proxhost import ProxHost
from cloudomate.util.fakeuserscraper import UserScraper
from cloudomate.util.settings import Settings
from cloudomate.wallet import Wallet

from cloudomate import globals

standard_library.install_aliases()


def _map_providers_to_dict(provider_list):
    return CaseInsensitiveDict(dict((provider.get_metadata()[0], provider) for provider in provider_list))


types = ["vps", "vpn"]


"""
All implemented providers, those commented out are not working for now. CCIHosting's and 
Pulseserver's gateway changed to CoinPayments and this is not implemented. CrownCloud 
manually checks orders and do not accept multiple variations of the same email. 
"""
providers = CaseInsensitiveDict({
    "vps": _map_providers_to_dict([
        BlueAngelHost,
        # CCIHosting,
        # CrownCloud,
        LineVast,
        # Pulseservers,
        UndergroundPrivate,
        TwoSync,
        ProxHost
    ]),
    "vpn": _map_providers_to_dict([
        AzireVpn,
    ])
})


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Cloudomate")
    parser.add_argument('--version', action='version', version='%(prog)s '+globals.__version__)

    subparsers = parser.add_subparsers(dest="type")

    add_vps_parsers(subparsers)
    add_vpn_parsers(subparsers)
    subparsers.required = True

    args = parser.parse_args(cmd)
    args.func(args)

def add_vpn_parsers(subparsers):
    vpn_parsers = subparsers.add_parser("vpn")
    vpn_parsers.set_defaults(type="vpn")
    vpn_subparsers = vpn_parsers.add_subparsers(dest="command")
    vpn_subparsers.required = True

    add_parser_list(vpn_subparsers, "vpn")
    add_parser_options(vpn_subparsers, "vpn")
    add_parser_purchase(vpn_subparsers, "vpn")
    add_parser_status(vpn_subparsers, "vpn")
    add_parser_info(vpn_subparsers, "vpn")


def add_vps_parsers(subparsers):
    vps_parsers = subparsers.add_parser("vps")
    vps_parsers.set_defaults(type="vps")
    vps_subparsers = vps_parsers.add_subparsers(dest="command")
    vps_subparsers.required = True

    add_parser_list(vps_subparsers, "vps")
    add_parser_options(vps_subparsers, "vps")
    add_parser_purchase(vps_subparsers, "vps")
    add_parser_status(vps_subparsers, "vps")
    add_parser_vps_setrootpw(vps_subparsers)
    add_parser_vps_get_ip(vps_subparsers)
    add_parser_vps_ssh(vps_subparsers)
    add_parser_info(vps_subparsers, "vps")


def add_parser_list(subparsers, provider_type):
    parser_list = subparsers.add_parser("list", help="List %s providers" % provider_type.upper())
    parser_list.set_defaults(func=list_providers)


def add_parser_options(subparsers, provider_type):
    parser_options = subparsers.add_parser("options", help="List %s provider configurations" % provider_type.upper())
    parser_options.add_argument("provider", help="The specified %s provider" % provider_type.upper(),
                                choices=providers[provider_type])
    parser_options.set_defaults(func=options)


def add_parser_purchase(subparsers, provider_type):
    parser_purchase = subparsers.add_parser("purchase", help="Purchase %s" % provider_type.upper())
    parser_purchase.set_defaults(func=purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers[provider_type])

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
    parser_purchase.add_argument("--randomuser", action="store_true", help="Use random user info")
    parser_purchase.add_argument("--testnet", action="store_true", help="Use Electrum's testnet bitcoins (for testing)")

    if provider_type == 'vps':
        parser_purchase.add_argument("option", help="The %s option number (see options)" % provider_type.upper(),
                                     type=int)
        parser_purchase.add_argument("-rp", "--rootpw", help="root password")
        parser_purchase.add_argument("-ns1", "--ns1", help="ns1")
        parser_purchase.add_argument("-ns2", "--ns2", help="ns2")
        parser_purchase.add_argument("--hostname", help="hostname")


def add_parser_status(subparsers, provider_type):
    parser_status = subparsers.add_parser("status", help="Get the status of the %s services" % provider_type.upper())
    parser_status.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_status.add_argument("-e", "--email", help="The login email address")
    parser_status.add_argument("-pw", "--password", help="The login password")
    parser_status.set_defaults(func=status)


def add_parser_vps_get_ip(subparsers):
    parser_get_ip = subparsers.add_parser("getip", help="Get the IP address of the specified service")
    parser_get_ip.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_get_ip.add_argument("-n", "--number", help="The number of the service get the IP address for")
    parser_get_ip.add_argument("-e", "--email", help="The login email address")
    parser_get_ip.add_argument("-pw", "--password", help="The login password")
    parser_get_ip.set_defaults(func=print_ip)


def add_parser_vps_ssh(subparsers):
    parser_ssh = subparsers.add_parser("ssh", help="SSH into an active service")
    parser_ssh.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_ssh.add_argument("-n", "--number", help="The number of the service to SSH into")
    parser_ssh.add_argument("-e", "--email", help="The login email address")
    parser_ssh.add_argument("-pw", "--password", help="The login password")
    parser_ssh.add_argument("-p", "--rootpw", help="The root password used to login")
    parser_ssh.add_argument("-u", "--user", help="The user password used to login", default="root")
    parser_ssh.set_defaults(func=ssh)


def add_parser_info(subparsers, provider_type):
    parser_info = subparsers.add_parser("info",
                                        help="Get information of the specified %s service" % provider_type.upper())
    parser_info.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_info.add_argument("-n", "--number",
                             help="The number of the %s service to get the info of" % provider_type.upper())
    parser_info.add_argument("-e", "--email", help="The login email address")
    parser_info.add_argument("-pw", "--password", help="The login password")

    if provider_type == "vpn":
        parser_info.add_argument("-o", "--ovpn", help="Save the ovpn file to the specified location")

    parser_info.set_defaults(func=info)


def add_parser_vps_setrootpw(subparsers):
    parser_setrootpw = subparsers.add_parser("setrootpw", help="Set the root password of the last activated service")
    parser_setrootpw.add_argument("provider", help="The specified provider", choices=providers['vps'])
    parser_setrootpw.add_argument("root_password", help="The new root password")
    parser_setrootpw.add_argument("-n", "--number", help="The number of the VPS service to change the password for")
    parser_setrootpw.add_argument("-e", "--email", help="The login email address")
    parser_setrootpw.add_argument("-pw", "--password", help="The login password")
    parser_setrootpw.set_defaults(func=change_root_password_ssh)


def print_ip(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    provider_instance = provider(user_settings)
    configuration = provider_instance.get_configuration()
    print(configuration.ip)


def info(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    config = provider(user_settings).get_configuration()

    if args.type == "vps":
        print(("Info for " + name))
        _print_info_vps(config)
    elif args.type == "vpn":
        if args.ovpn:
            _save_info_vpn(config, args.ovpn)
        else:
            print(("Info for " + name))
            _print_info_vpn(config)


def status(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    print(("Getting status for %s." % name))
    user_settings = _get_user_settings(args, name)
    p = provider(user_settings)
    s = p.get_status()

    if args.type == "vps":
        # If we don't currently support usage statistics for this provider
        if s.memory.used == -1.0:
            row = "{:20}" * 2
            print(row.format("Online", "Expiration"))
            print(row.format(str(s.online), s.expiration.isoformat()))
        else:
            row = "{:20}" * 5
            print(row.format("Memory used (GB)", "Storage used (GB)", "Bandwidth used (GB)", "Online", "Expiration"))
            print(row.format(
                '{:.2f}/{:.2f}'.format(s.memory.used, s.memory.total),
                '{:.2f}/{:.2f}'.format(s.storage.used, s.storage.total),
                '{:.2f}/{:.2f}'.format(s.bandwidth.used, s.bandwidth.total),
                str(s.online),
                s.expiration.isoformat()
            ))
    elif args.type == "vpn":
        row = "{:18}" * 2
        print(row.format("Online", "Expiration"))
        print(row.format(str(s.online), s.expiration.isoformat()))


def options(args):
    provider = _get_provider(args)

    if args.type == "vps":
        _options_vps(provider)
    elif args.type == "vpn":
        _options_vpn(provider)


def purchase(args):
    if "provider" not in vars(args):
        sys.exit(2)
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    if args.randomuser:
        _merge_random_user_data(user_settings)

        if args.testnet or os.getenv('TESTNET', '0') == '1':
            user_settings.put('user', 'testnet', '1')
            os.environ['TESTNET'] = '1'
            print('testnet on')
        else:
            user_settings.put('user', 'testnet', '0')
            os.environ['TESTNET'] = '0'
            print('testnet off')
        user_settings.save_settings()
        print('Random user settings used: ' + user_settings.get_default_config_location())

    if not _check_provider(provider, user_settings):
        print("Missing option")
        sys.exit(2)

    if args.type == 'vps':
        _purchase_vps(provider, user_settings, args)
    else:
        _purchase_vpn(provider, user_settings, args)


def _check_provider(provider, config):
    return config.verify_options(provider.get_required_settings())


def _merge_random_user_data(user_settings):
    usergenerator = UserScraper()
    randomuser = usergenerator.get_user()
    for section in randomuser.keys():
        for key in randomuser[section].keys():
            user_settings.put(section, key, randomuser[section][key])


def _get_user_settings(args, provider=None):
    user_settings = Settings()
    if 'config' in vars(args):
        user_settings.read_settings(filename=args.config)
    else:
        user_settings.read_settings()
    _merge_arguments(user_settings, provider, vars(args))

    # Set global testnet variable according to configuration
    if user_settings.has_key('user', 'testnet') and user_settings.get('user', 'testnet') == '1':
        os.environ['TESTNET'] = '1'
    else:
        os.environ['TESTNET'] = '0'
    return user_settings


def _merge_arguments(config, provider, args):
    for key in args:
        if args[key] is not None:
            config.put(provider, key, args[key])


def _purchase_vps(provider, user_settings, args):
    vps_option = args.option
    configurations = provider.get_options()
    if not 0 <= vps_option < len(configurations):
        print(('Specified configuration %s is not in range 0-%s' % (vps_option, len(configurations))))
        sys.exit(1)
    vps_option = configurations[vps_option]
    row_format = "{:15}" * 6
    print("Selected configuration:")
    print((row_format.format("Name", "CPU", "RAM", "Storage", "Bandwidth", "Price (USD)")))
    bandwidth = "Unlimited" if vps_option.bandwidth == sys.maxsize else vps_option.bandwidth
    print((row_format.format(
        vps_option.name,
        str(vps_option.cores),
        str(vps_option.memory),
        str(vps_option.storage),
        str(bandwidth),
        str(vps_option.price))))

    if args.noconfirm or (
            user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")
    if choice:
        _register(provider, vps_option, user_settings)
    else:
        return False


def _purchase_vpn(provider, user_settings, args):
    print("Selected configuration:")
    options = provider.get_options()
    option = options[0]

    row = "{:18}" * 5
    print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Price (USD)"))
    bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)
    speed = "Unlimited" if option.speed == sys.maxsize else option.speed
    print(row.format(option.name, option.protocol, bandwidth, speed, str(option.price)))

    if args.noconfirm or (
            user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")

    if choice:
        _register(provider, options[0], user_settings)
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
            choice = input("%s (%s) " % (message, prompt)).lower()
        except EOFError:
            sys.exit(2)
        if default is not None and choice == '':
            return valid_options[default]
        elif choice in valid_options:
            return valid_options[choice]
        print("Please respond with y[es] or n[o]")


def list_providers(args):
    _list_providers(args.type)


def _print_unknown_provider(provider):
    if provider:
        print(("Unknown provider: %s\n" % provider))
    else:
        print("Please specify a provider")


def _print_unknown_provider_type(provider_type):
    if provider_type:
        print(("Unknown provider type: %s\n" % provider_type))
    else:
        print("Please specify a provider type")


def _list_providers(provider_type):
    print("Providers:")
    for provider in providers[provider_type].values():
        name, website = provider.get_metadata()
        print("   {:15}{:30}".format(name, website))


def _list_provider_types():
    print("Provider Types:")
    for provider_type in types:
        print(("   {:15}".format(provider_type)))


def _options_vps(p):
    name, _ = p.get_metadata()
    print(("Options for %s:\n" % name))
    options = p.get_options()

    # Print heading
    row = "{:<5}" + "{:20}" * 8
    print(row.format("#", "Name", "Cores", "Memory (GB)", "Storage (GB)", "Bandwidth", "Connection (Gbit/s)",
                     "Est. Price (mBTC)", "Price (USD)"))

    for i, option in enumerate(options):
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        gateway = p.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        print(row.format(i, option.name, str(option.cores), str(option.memory), str(option.storage), bandwidth,
                         str(option.connection), str(estimate), str(option.price)))


def _options_vpn(provider):
    name, _ = provider.get_metadata()
    print(("Options for %s:\n" % name))
    options = provider.get_options()

    # Print heading
    row = "{:18}" * 6
    print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Est. Price (mBTC)", "Price (USD)"))

    for option in options:
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)
        speed = "Unlimited" if option.speed == sys.maxsize else option.speed

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        gateway = provider.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        print(row.format(option.name, option.protocol, bandwidth, speed, str(estimate), str(option.price)))


def _register(provider, vps_option, settings):
    # For now use standard wallet implementation through Electrum
    # If wallet path is defined in config, use that.
    testnet = os.getenv('TESTNET', '0') == '1'

    if settings.has_key('client', 'walletpath'):
        wallet = Wallet(wallet_path=settings.get('client', 'walletpath'), testnet=testnet)
    else:
        wallet = Wallet(testnet=testnet)

    provider_instance = provider(settings)
    provider_instance.purchase(wallet, vps_option)


def _get_provider(args):
    provider_type = args.type
    provider = args.provider
    if not provider_type or provider_type not in providers:
        _print_unknown_provider_type(provider_type)
        _list_provider_types()
        sys.exit(2)

    if not provider or provider not in providers[provider_type]:
        _print_unknown_provider(provider)
        _list_providers(provider_type)
        sys.exit(2)
    return providers[provider_type][provider]


def ssh(args, command=None):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)
    config = provider(user_settings).get_configuration()
    commandline = ['sshpass', '-p', config.root_password, 'ssh', '-o', 'StrictHostKeyChecking=no',
                   'root@' + config.ip]

    if command:
        commandline.append(command)

    try:
        subprocess.call(commandline)
        return True
    except OSError as e:
        print(e)
        print('Install sshpass to use this command')
        return False


def change_root_password_ssh(args):
    if ssh(args, 'echo "root:' + args.root_password + '" | chpasswd'):
        provider = _get_provider(args)
        name, _ = provider.get_metadata()
        user_settings = _get_user_settings(args, name)
        user_settings.put("server", "root_password", args.root_password)
        user_settings.save_settings()
        print("Successfully set new root password in the config")
    else:
        print("Failed to set the new root password")
        sys.exit(2)


def _print_info_vps(info):
    row = "{:18}" * 2
    print(row.format("IP address", "Root password"))
    print(row.format(str(info.ip), str(info.root_password)))


def _print_info_vpn(provider_info):
    credentials = "credentials.conf"
    header = "=" * 20

    ovpn = provider_info.ovpn
    ovpn += "\nauth-user-pass " + credentials

    print("\ncredentials.conf")
    print(header)
    print(provider_info.username)
    print(provider_info.password)
    print("\nsettings.ovpn")
    print(header)
    print(ovpn)
    print(header)


def _save_info_vpn(info, ovpn):
    if not ovpn.endswith('.ovpn'):
        ovpn = ovpn + '.ovpn'

    ovpn = path.normcase(path.normpath(path.join(os.getcwd(), ovpn)))
    dir, _ = path.split(ovpn)
    credentials = 'credentials.conf'

    with io.open(ovpn, 'w', encoding='utf-8') as ovpn_file:
        ovpn_file.write(info.ovpn + '\nauth-user-pass ' + credentials)

    with io.open(path.join(dir, credentials), 'w', encoding='utf-8') as credentials_file:
        credentials_file.writelines([info.username + '\n', info.password])

    print("Saved VPN configuration to " + ovpn)


if __name__ == '__main__':
    execute()
