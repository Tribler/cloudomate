class VPSOutOfStockException(Exception):
    """Exception raised when trying to purchase a VPS that is out of stock."""
    def __init__(self, vps_option, msg=None):
        if msg is None:
            msg = "VPS Option '{}' is out of stock".format(vps_option.name)
        super(Exception, self).__init__(msg)
        self.vps_option = vps_option

