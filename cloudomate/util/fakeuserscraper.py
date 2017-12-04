from mechanicalsoup import StatefulBrowser


class UserScraper:
    """
    Scrapes fakeadressgenerator.com for fake user data,
    """

    attributes = [
        'Full Name',
        'Street',
        'City',
        'State Full',
        'Zip Code',
        'Phone Number',
    ]

    pages = {
        'NL': 'http://www.fakeaddressgenerator.com/World/Netherlands_address_generator',
        'US': 'http://www.fakeaddressgenerator.com/World/us_address_generator',
        'UK': 'http://www.fakeaddressgenerator.com/World/uk_address_generator',
        'CA': 'http://www.fakeaddressgenerator.com/World/ca_address_generator',
    }

    def __init__(self, country='NL'):
        self.br = StatefulBrowser()
        self.page = UserScraper.pages.get(country)


    def get_user(self):
        self.br.open(self.page)
        attrs = {}

        for attr in self.attributes:
            attrs[attr] = self._get_attribute(attr)

        return self._map_to_config(attrs)

    def _map_to_config(self, attrs):
        config = {}
        # Treat full name separately because it needs to be split
        if 'Full Name' in attrs:
            config['firstname'] = attrs['Full Name'].split('\xa0')[0]
            config['lastname'] = attrs['Full Name'].split('\xa0')[-1]

        # Map the possible user attributes to their config names
        mapping = {
            'Street': 'address',
            'City': 'city',
            'State Full': 'state',
            'Zip Code': 'zipcode',
            'Phone Number': 'phonenumber',
            'Company': 'companyname',
        }

        for attr in attrs.keys():
            if attr in mapping.keys():
                config[mapping[attr]] = attrs[attr]
        return config


    def _get_attribute(self, attribute):
        return self.br.get_current_page()\
            .find(string=attribute)\
            .parent.parent.parent\
            .find('input')\
            .get('value')