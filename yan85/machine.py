from .utils import *

class Machine:
    #machine virtual memory
    vmem = []
    #defaults
    conf = {
        'vmem_bytes': 0,
        'code_base_address': 0x0,
        'registers_base_address': 0x400,
        'A_address': 0x0,
        'B_address': 0x1,
        'C_address': 0x2,
        'D_address': 0x3,
        's_address': 0x4,
        'i_address': 0x5, #instructions counter
        'f_address': 0x6,
        #                  40
        #                  |20
        #                  ||10
        #                  |||8421 
        'register_order': 'ABCDsif',
        }

    def __init__(self, 
                 vmem_bytes=conf['vmem_bytes'],
                 code_base_address=conf['code_base_address'],
                 registers_base_address=conf['registers_base_address'],
                 register_order=conf['register_order']
                 ):
        self.conf['vmem_bytes'] = vmem_bytes
        self.conf['code_base_address'] = code_base_address
        self.conf['registers_base_address'] = registers_base_address
        self.conf['register_order'] = register_order
        #initialize the virtual memory
        self.vmem = [0] * self.conf['vmem_bytes']


    def load_code(self, code_dump: str):
        """
        load yan code into memory, from a hexdump string.
        The code is loaded at offset conf.code_base_address
        The code must be a string containing hex in the format:
            'hh hh hh hh hh hh hh ...'
        """
        code_bytes = []
        dump_to_code_bytes(code_dump, code_bytes)
        virtual_mmap(self.vmem, code_bytes, self.conf['code_base_address'])

