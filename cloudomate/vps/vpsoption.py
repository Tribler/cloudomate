class VpsOption(object):
    def __init__(self,
                 name=None,
                 price=None,
                 cpu=None,
                 ram=None,
                 storage=None,
                 bandwidth=None,
                 connection=None,
                 purchase_url=None):
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.storage = storage
        self.bandwidth = bandwidth
        self.connection = connection
        self.price = price
        self.purchase_url = purchase_url
