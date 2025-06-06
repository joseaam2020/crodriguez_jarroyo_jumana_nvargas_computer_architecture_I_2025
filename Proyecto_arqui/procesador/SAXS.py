from Safe import Safe

class SAXS:
    def __init__(self,safe : Safe):
        self.safe = safe

    def saxs_operation(self, reg_r1_value, key_index):
        
        key = self.safe.load_key(key_index)
        key_low = key[0]
        key_high = key[1]
        
        left_shifted = (reg_r1_value << 4) & 0xFFFFFFFF
        left_part = (left_shifted + key_low) & 0xFFFFFFFF
        
        right_shifted = reg_r1_value >> 5
        right_part = (right_shifted + key_high) & 0xFFFFFFFF
        
        result = left_part ^ right_part
        return result        
