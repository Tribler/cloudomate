class VpsOption(object):

    def __init__(self,
                 name,
                 price,
                 currency,
                 cpu,
                 ram,
                 storage,
                 bandwidth,
                 connection,
                 purchase_url):
        self.name = name
        self.ram = ram
        self.cpu = cpu
        self.storage = storage
        self.bandwidth = bandwidth
        self.connection = connection
        self.price = price
        self.currency = currency
        self.purchase_url = purchase_url
