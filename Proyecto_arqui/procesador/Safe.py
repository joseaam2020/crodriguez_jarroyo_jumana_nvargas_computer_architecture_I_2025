class Safe:
    def __init__(self):
        self.keys = [[[0,0],[0,0]],[[0,0],[0,0]],[[0,0],[0,0]],[[0,0],[0,0]]]

    def store_key(self, key_index, reg_r1, reg_r2, reg_r3, reg_r4):
        new_index = key_index % 4
        key_low = [reg_r1, reg_r2]
        key_high = [reg_r3, reg_r4]
        key_data = [key_low, key_high]
        self.keys[new_index] = key_data

    def load_key(self,index):
        key_index = (index % 8) // 2
        high_low_index = index % 2
        return self.keys[key_index][high_low_index]
    

testSafe = Safe()
testSafe.store_key(0,1,2,3,4)
#print(testSafe.load_key(1))
#print(testSafe.keys)