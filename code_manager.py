# code_manager.py

class CodeManager:
    def __init__(self):
        # Initialize the list of codes here
        # self.available_codes = []
        self.available_codes = ['LMTMYH2IZ36', 'LMTMYO9NKUK', 'LMTMYTLIN0I', 'LMTMYFPN9V1', 'LMTMY25MGLY', 'LMTMYYPELZJ', 
                                  'LMTMYWBGDHN', 'LMTMYS8Z61F', 'LMTMYHRKZTW', 'LMTMYJMXNXS', 'LMTMY6IK3WK', 'LMTMY34Q1IE', 
                                  'LMTMYNWRG89', 'LMTMYONEBY5', 'LMTMYLQOFLB', 'LMTMYH206MD', 'LMTMY3GYW2P', 'LMTMY64K4S4', 'LMTMYS00RS6', 'LMTMYU2HNMX', 
                                  'LMTMY1D0BM1', 'LMTMY8IOS3B', 'LMTMYPLG8PZ', 'LMTMYZU62C7', 'LMTMY9A8F7N', 'LMTMYY38G7P', 'LMTMYS58R7L', 'LMTMYBEKT5U', 
                                  'LMTMYZFKIWS', 'LMTMYX0V0NE', 'LMTMYWST3V9', 'LMTMYAK59WV', 'LMTMYOY8957', 'LMTMY7ZX2LU', 'LMTMYGJC99V', 'LMTMYTS0B67', 
                                  'LMTMYBLPY9A', 'LMTMYEPEIMT', 'LMTMYHGOHC1', 'LMTMYOW6U2W', 'LMTMY8NWBL5', 'LMTMYFIGDGY', 'LMTMYKIZ08F', 'LMTMYRV0200', 
                                  'LMTMYFRCOBB', 'LMTMYKR58JF', 'LMTMYYD9HDW', 'LMTMYUBCDV2', 'LMTMY05NKIW', 'LMTMYZDK8AY']
        self.used_codes = []

    def add_used_code(self, code):
        self.used_codes.append(code)

    def is_code_used(self, code):
        return code in self.used_codes

    def is_empty(self):
        return not bool(self.available_codes)

    def get_available_code(self):
        if not self.is_empty():
            return self.available_codes[0]
        else:
            return None

    def remove_available_code(self, code):
        if code in self.available_codes:
            self.available_codes.remove(code)
