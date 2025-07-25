import struct

class Util:
    @staticmethod
    def get_be_int32(array, offset):
        """從位元組陣列中讀取大端序32位整數"""
        return struct.unpack('>I', array[offset:offset+4])[0]
    
    @staticmethod
    def get_be_int16(array, offset):
        """從位元組陣列中讀取大端序16位整數"""
        val = struct.unpack('>H', array[offset:offset+2])[0]
        if val >= 0x8000:
            val -= 0x10000
        return val
    
    @staticmethod
    def get_be_uint16(array, offset):
        """從位元組陣列中讀取大端序16位無符號整數"""
        return struct.unpack('>H', array[offset:offset+2])[0]
    
    @staticmethod
    def set_be_uint16(array, offset, data):
        """在位元組陣列中設置大端序16位無符號整數"""
        struct.pack_into('>H', array, offset, data)
    
    @staticmethod
    def set_be_uint32(array, offset, data):
        """在位元組陣列中設置大端序32位無符號整數"""
        struct.pack_into('>I', array, offset, data)
    
    @staticmethod
    def get_le_int32(array, offset):
        """從位元組陣列中讀取小端序32位整數（低位在前，高位在後）"""
        return array[offset] + (array[offset+1] << 8) + (array[offset+2] << 16) + (array[offset+3] << 24)
    
    @staticmethod
    def get_le_int16(array, offset):
        """從位元組陣列中讀取小端序16位整數（低位在前，高位在後）"""
        val = array[offset] + (array[offset+1] << 8)
        if val >= 0x8000:
            val -= 0x10000
        return val
    
    @staticmethod
    def get_le_uint16(array, offset):
        """從位元組陣列中讀取小端序16位無符號整數（低位在前，高位在後）"""
        return array[offset] + (array[offset+1] << 8)
    
    @staticmethod
    def set_le_uint16(array, offset, data):
        """在位元組陣列中設置小端序16位無符號整數（低位在前，高位在後）"""
        array[offset] = data & 0xFF
        array[offset + 1] = (data >> 8) & 0xFF
    
    @staticmethod
    def set_le_uint32(array, offset, data):
        """在位元組陣列中設置小端序32位無符號整數（低位在前，高位在後）"""
        array[offset] = data & 0xFF
        array[offset + 1] = (data >> 8) & 0xFF
        array[offset + 2] = (data >> 16) & 0xFF
        array[offset + 3] = (data >> 24) & 0xFF
    
    @staticmethod
    def conv_hex_string_to_bytes(hex_str):
        """將十六進制字串轉換為位元組陣列"""
        return bytes.fromhex(hex_str.replace(' ', ''))
    
    @staticmethod
    def conv_bytes_to_hex_string(bytes_data, offset, length):
        """將位元組陣列轉換為十六進制字串"""
        return ' '.join(f'{b:02x}' for b in bytes_data[offset:offset+length]) 