import os
from datetime import datetime
from PIL import Image
from base_unit_info import BaseUnitInfo
from util import Util

class UnitData:
    """單位數據"""
    def __init__(self):
        self.data = b''

class FB2Info(BaseUnitInfo):
    """FB2檔案信息類"""
    
    def __init__(self, file_name):
        super().__init__()
        self.fb2_file = file_name
        self.mpl_file = os.path.join(os.path.dirname(file_name), 
                                   os.path.splitext(os.path.basename(file_name))[0] + ".mpl")
        self.map_x = 0
        self.map_y = 0
        self.unit_count = 0
        self.unit_data_set = []
        self.unit_index = []
        
        # FB2檔案標頭
        self.fb2_head = bytes([0x43, 0x45, 0x4C, 0xD0, 0x07, 0x0F, 0x00, 0x1e, 0x00, 0x18, 0x00, 0x00, 0x00, 0x10, 0x00])
        # MPL檔案標頭
        self.mpl_head = bytes([0x4D, 0x50, 0x4C, 0xD0, 0x07, 0x0B, 0x00, 0x00, 0x00, 0x00, 0x00])
        
        self._load_fb2_file(file_name)
    
    def _load_fb2_file(self, file_name):
        """載入FB2檔案"""
        # 載入MPL檔案
        self._load_mpl_file()
        
        # 載入FB2檔案
        with open(file_name, 'rb') as f:
            data = f.read()
        
        self._parse_fb2_structure(data)
    
    def _load_mpl_file(self):
        """載入MPL檔案"""
        if not os.path.exists(self.mpl_file):
            raise FileNotFoundError(f"MPL檔案不存在: {self.mpl_file}")
        
        with open(self.mpl_file, 'rb') as f:
            data = f.read()
        
        # 檢查檔案大小是否足夠
        if len(data) < 0x0B + 2:  # 至少需要標頭 + 地圖尺寸
            raise ValueError(f"MPL檔案太小: {len(data)} bytes")
        
        # 調試：顯示前 20 個位元組
        print(f"DEBUG: MPL檔案前20個位元組: {data[:20].hex()}")
        
        # 嘗試不同的地圖尺寸讀取位置
        # 方法1：原始位置（位址 7 和 9）
        map_x_1 = Util.get_be_int16(data, 7)
        map_y_1 = Util.get_be_int16(data, 9)
        print(f"DEBUG: 方法1 (位址7,9): {map_x_1} x {map_y_1}")
        
        # 方法2：嘗試位址 8 和 10
        if len(data) >= 12:
            map_x_2 = Util.get_be_int16(data, 8)
            map_y_2 = Util.get_be_int16(data, 10)
            print(f"DEBUG: 方法2 (位址8,10): {map_x_2} x {map_y_2}")
        
        # 方法3：嘗試小端序
        map_x_3 = Util.get_le_int16(data, 7)
        map_y_3 = Util.get_le_int16(data, 9)
        print(f"DEBUG: 方法3 (小端序位址7,9): {map_x_3} x {map_y_3}")
        
        # 方法4：嘗試位址 6 和 8
        if len(data) >= 10:
            map_x_4 = Util.get_be_int16(data, 6)
            map_y_4 = Util.get_be_int16(data, 8)
            print(f"DEBUG: 方法4 (位址6,8): {map_x_4} x {map_y_4}")
        
        # 暫時使用方法3（小端序）作為測試
        self.map_x = map_x_3
        self.map_y = map_y_3
        
        print(f"DEBUG: 選擇的地圖尺寸: {self.map_x} x {self.map_y}")
        
        # 檢查地圖尺寸是否合理
        if self.map_x <= 0 or self.map_y <= 0:
            raise ValueError(f"無效的地圖尺寸: {self.map_x} x {self.map_y}")
        
        # 檢查地圖尺寸是否過大（防止記憶體溢出）
        if self.map_x > 1000 or self.map_y > 1000:
            raise ValueError(f"地圖尺寸過大: {self.map_x} x {self.map_y} (最大允許 1000x1000)")
        
        # 計算需要的單位索引數量
        unit_count = self.map_x * self.map_y
        required_size = 0x0B + unit_count * 2
        
        print(f"DEBUG: 計算的單位數量: {unit_count}")
        print(f"DEBUG: 需要的檔案大小: {required_size} bytes")
        
        # 檢查檔案是否有足夠的數據
        if len(data) < required_size:
            raise ValueError(f"MPL檔案數據不足: 需要 {required_size} bytes，實際 {len(data)} bytes")
        
        # 解析單位索引
        self.unit_index = []
        p = 0x0B
        for i in range(unit_count):
            self.unit_index.append(Util.get_le_int16(data, p))
            p += 2
    
    def _parse_fb2_structure(self, data):
        """解析FB2檔案結構"""
        # 檢查檔案大小是否足夠
        if len(data) < 0x0F:  # 至少需要標頭 + 單位數量
            raise ValueError(f"FB2檔案太小: {len(data)} bytes")
        
        # 獲取單位數量（使用小端序）
        self.unit_count = Util.get_le_uint16(data, 0x0B)
        
        # 檢查單位數量是否合理
        if self.unit_count <= 0:
            raise ValueError(f"無效的單位數量: {self.unit_count}")
        
        # 檢查單位數量是否過大（防止記憶體溢出）
        if self.unit_count > 10000:
            raise ValueError(f"單位數量過大: {self.unit_count} (最大允許 10000)")
        
        # 計算需要的偏移表大小
        offset_table_size = 0x0F + self.unit_count * 4
        
        # 檢查檔案是否有足夠的偏移表數據
        if len(data) < offset_table_size:
            raise ValueError(f"FB2檔案偏移表數據不足: 需要 {offset_table_size} bytes，實際 {len(data)} bytes")
        
        # 解析單位數據
        p = 0x0F
        for i in range(self.unit_count):
            if i == self.unit_count - 1:
                # 最後一個單位
                offset = Util.get_le_int32(data, p)
                
                # 檢查偏移是否有效
                if offset < 0 or offset >= len(data):
                    raise ValueError(f"無效的單位數據偏移: {offset}")
                
                unit_data = UnitData()
                unit_data.data = self.get_sub_array(data, offset, len(data) - offset)
                self.unit_data_set.append(unit_data)
            else:
                # 其他單位
                offset = Util.get_le_int32(data, p)
                offset1 = Util.get_le_int32(data, p + 4)
                
                # 檢查偏移是否有效
                if offset < 0 or offset1 < 0 or offset >= len(data) or offset1 > len(data) or offset >= offset1:
                    raise ValueError(f"無效的單位數據偏移範圍: {offset} - {offset1}")
                
                unit_data = UnitData()
                unit_data.data = self.get_sub_array(data, offset, offset1 - offset)
                self.unit_data_set.append(unit_data)
                p += 4
    
    def dispose(self):
        """釋放資源"""
        self.unit_data_set.clear()
    
    def get_map_draw_data(self):
        """獲取地圖繪製數據"""
        ret = bytearray(self.map_x * self.BLOCK_X_LIMIT * self.map_y * self.BLOCK_Y_LIMIT * 2)
        p = 0
        
        for i in range(len(self.unit_index)):
            # 檢查索引是否有效
            if self.unit_index[i] < 0 or self.unit_index[i] >= len(self.unit_data_set):
                raise ValueError(f"無效的單位索引: {self.unit_index[i]} (總共 {len(self.unit_data_set)} 個單位)")
            
            unit_data = self.get_draw_data(self.unit_data_set[self.unit_index[i]].data)
            self.copy_buffer(unit_data, 0, ret, p, len(unit_data))
            p += len(unit_data)
        
        return bytes(ret)
    
    def get_map_bitmap(self):
        """獲取地圖位圖"""
        draw_data = self.get_map_draw_data()
        return self.make_bitmap(draw_data, self.map_x * self.BLOCK_X_LIMIT, 
                               self.map_y * self.BLOCK_Y_LIMIT)
    
    def save_bitmap_to_fb2_info(self, bitmap):
        """從點陣圖儲存到 FB2 資訊"""
        self.unit_data_set.clear()
        self.unit_index = [0] * (self.map_x * self.map_y)
        
        original_unit_data = bytearray(self.BLOCK_X_LIMIT * self.BLOCK_Y_LIMIT * 2)

        for p in range(self.map_x * self.map_y):
            block_y = p // self.map_x
            block_x = p % self.map_x
            
            start_x = block_x * self.BLOCK_X_LIMIT
            start_y = block_y * self.BLOCK_Y_LIMIT
            
            pixel_data_pointer = 0
            for j in range(self.BLOCK_Y_LIMIT):
                for i in range(self.BLOCK_X_LIMIT):
                    px_x = start_x + i
                    px_y = start_y + j
                    
                    r, g, b, _ = bitmap.getpixel((px_x, px_y))
                    
                    # 將 8-bit RGB 轉換為 15-bit RGB555 大端序
                    color_val = ((r & 0xF8) << 7) | ((g & 0xF8) << 2) | ((b & 0xF8) >> 3)
                    Util.set_be_uint16(original_unit_data, pixel_data_pointer, color_val)
                    pixel_data_pointer += 2
            
            ud = UnitData()
            ud.data = self.compress_unit_data(bytes(original_unit_data))
            self.unit_data_set.append(ud)
            self.unit_index[p] = p

    def save_fb2_to_file(self):
        """保存FB2檔案"""
        backup_file = self._create_backup_file(self.fb2_file, ".FB2")
        
        # 計算檔案大小
        file_size = self._get_fb2_current_file_size()
        if file_size == -1:
            return ""
        
        # 構建檔案數據
        file_data = bytearray(file_size)
        p_offset = 0x0F
        p_data = p_offset + 4 * len(self.unit_data_set)
        
        # 複製標頭
        file_data[:len(self.fb2_head)] = self.fb2_head
        
        # 設置單位數量
        Util.set_be_uint16(file_data, 11, len(self.unit_data_set))
        
        # 寫入單位數據
        for unit_data in self.unit_data_set:
            Util.set_be_uint32(file_data, p_offset, p_data)
            p_offset += 4
            file_data[p_data:p_data+len(unit_data.data)] = unit_data.data
            p_data += len(unit_data.data)
        
        # 創建備份並寫入新檔案
        if os.path.exists(self.fb2_file):
            import shutil
            shutil.copy2(self.fb2_file, backup_file)
        
        with open(self.fb2_file, 'wb') as f:
            f.write(file_data)
        
        return backup_file
    
    def save_mpl_to_file(self):
        """保存MPL檔案"""
        backup_file = self._create_backup_file(self.mpl_file, ".MPL")
        
        # 計算檔案大小
        file_size = self._get_mpl_current_file_size()
        if file_size == -1:
            return ""
        
        # 構建檔案數據
        file_data = bytearray(file_size)
        p_offset = 0x0B
        
        # 複製標頭
        file_data[:len(self.mpl_head)] = self.mpl_head
        
        # 設置地圖尺寸
        Util.set_be_uint16(file_data, 7, self.map_x)
        Util.set_be_uint16(file_data, 9, self.map_y)
        
        # 寫入單位索引
        for index in self.unit_index:
            Util.set_be_uint16(file_data, p_offset, index)
            p_offset += 2
        
        # 創建備份並寫入新檔案
        if os.path.exists(self.mpl_file):
            import shutil
            shutil.copy2(self.mpl_file, backup_file)
        
        with open(self.mpl_file, 'wb') as f:
            f.write(file_data)
        
        return backup_file
    
    def _get_fb2_current_file_size(self):
        """獲取FB2檔案當前大小"""
        if self.fb2_file is None:
            return -1
        
        size = len(self.fb2_head) + len(self.unit_data_set) * 4
        for unit_data in self.unit_data_set:
            size += len(unit_data.data)
        
        return size
    
    def _get_mpl_current_file_size(self):
        """獲取MPL檔案當前大小"""
        if self.fb2_file is None:
            return -1
        
        return len(self.mpl_head) + len(self.unit_index) * 2
    
    def _create_backup_file(self, original_file, extension):
        """創建備份檔案"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        backup_name = f"{os.path.splitext(original_file)[0]}_Bak_{timestamp}{extension}"
        return backup_name 