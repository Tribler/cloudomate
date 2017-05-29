import unittest
import parameterized

from cloudomate.gateway import coinbase, bitpay

gateways = [
    (bitpay.extract_info, ),
    (coinbase.extract_info, ),
]




class TestHosters(unittest.TestCase):
    #@parameterized.expand(gateways)
    #def testHosterImplementsInterface(self, hoster):
    #    self.assertTrue('options' in dir(hoster), msg='options is not implemented in {0}'.format(hoster.name))
    #    self.assertTrue('purchase' in dir(hoster), msg='purchase is not implemented in {0}'.format(hoster.name))

    @parameterized.expand(gateways)
    def testWrongURL(self):
        '''
        
        :return: 
        '''

    def testAmountFormatting(self):
        '''
        
        :return: 
        '''

    def testAddressFormatting(self):
        '''
        
        :return: 
        '''