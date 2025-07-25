from PIL import Image, ImageDraw
import numpy as np
from util import Util

class BaseUnitInfo:
    BLOCK_X_LIMIT = 30
    BLOCK_Y_LIMIT = 24
    SKIP = 0x40
    FILL = 0x80
    FILL_REPEAT = 0xC0
    
    def compress_unit_data(self, unit_data):
        """壓縮單位數據"""
        MAX_COUNTER = 0x1E
        ret_str = ""
        
        for i in range(0, len(unit_data), MAX_COUNTER * 2):
            block_data = self.get_sub_array(unit_data, i, MAX_COUNTER * 2)
            compressed_block_data = self.compress_block_data(block_data)
            ret_str += compressed_block_data
        
        return Util.conv_hex_string_to_bytes(ret_str)
    
    @staticmethod
    def get_draw_coordinate(offset, x_limit, y_limit):
        """獲取繪製座標"""
        block_x = x_limit // BaseUnitInfo.BLOCK_X_LIMIT
        block_y = y_limit // BaseUnitInfo.BLOCK_Y_LIMIT
        point_count = offset // 2
        
        total_line = point_count // BaseUnitInfo.BLOCK_X_LIMIT
        total_block = total_line // BaseUnitInfo.BLOCK_Y_LIMIT
        x = point_count % BaseUnitInfo.BLOCK_X_LIMIT
        y = total_line % BaseUnitInfo.BLOCK_Y_LIMIT
        
        x += (total_block % block_x) * BaseUnitInfo.BLOCK_X_LIMIT
        y += (total_block // block_x) * BaseUnitInfo.BLOCK_Y_LIMIT
        
        return x, y
    
    def get_draw_data(self, unit_data):
        """獲取繪製數據"""
        ret = bytearray(BaseUnitInfo.BLOCK_X_LIMIT * BaseUnitInfo.BLOCK_Y_LIMIT * 2)
        p = 0
        j = 0
        
        while j < len(unit_data):
            n = (unit_data[j] & 0x1F) + 1
            
            if (unit_data[j] & 0x80) == 0x80:
                if (unit_data[j] & 0x40) == 0x40:
                    # 重複模式
                    while n > 0:
                        self.copy_buffer(unit_data, j + 1, ret, p, 2)
                        p += 2
                        n -= 1
                    j += 2
                else:
                    # 填充模式
                    self.copy_buffer(unit_data, j + 1, ret, p, n * 2)
                    j += n * 2
                    p += n * 2
            else:
                if (unit_data[j] & 0x40) == 0x40:
                    # 跳過模式
                    p += n * 2
                else:
                    # 未使用的情況
                    p += n * 2
            j += 1
        
        return bytes(ret)
    
    def make_bitmap(self, draw_data, x, y, alpha_flag=0, red=0, green=0, blue=0, is_transparent=False):
        """創建位圖"""
        image = Image.new('RGBA', (x, y), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 設定透明色（與C#版本一致）
        transparent_color = None
        if alpha_flag == 0x02:
            transparent_color = (0, 0, 0)  # 黑色
        elif alpha_flag == 0x07:
            transparent_color = (255, 255, 255)  # 白色
        
        p = 0
        while p < len(draw_data):
            color = Util.get_le_int16(draw_data, p)
            
            # 提取RGB分量 (RGB555)
            r = (color & 0x7C00) >> 7
            g = (color & 0x03E0) >> 2
            b = (color & 0x001F) << 3
            
            # 獲取座標
            i, j = self.get_draw_coordinate(p, x, y)
            
            # 處理透明度（與C#版本一致）
            if alpha_flag == 0x00:
                alpha = 255
            elif alpha_flag == 0x01:
                alpha = 128
            elif alpha_flag == 0x02:
                alpha = 255
            elif alpha_flag == 0x07:
                alpha = 255
            else:
                alpha = 255
            
            # 繪製像素
            draw.point((i, j), fill=(r, g, b, alpha))
            p += 2
        
        # 處理透明色（與C#版本一致）
        if is_transparent and transparent_color:
            pixels = image.load()
            if pixels is not None:
                for y in range(image.height):
                    for x in range(image.width):
                        r, g, b, a = pixels[x, y]
                        # 將指定的透明色變為透明
                        if (r, g, b) == transparent_color:
                            pixels[x, y] = (r, g, b, 0)
        
        return image
    
    def get_sub_array(self, in_buff, start, length):
        """獲取子陣列"""
        return in_buff[start:start+length]
    
    def copy_buffer(self, in_buff, in_offset, out_buff, out_offset, length):
        """複製緩衝區"""
        out_buff[out_offset:out_offset+length] = in_buff[in_offset:in_offset+length]
    
    def make_skip_pattern(self, unit_data, pixel_offset, pixel_len):
        """創建跳過模式"""
        if pixel_len == 0:
            return ""
        
        head = BaseUnitInfo.SKIP | (pixel_len - 1)
        return f"{head:02x}"
    
    def make_fill_repeat_pattern(self, unit_data, pixel_offset, pixel_len):
        """創建重複填充模式"""
        if pixel_len == 0:
            return ""
        
        head = BaseUnitInfo.FILL_REPEAT | (pixel_len - 1)
        pattern = ""
        
        for i in range(pixel_len):
            color = Util.get_le_int16(unit_data, pixel_offset + i * 2)
            pattern += f"{color:04x}"
        
        return f"{head:02x}{pattern}"
    
    def make_fill_pattern(self, unit_data, pixel_offset, pixel_len):
        """創建填充模式"""
        if pixel_len == 0:
            return ""
        
        head = BaseUnitInfo.FILL | (pixel_len - 1)
        pattern = ""
        
        for i in range(pixel_len):
            color = Util.get_le_int16(unit_data, pixel_offset + i * 2)
            pattern += f"{color:04x}"
        
        return f"{head:02x}{pattern}"
    
    def compress_block_data(self, block_data):
        """壓縮區塊數據"""
        if len(block_data) == 0:
            return ""
        
        ret = ""
        i = 0
        
        while i < len(block_data):
            # 尋找重複模式
            repeat_count = 1
            while (i + repeat_count * 2 < len(block_data) and 
                   repeat_count < 0x1F and
                   block_data[i:i+2] == block_data[i+repeat_count*2:i+repeat_count*2+2]):
                repeat_count += 1
            
            if repeat_count > 1:
                ret += self.make_fill_repeat_pattern(block_data, i, repeat_count)
                i += repeat_count * 2
                continue
            
            # 尋找填充模式
            fill_count = 1
            while (i + fill_count * 2 < len(block_data) and 
                   fill_count < 0x1F and
                   block_data[i:i+2] != block_data[i+fill_count*2:i+fill_count*2+2]):
                fill_count += 1
            
            if fill_count > 1:
                ret += self.make_fill_pattern(block_data, i, fill_count)
                i += fill_count * 2
                continue
            
            # 單個像素
            ret += f"{block_data[i]:02x}{block_data[i+1]:02x}"
            i += 2
        
        return ret 