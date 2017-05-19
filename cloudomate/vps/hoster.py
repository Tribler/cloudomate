"""
Hoster provides abstract implementations for common functionality
At this time there is no abstract implementation for any functionality.
"""


class Hoster(object):
    name = None
    website = None
    required_settings = None
    configurations = None

    def options(self):
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, user_settings, vps_option):
        raise NotImplementedError('Abstract method implementation')

    def print_configurations(self):
        """
        Print parsed VPS configurations.
        """
        row_format = "{:<5}" + "{:15}" * 7
        print(row_format.format("#", "Name", "CPU", "RAM", "Storage", "Bandwidth", "Connection", "Price"))

        i = 0
        for item in self.configurations:
            print(row_format.format(i, item.name, item.cpu, item.ram, item.storage, item.bandwidth,
                                    item.connection, item.price))
            i = i + 1

    @staticmethod
    def _print_row(i, item, item_names):
        row_format = "{:<5}" + "{:15}" * len(item_names)
        values = [i]
        for key in item_names.keys():
            if key in item:
                values.append(item[key])
            else:
                values.append("")
        print(row_format.format(*values))

    def _create_browser(self):
        br = Browser()
        br.set_handle_robots(False)
        br.addheaders = [('User-agent', 'Chromium')]
        return br
