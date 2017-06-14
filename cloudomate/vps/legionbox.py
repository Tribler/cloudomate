from cloudomate.vps.clientarea import ClientArea

from cloudomate.gateway import coinbase
from cloudomate.vps.solusvm_hoster import SolusvmHoster


class LegionBox(SolusvmHoster):
    name = "legionbox"
    website = "https://legionbox.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber',
        'password',
        'hostname',
        'rootpw']
    # clientarea_url = 'https://rockhoster.com/cloud/clientarea.php'
    # client_data_url = 'https://rockhoster.com/cloud/modules/servers/solusvmpro/get_client_data.php'
    # gateway = coinbase

    def __init__(self):
        super(LegionBox, self).__init__()

    def start(self):
        hosting_page = self.br.open("https://rockhoster.com/linux.html")
        options = self.parse_options(hosting_page.get_data())
        return options

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_client_data()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_client_data_ip(self.client_data_url)

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        info_dict = clientarea.get_client_data_info_dict(self.client_data_url)
        self._print_info_dict(info_dict)
