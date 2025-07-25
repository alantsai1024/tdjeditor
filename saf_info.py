import struct
import os
from datetime import datetime
from PIL import Image
from base_unit_info import BaseUnitInfo
from util import Util
from alpha2_config import Alpha2Config

class WaveHeader:
    """波形標頭"""
    def __init__(self):
        self.RIFF = ""
        self.FileSize = 0
        self.WAVE = ""
        self.FORMAT = ""
        self.FormatSize = 0
        self.FilePadding = 0
        self.FormatChannels = 0
        self.SamplesPerSecond = 0
        self.AverageBytesPerSecond = 0
        self.BytesPerSample = 0
        self.BitsPerSample = 0
        self.FormatExtra = 0
        self.FACT = ""
        self.FactSize = 0
        self.FactInf = 0
        self.DATA = bytes()
        self.DataSize = 0

class UnitDataSet:
    """單元數據集"""
    def __init__(self):
        self.data = bytes()

class FrameConstruct:
    """幀結構"""
    def __init__(self):
        self.data = bytes()
        self.x = 0
        self.y = 0
        self.bitmap = None

class ParameterUnit:
    """參數單元"""
    def __init__(self):
        self.frame_index = 0
        self.draw_x = 0
        self.draw_y = 0
        self.alpha = 0
        self.red = 0
        self.green = 0
        self.blue = 0

class FrameParameter:
    """幀參數"""
    def __init__(self):
        self.data = bytes()
        self.params = []
        self.wave_index = 0

class WaveData:
    """波形數據"""
    def __init__(self):
        self.channels = 0
        self.bits = 0
        self.sample_rate = 0
        self.data_length = 0
        self.data = bytes()

class UnknownData:
    """未知數據"""
    def __init__(self):
        self.data = bytes()

class SAFInfo(BaseUnitInfo):
    """SAF檔案信息類"""
    
    def __init__(self, file_path):
        super().__init__()
        
        # SAF檔案特定屬性
        self.saf_file = file_path
        self.frame_parameter = []
        self.frame_construct = []
        self.unit_data_set = []
        self.wave_data = []
        self.unknown_data1 = []
        
        # SAF檔案標頭
        self.saf_head = bytes([0x53, 0x41, 0x46, 0x05, 0x02, 0x74, 0x00, 0x1e, 0x00, 0x18, 0x00, 0x00])
        self.size_sector = 10 * (2 + 4 + 4) + 4  # 2字節個數+4字節起始地址+4字節結束地址
        self.offset_frame_parameter_begin = 0x74
        
        # 解析SAF檔案
        self._parse_saf_file()
    
    def _parse_saf_file(self):
        """解析SAF檔案"""
        try:
            with open(self.saf_file, 'rb') as f:
                buffer = f.read()
            
            p = 12  # 從標頭後開始
            i = 1
            j = 1
            
            # 讀取第一個itemcount
            itemcount = Util.get_le_int16(buffer, p)
            
            while itemcount != 0:
                itemstart = Util.get_le_int32(buffer, p + 2)
                itemlength = Util.get_le_int32(buffer, p + 6)
                last_item_end = itemstart + itemlength
                
                while j <= itemcount:
                    if i > 5:
                        raise Exception("出現未知Chunk")
                    
                    if i != 5:
                        # 檢查itemstart+4是否超出buffer
                        if itemstart + 4 > len(buffer):
                            raise Exception(f"subitemstart超出檔案範圍: itemstart={itemstart}, buffer_size={len(buffer)}")
                        subitemstart = Util.get_le_int32(buffer, itemstart)
                        if j < itemcount:
                            if itemstart + 8 > len(buffer):
                                raise Exception(f"subitemend超出檔案範圍: itemstart={itemstart}, buffer_size={len(buffer)}")
                            subitemend = Util.get_le_int32(buffer, itemstart + 4)
                        else:
                            subitemend = last_item_end
                        # 檢查邊界
                        if subitemstart >= len(buffer) or subitemend > len(buffer) or subitemstart >= subitemend:
                            raise Exception(f"無效的數據範圍: start={subitemstart}, end={subitemend}, buffer_size={len(buffer)}")
                        subdata = buffer[subitemstart:subitemend]
                    else:
                        if p + 2 + itemcount * 2 > len(buffer):
                            raise Exception(f"未知數據區塊超出範圍: p={p}, itemcount={itemcount}, buffer_size={len(buffer)}")
                        subdata = buffer[p + 2:p + 2 + itemcount * 2]
                    
                    # 根據類型處理數據
                    if i == 1:
                        fp = FrameParameter()
                        fp.data = subdata
                        self.frame_parameter.append(fp)
                    elif i == 2:
                        fc = FrameConstruct()
                        fc.data = subdata
                        if len(subdata) >= 4:
                            fc.x = Util.get_le_uint16(subdata, 0) * 30
                            fc.y = Util.get_le_uint16(subdata, 2) * 24
                        self.frame_construct.append(fc)
                    elif i == 3:
                        fd = UnitDataSet()
                        fd.data = subdata
                        self.unit_data_set.append(fd)
                    elif i == 4:
                        ud = WaveData()
                        if len(subdata) >= 8:
                            ud.channels = subdata[0]
                            ud.bits = subdata[1]
                            ud.sample_rate = Util.get_be_uint16(subdata, 2)
                            ud.data_length = Util.get_be_int32(subdata, 4)
                        ud.data = subdata
                        self.wave_data.append(ud)
                    elif i == 5:
                        ud1 = UnknownData()
                        ud1.data = subdata
                        self.unknown_data1.append(ud1)
                    
                    itemstart += 4
                    j += 1
                
                p += 10
                i += 1
                j = 1
                
                # 讀取下一個itemcount
                if p + 2 <= len(buffer):
                    itemcount = Util.get_le_int16(buffer, p)
                else:
                    itemcount = 0
            
            # 處理幀參數
            self._process_frame_parameters()
            
        except Exception as e:
            raise Exception(f"解析SAF檔案時發生錯誤: {str(e)}")
    
    def _process_frame_parameters(self):
        """處理幀參數"""
        for fp in self.frame_parameter:
            if fp.data and len(fp.data) >= 10:
                param_count = Util.get_le_int16(fp.data, 8)
                fp.wave_index = Util.get_le_int16(fp.data, 0)
                tp = 10
                
                if param_count != 0:
                    if fp.params is None:
                        fp.params = []
                    
                    for j in range(param_count):
                        if tp + 11 <= len(fp.data):  # 確保有足夠的數據
                            pu = ParameterUnit()
                            pu.frame_index = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            pu.draw_x = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            pu.draw_y = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            pu.alpha = fp.data[tp]
                            tp += 1
                            pu.red = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            pu.green = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            pu.blue = Util.get_le_int16(fp.data, tp)
                            tp += 2
                            
                            fp.params.append(pu)
    
    def get_frame_count(self):
        """獲取幀數量"""
        return len(self.frame_parameter)
    
    def get_frame_x(self, frame_index):
        """獲取幀寬度"""
        if 0 <= frame_index < len(self.frame_construct):
            return self.frame_construct[frame_index].x
        return 0
    
    def get_frame_y(self, frame_index):
        """獲取幀高度"""
        if 0 <= frame_index < len(self.frame_construct):
            return self.frame_construct[frame_index].y
        return 0
    
    def _get_frame_draw_data(self, frame_construct_index):
        """從一個FrameConstruct中提取所有單元的繪製數據"""
        if not (0 <= frame_construct_index < len(self.frame_construct)):
            return bytes()

        # FrameConstruct數據的前4字節是寬高，之後是單元索引列表
        construct_data = self.frame_construct[frame_construct_index].data[4:]
        all_unit_draw_data = bytearray()
        p = 0
        while p + 2 <= len(construct_data):
            # 根據測試，此處也應為小端序
            unit_index = Util.get_le_int16(construct_data, p)
            p += 2
            
            if unit_index < 0:
                continue
            if not (0 <= unit_index < len(self.unit_data_set)):
                continue
                
            unit_data = self.unit_data_set[unit_index].data
            if unit_data:
                # 調用基類的get_draw_data解壓單元數據
                unit_draw_data = self.get_draw_data(unit_data)
                all_unit_draw_data.extend(unit_draw_data)
                
        return bytes(all_unit_draw_data)

    def _make_frame_construct_bitmap(self, frame_construct_index):
        """將一個完整的FrameConstruct繪製成位圖"""
        if not (0 <= frame_construct_index < len(self.frame_construct)):
            return None
        
        frame_x = self.get_frame_x(frame_construct_index)
        frame_y = self.get_frame_y(frame_construct_index)
        
        if frame_x <= 0 or frame_y <= 0:
            return None

        draw_data = self._get_frame_draw_data(frame_construct_index)
        if not draw_data:
            return None
        
        # 調用基類的make_bitmap進行繪製，啟用透明度處理
        bitmap = self.make_bitmap(draw_data, frame_x, frame_y, is_transparent=True)
        
        # 確保黑色背景變為透明（與C#版本一致）
        if bitmap:
            bitmap = self._make_black_transparent(bitmap)
        
        return bitmap
    
    def _make_black_transparent(self, image):
        """將黑色背景變為透明（模擬C#的MakeTransparent）"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        new_image = image.copy()
        pixels = new_image.load()
        if pixels is None:
            return image

        for y in range(new_image.height):
            for x in range(new_image.width):
                r, g, b, a = pixels[x, y]
                # 將純黑色像素變為透明
                if r == 0 and g == 0 and b == 0:
                    pixels[x, y] = (0, 0, 0, 0)
        
        return new_image

    def get_frame_bitmap(self, frame_index):
        """獲取最終合成的幀位圖"""
        if 0 <= frame_index < len(self.frame_parameter):
            return self._make_frame_bitmap(frame_index)
        return None
    
    def _make_frame_bitmap(self, frame_index):
        """通過組合多個FrameConstruct來製作最終的幀位圖"""
        if frame_index >= len(self.frame_parameter):
            return None
        
        fp = self.frame_parameter[frame_index]
        if not fp.params:
            return None
        
        # 預先生成所有需要的位圖，並計算最終畫布大小
        temp_bitmaps = []
        max_x = 0
        max_y = 0
        for param in fp.params:
            if param.frame_index < 0:
                continue
            
            construct_bitmap = self._make_frame_construct_bitmap(param.frame_index)
            if construct_bitmap:
                max_x = max(max_x, param.draw_x + construct_bitmap.width)
                max_y = max(max_y, param.draw_y + construct_bitmap.height)
                temp_bitmaps.append({'bitmap': construct_bitmap, 'param': param})

        if max_x == 0 or max_y == 0:
            return None
            
        # 創建最終畫布
        image = Image.new('RGBA', (max_x, max_y), (0, 0, 0, 0))

        # 將所有位圖合成到畫布上，正確的圖層順序（先畫底層，後畫上層）
        for item in temp_bitmaps:
            # 應用顏色和透明度調整
            adjusted_bitmap = self._adjust_unit_colors(item['bitmap'], item['param'])
            # 使用alpha_composite進行帶透明度的合成
            image.alpha_composite(adjusted_bitmap, (item['param'].draw_x, item['param'].draw_y))
            
        return image
    
    def _adjust_unit_colors(self, bitmap, param):
        """調整位圖顏色和透明度（基於C#邏輯，像素級處理）"""
        if not bitmap:
            return bitmap

        adjusted = bitmap.copy()
        pixels = adjusted.load()

        # 根據alphaFlag設定透明度及透明色
        if param.alpha == 0x00:
            alpha_factor = 1.0
            transparent_color = None
        elif param.alpha == 0x01:
            alpha_factor = 0.75  # 調整為0.75，減少透明度（原本0.5太透明）
            transparent_color = None
        elif param.alpha == 0x02:
            # alpha=2 的特殊處理：半透明+高亮+重複疊加更鮮豔
            return self._apply_alpha2_enhanced_effects(adjusted, param)
        elif param.alpha == 0x07:
            alpha_factor = 1.0
            transparent_color = (255, 255, 255)  # 白色
        else:
            alpha_factor = 1.0
            transparent_color = None

        for y in range(adjusted.height):
            for x in range(adjusted.width):
                r, g, b, a = pixels[x, y]
                # 處理透明色
                if transparent_color and (r, g, b) == transparent_color:
                    a = 0
                else:
                    # 像素級 alpha 混合
                    a = int(a * alpha_factor)
                pixels[x, y] = (r, g, b, a)
        return adjusted

    def _apply_alpha2_enhanced_effects(self, bitmap, param):
        """為alpha=2應用真正的重複疊加效果：將相同元素重複疊加使其變鮮豔"""
        if not bitmap:
            return bitmap

        # 從配置文件獲取增強參數
        config = Alpha2Config.get_config()
        base_alpha = config['base_alpha']
        highlight_factor = config['highlight_factor']
        saturation_boost = config['saturation_boost']
        overlay_intensity = config['overlay_intensity']

        # 重複疊加次數（可配置）
        overlay_count = getattr(config, 'overlay_count', 3)  # 預設疊加3次

        # 第一步：預處理原始圖像
        base_image = self._preprocess_alpha2_image(bitmap, highlight_factor, saturation_boost)

        # 第二步：執行重複疊加
        result_image = self._perform_multiple_overlay(base_image, overlay_count, overlay_intensity)

        # 第三步：應用最終的透明度
        final_image = self._apply_final_alpha(result_image, base_alpha)

        return final_image

    def _preprocess_alpha2_image(self, bitmap, highlight_factor, saturation_boost):
        """預處理alpha=2圖像：高亮和飽和度增強"""
        processed = bitmap.copy()
        pixels = processed.load()

        for y in range(processed.height):
            for x in range(processed.width):
                r, g, b, a = pixels[x, y]

                # 跳過完全透明的像素
                if a == 0:
                    continue

                # 黑色背景變為透明
                if r == 0 and g == 0 and b == 0:
                    pixels[x, y] = (0, 0, 0, 0)
                    continue

                # 1. 適中高亮處理 - 使alpha=2明亮但不過度
                # 使用溫和的高亮算法
                r = min(255, int(r * highlight_factor + (255 - r) * 0.15))  # 適中提升亮度
                g = min(255, int(g * highlight_factor + (255 - g) * 0.15))
                b = min(255, int(b * highlight_factor + (255 - b) * 0.15))

                # 如果highlight_factor >= 1.5，應用適中的額外亮度提升
                if highlight_factor >= 1.5:
                    brightness_boost = 0.2  # 額外20%亮度提升（降低了）
                    r = min(255, int(r + (255 - r) * brightness_boost))
                    g = min(255, int(g + (255 - g) * brightness_boost))
                    b = min(255, int(b + (255 - b) * brightness_boost))

                # 2. 飽和度增強
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                r = min(255, max(0, int(gray + (r - gray) * saturation_boost)))
                g = min(255, max(0, int(gray + (g - gray) * saturation_boost)))
                b = min(255, max(0, int(gray + (b - gray) * saturation_boost)))

                pixels[x, y] = (r, g, b, a)

        return processed

    def _perform_multiple_overlay(self, base_image, overlay_count, overlay_intensity):
        """執行多次重複疊加，模擬相同元素重複疊加的效果"""
        if overlay_count <= 1:
            return base_image

        # 創建結果圖像
        result = Image.new('RGBA', base_image.size, (0, 0, 0, 0))

        # 第一層：直接貼上基礎圖像
        result = Image.alpha_composite(result, base_image)

        # 後續層：重複疊加相同的圖像
        for i in range(1, overlay_count):
            # 計算當前層的強度（遞減以避免過度飽和）
            current_intensity = overlay_intensity * (1.0 - i * 0.1)
            current_intensity = max(0.1, current_intensity)  # 最小強度0.1

            # 創建當前層的疊加圖像
            overlay_layer = self._create_overlay_layer(base_image, current_intensity)

            # 使用加法混合模式疊加
            result = self._additive_blend(result, overlay_layer)

        return result

    def _create_overlay_layer(self, base_image, intensity):
        """創建疊加層，調整強度"""
        overlay = base_image.copy()
        pixels = overlay.load()

        for y in range(overlay.height):
            for x in range(overlay.width):
                r, g, b, a = pixels[x, y]

                if a == 0:
                    continue

                # 調整疊加層的強度
                overlay_alpha = int(a * intensity)
                pixels[x, y] = (r, g, b, overlay_alpha)

        return overlay

    def _additive_blend(self, base, overlay):
        """加法混合模式：將兩個圖像相加，產生更鮮豔的效果"""
        result = Image.new('RGBA', base.size, (0, 0, 0, 0))
        base_pixels = base.load()
        overlay_pixels = overlay.load()
        result_pixels = result.load()

        for y in range(result.height):
            for x in range(result.width):
                base_r, base_g, base_b, base_a = base_pixels[x, y]
                over_r, over_g, over_b, over_a = overlay_pixels[x, y]

                # 加法混合：顏色相加但限制在255以內
                final_r = min(255, base_r + int(over_r * over_a / 255))
                final_g = min(255, base_g + int(over_g * over_a / 255))
                final_b = min(255, base_b + int(over_b * over_a / 255))

                # 透明度使用較大值
                final_a = max(base_a, over_a)

                result_pixels[x, y] = (final_r, final_g, final_b, final_a)

        return result

    def _apply_final_alpha(self, image, base_alpha):
        """應用最終的透明度"""
        final = image.copy()
        pixels = final.load()

        for y in range(final.height):
            for x in range(final.width):
                r, g, b, a = pixels[x, y]

                if a > 0:
                    final_alpha = int(a * base_alpha)
                    pixels[x, y] = (r, g, b, final_alpha)

        return final

    def has_multiplex_unit(self):
        """檢查是否有重複使用的圖元"""
        # 實現檢查邏輯
        return False
    
    def save_bitmap_to_frame(self, bitmap, frame_index):
        """保存位圖到幀"""
        # 實現保存邏輯
        pass
    
    def save_saf_to_file(self, is_delete_wave=False):
        """保存SAF檔案"""
        # 實現保存邏輯
        return None
    
    def dispose(self):
        """釋放資源"""
        self.frame_parameter.clear()
        self.frame_construct.clear()
        self.unit_data_set.clear()
        self.wave_data.clear()
        self.unknown_data1.clear()

    def _make_csharp_wav_header(self, wave):
        """產生與C#一致的WAV header (固定44 bytes, 大端序)"""
        data_len = wave.data_length
        # 固定44 bytes WAV header
        header = bytearray([
            0x52,0x49,0x46,0x46,0,0,0,0,0x57,0x41,0x56,0x45,0x66,0x6D,0x74,0x20,
            0x10,0x00,0x00,0x00,0x01,0x00,0x01,0x00,0x22,0x56,0x00,0x00,0x44,0xAC,0x00,0x00,
            0x02,0x00,0x10,0x00,0x64,0x61,0x74,0x61,0,0,0,0
        ])
        # 動態填入 header
        header[0x16] = wave.channels
        header[0x18:0x1A] = wave.sample_rate.to_bytes(2, 'big')  # C#用BE
        header[0x20] = (wave.bits // 8) * wave.channels
        header[0x22] = wave.bits
        header[0x28:0x2C] = data_len.to_bytes(4, 'big')
        header[0x4:0x8] = (data_len + 0x1C).to_bytes(4, 'big')
        return header

    def export_single_wave(self, wave_index, filename):
        """仿照C#正確輸出WAV音效"""
        if not (0 <= wave_index < len(self.wave_data)):
            raise Exception(f"無效的音效索引: {wave_index}")
        wave = self.wave_data[wave_index]
        wav_header = self._make_csharp_wav_header(wave)
        with open(filename, 'wb') as f:
            f.write(wav_header)
            f.write(wave.data[8:8+wave.data_length])

    def export_combined_wave(self, filename):
        """仿照C#正確輸出第一個音效（與C#一致）"""
        if not self.wave_data:
            raise Exception("沒有音效資料可導出")
        wave = self.wave_data[0]
        wav_header = self._make_csharp_wav_header(wave)
        with open(filename, 'wb') as f:
            f.write(wav_header)
            f.write(wave.data[8:8+wave.data_length])

    def export_sequence_mixed_audio(self, filename, frame_duration_ms=100):
        """根據播放順序導出混合後的完整音頻（穩定版本，保持原始音質）"""
        if not self.wave_data:
            raise Exception("沒有音效資料可導出")

        if not self.frame_parameter:
            raise Exception("沒有幀參數資料")

        try:
            import numpy as np
        except ImportError:
            raise Exception("需要安裝numpy庫來支持音頻混合功能")

        # 使用原始音頻格式，避免不必要的轉換
        output_sample_rate = 22050  # 保持原始採樣率
        output_channels = 1         # 預設單聲道
        output_bits = 16           # 預設16位

        # 從現有音頻中選擇格式（保持原始格式）
        if self.wave_data:
            for wave in self.wave_data:
                if wave.sample_rate > 0 and wave.channels > 0 and wave.bits > 0:
                    output_sample_rate = wave.sample_rate
                    output_channels = wave.channels
                    output_bits = wave.bits
                    break

        print(f"使用音頻格式: {output_channels}聲道, {output_bits}bit, {output_sample_rate}Hz")

        # 計算每幀的樣本數
        frame_duration_seconds = frame_duration_ms / 1000.0
        samples_per_frame = int(output_sample_rate * frame_duration_seconds)

        print(f"每幀時長: {frame_duration_ms}ms, 每幀樣本數: {samples_per_frame}")

        # 預處理所有音頻數據（轉換為numpy數組進行正確混音）
        processed_audio = {}
        for i, wave in enumerate(self.wave_data):
            try:
                # 使用穩定的音頻樣本提取方法
                audio_samples = self._extract_audio_samples(wave, output_sample_rate, output_channels, output_bits)
                processed_audio[i] = audio_samples
                print(f"音頻 #{i}: {len(audio_samples)} 樣本")
            except Exception as e:
                print(f"警告：處理音頻 #{i} 時發生錯誤: {e}")
                processed_audio[i] = np.array([], dtype=np.int16)

        # 根據幀序列生成混合音頻（正確的時間軸混音）
        mixed_audio_samples = []

        for frame_idx, frame_param in enumerate(self.frame_parameter):
            wave_index = frame_param.wave_index

            if wave_index == -1 or wave_index not in processed_audio:
                # 靜音幀或無效索引
                silence_samples = np.zeros(samples_per_frame, dtype=np.int16)
                mixed_audio_samples.append(silence_samples)
            else:
                # 播放指定音頻
                audio_samples = processed_audio[wave_index]

                if len(audio_samples) == 0:
                    # 空音頻，使用靜音
                    silence_samples = np.zeros(samples_per_frame, dtype=np.int16)
                    mixed_audio_samples.append(silence_samples)
                elif len(audio_samples) >= samples_per_frame:
                    # 音頻足夠長，取前面部分
                    frame_samples = audio_samples[:samples_per_frame]
                    mixed_audio_samples.append(frame_samples)
                else:
                    # 音頻較短，使用完整音頻並補零
                    padded_samples = np.zeros(samples_per_frame, dtype=np.int16)
                    padded_samples[:len(audio_samples)] = audio_samples
                    mixed_audio_samples.append(padded_samples)

        # 合併所有幀的音頻
        final_audio_samples = np.concatenate(mixed_audio_samples)

        # 檢查並防止爆音（削波）- 使用更保守的閾值
        max_amplitude = np.max(np.abs(final_audio_samples))
        safe_threshold = 30000  # 使用更保守的閾值，約91.6%的最大值

        if max_amplitude > safe_threshold:
            # 如果超出安全閾值，進行正規化
            normalization_factor = safe_threshold / max_amplitude
            final_audio_samples = (final_audio_samples * normalization_factor).astype(np.int16)
            print(f"檢測到高振幅，已正規化: 原始最大振幅 {max_amplitude}, 正規化係數 {normalization_factor:.3f}")
        else:
            final_audio_samples = final_audio_samples.astype(np.int16)
            if max_amplitude > 25000:  # 75%閾值警告
                print(f"音頻振幅較高: {max_amplitude} (安全範圍內)")

        # 轉換為字節
        final_audio_bytes = final_audio_samples.tobytes()
        print(f"最終音頻: {len(final_audio_samples)} 樣本, {len(final_audio_samples)/output_sample_rate:.2f} 秒")

        # 導出為WAV檔案（使用與單一聲音導出完全相同的方式）
        self._save_mixed_wav_file_bytes_compatible(filename, final_audio_bytes, output_sample_rate, output_channels, output_bits)

        return {
            'total_frames': len(self.frame_parameter),
            'total_duration': len(final_audio_samples) / output_sample_rate,
            'sample_rate': output_sample_rate,
            'channels': output_channels,
            'bits': output_bits
        }

    def _extract_high_quality_audio_samples(self, wave, target_sample_rate, target_channels, target_bits):
        """提取高質量音頻樣本，支持採樣率轉換和防拍頻處理"""
        try:
            import numpy as np
            from scipy import signal
        except ImportError:
            # 如果沒有scipy，使用基本的numpy處理
            return self._extract_basic_high_quality_samples(wave, target_sample_rate, target_channels, target_bits)

        if wave.data_length == 0:
            return np.array([], dtype=np.float32)

        # 提取原始音頻數據（跳過8字節頭部）
        raw_audio = wave.data[8:8+wave.data_length]

        if len(raw_audio) == 0:
            return np.array([], dtype=np.float32)

        # 根據位深度解析音頻數據，轉換為浮點數
        if wave.bits == 8:
            # 8位音頻，無符號
            audio_samples = np.frombuffer(raw_audio, dtype=np.uint8)
            # 轉換為浮點數 [-1.0, 1.0]
            audio_samples = (audio_samples.astype(np.float32) - 128.0) / 128.0
        elif wave.bits == 16:
            # 16位音頻，有符號，小端序
            audio_samples = np.frombuffer(raw_audio, dtype='<i2')
            # 轉換為浮點數 [-1.0, 1.0]
            audio_samples = audio_samples.astype(np.float32) / 32768.0
        elif wave.bits == 24:
            # 24位音頻，需要特殊處理
            audio_samples = []
            for i in range(0, len(raw_audio), 3):
                if i + 2 < len(raw_audio):
                    sample = int.from_bytes(raw_audio[i:i+3], byteorder='little', signed=True)
                    audio_samples.append(sample / 8388608.0)  # 24位最大值
            audio_samples = np.array(audio_samples, dtype=np.float32)
        elif wave.bits == 32:
            # 32位音頻
            audio_samples = np.frombuffer(raw_audio, dtype=np.int32)
            audio_samples = audio_samples.astype(np.float32) / 2147483648.0
        else:
            # 不支持的位深度
            return np.array([], dtype=np.float32)

        # 處理聲道轉換
        if wave.channels == 2 and target_channels == 1:
            # 立體聲轉單聲道
            audio_samples = audio_samples.reshape(-1, 2)
            audio_samples = np.mean(audio_samples, axis=1)
        elif wave.channels == 1 and target_channels == 2:
            # 單聲道轉立體聲
            audio_samples = np.repeat(audio_samples, 2)

        # 採樣率轉換（使用高質量重採樣）
        if wave.sample_rate != target_sample_rate and wave.sample_rate > 0:
            # 計算重採樣比率
            resample_ratio = target_sample_rate / wave.sample_rate

            # 使用scipy的高質量重採樣
            if len(audio_samples) > 0:
                try:
                    # 使用polyphase濾波器進行高質量重採樣
                    new_length = int(len(audio_samples) * resample_ratio)
                    audio_samples = signal.resample(audio_samples, new_length)
                except:
                    # 如果scipy重採樣失敗，使用線性插值
                    old_indices = np.arange(len(audio_samples))
                    new_indices = np.linspace(0, len(audio_samples) - 1, int(len(audio_samples) * resample_ratio))
                    audio_samples = np.interp(new_indices, old_indices, audio_samples)

        # 應用輕微的抗混疊濾波，減少拍頻干擾
        if len(audio_samples) > 100:  # 只對足夠長的音頻應用濾波
            try:
                # 設計低通濾波器，截止頻率為奈奎斯特頻率的90%
                nyquist = target_sample_rate / 2
                cutoff = nyquist * 0.9
                sos = signal.butter(4, cutoff / nyquist, btype='low', output='sos')
                audio_samples = signal.sosfilt(sos, audio_samples)
            except:
                # 如果濾波失敗，跳過濾波步驟
                pass

        return audio_samples.astype(np.float32)

    def _extract_basic_high_quality_samples(self, wave, target_sample_rate, target_channels, target_bits):
        """基本的高質量音頻樣本提取（不依賴scipy）"""
        try:
            import numpy as np
        except ImportError:
            raise Exception("需要安裝numpy庫")

        if wave.data_length == 0:
            return np.array([], dtype=np.float32)

        # 提取原始音頻數據（跳過8字節頭部）
        raw_audio = wave.data[8:8+wave.data_length]

        if len(raw_audio) == 0:
            return np.array([], dtype=np.float32)

        # 根據位深度解析音頻數據，轉換為浮點數
        if wave.bits == 8:
            audio_samples = np.frombuffer(raw_audio, dtype=np.uint8)
            audio_samples = (audio_samples.astype(np.float32) - 128.0) / 128.0
        elif wave.bits == 16:
            audio_samples = np.frombuffer(raw_audio, dtype='<i2')
            audio_samples = audio_samples.astype(np.float32) / 32768.0
        else:
            # 其他位深度，預設轉換為16位處理
            audio_samples = np.frombuffer(raw_audio, dtype='<i2')
            audio_samples = audio_samples.astype(np.float32) / 32768.0

        # 處理聲道轉換
        if wave.channels == 2 and target_channels == 1:
            audio_samples = audio_samples.reshape(-1, 2)
            audio_samples = np.mean(audio_samples, axis=1)

        # 簡單的線性插值重採樣
        if wave.sample_rate != target_sample_rate and wave.sample_rate > 0:
            resample_ratio = target_sample_rate / wave.sample_rate
            if len(audio_samples) > 0:
                old_indices = np.arange(len(audio_samples))
                new_indices = np.linspace(0, len(audio_samples) - 1, int(len(audio_samples) * resample_ratio))
                audio_samples = np.interp(new_indices, old_indices, audio_samples)

        return audio_samples.astype(np.float32)

    def _extract_audio_samples(self, wave, target_sample_rate, target_channels, target_bits):
        """從WaveData中提取音頻樣本並轉換格式"""
        try:
            import numpy as np
        except ImportError:
            raise Exception("需要安裝numpy庫")

        if wave.data_length == 0:
            return np.array([], dtype=np.int16)

        # 提取原始音頻數據（跳過8字節頭部）
        raw_audio = wave.data[8:8+wave.data_length]

        if len(raw_audio) == 0:
            return np.array([], dtype=np.int16)

        # 根據位深度解析音頻數據（與SAF原始格式保持一致）
        if wave.bits == 8:
            # 8位音頻，無符號（與SAF格式一致）
            audio_samples = np.frombuffer(raw_audio, dtype=np.uint8)
            # 轉換為16位有符號（保持原始音質）
            audio_samples = (audio_samples.astype(np.int16) - 128) * 256
        elif wave.bits == 16:
            # 16位音頻，有符號，小端序（與SAF格式一致）
            audio_samples = np.frombuffer(raw_audio, dtype='<i2')  # 明確指定小端序
        elif wave.bits == 24:
            # 24位音頻，需要特殊處理
            audio_samples = []
            for i in range(0, len(raw_audio), 3):
                if i + 2 < len(raw_audio):
                    # 小端序24位轉16位
                    sample = int.from_bytes(raw_audio[i:i+3], byteorder='little', signed=True)
                    audio_samples.append(sample >> 8)  # 轉為16位
            audio_samples = np.array(audio_samples, dtype=np.int16)
        elif wave.bits == 32:
            # 32位音頻
            audio_samples = np.frombuffer(raw_audio, dtype=np.int32)
            # 轉換為16位
            audio_samples = (audio_samples >> 16).astype(np.int16)
        else:
            # 不支持的格式，返回空數組
            return np.array([], dtype=np.int16)

        # 處理聲道
        if wave.channels == 2 and target_channels == 1:
            # 立體聲轉單聲道（取平均）
            audio_samples = audio_samples.reshape(-1, 2)
            audio_samples = np.mean(audio_samples, axis=1).astype(np.int16)
        elif wave.channels == 1 and target_channels == 2:
            # 單聲道轉立體聲（複製）
            audio_samples = np.repeat(audio_samples, 2)

        # 處理採樣率（簡單重採樣）
        if wave.sample_rate != target_sample_rate and wave.sample_rate > 0:
            # 簡單的線性重採樣
            original_length = len(audio_samples)
            target_length = int(original_length * target_sample_rate / wave.sample_rate)

            if target_length > 0:
                indices = np.linspace(0, original_length - 1, target_length)
                audio_samples = np.interp(indices, np.arange(original_length), audio_samples).astype(np.int16)

        return audio_samples

    def _extract_raw_audio_bytes(self, wave):
        """直接提取原始音頻字節數據，完全避免numpy處理（與單一導出完全一致）"""
        if wave.data_length == 0:
            return b''

        # 直接返回原始音頻字節數據（跳過8字節頭部，與export_single_wave完全一致）
        raw_audio_bytes = wave.data[8:8+wave.data_length]

        # 如果是立體聲，需要轉為單聲道（但保持字節級操作）
        if wave.channels == 2 and wave.bits == 16:
            # 立體聲16位轉單聲道16位（字節級操作）
            mono_bytes = bytearray()
            for i in range(0, len(raw_audio_bytes), 4):  # 每4字節是一對立體聲樣本
                if i + 3 < len(raw_audio_bytes):
                    # 讀取左右聲道（小端序16位）
                    left = int.from_bytes(raw_audio_bytes[i:i+2], 'little', signed=True)
                    right = int.from_bytes(raw_audio_bytes[i+2:i+4], 'little', signed=True)
                    # 平均值
                    mono = (left + right) // 2
                    # 轉回字節（小端序）
                    mono_bytes.extend(mono.to_bytes(2, 'little', signed=True))
            return bytes(mono_bytes)

        elif wave.channels == 2 and wave.bits == 8:
            # 立體聲8位轉單聲道8位
            mono_bytes = bytearray()
            for i in range(0, len(raw_audio_bytes), 2):  # 每2字節是一對立體聲樣本
                if i + 1 < len(raw_audio_bytes):
                    left = raw_audio_bytes[i]
                    right = raw_audio_bytes[i+1]
                    mono = (left + right) // 2
                    mono_bytes.append(mono)
            return bytes(mono_bytes)

        else:
            # 單聲道或其他格式，直接返回原始數據
            return raw_audio_bytes

    def _save_mixed_wav_file_bytes_compatible(self, filename, audio_bytes, sample_rate, channels, bits):
        """保存混合音頻字節數據為WAV檔案（完全模仿單一聲音導出的方式）"""

        # 創建一個臨時的WaveData對象來使用現有的_make_csharp_wav_header方法
        temp_wave = type('TempWave', (), {})()
        temp_wave.channels = channels
        temp_wave.bits = bits
        temp_wave.sample_rate = sample_rate
        temp_wave.data_length = len(audio_bytes)

        # 使用與單一聲音導出完全相同的頭部生成方法
        wav_header = self._make_csharp_wav_header(temp_wave)

        # 使用與單一聲音導出完全相同的寫入方式
        with open(filename, 'wb') as f:
            f.write(wav_header)
            f.write(audio_bytes)  # 直接寫入原始字節數據，與export_single_wave完全一致

    def _save_mixed_wav_file_csharp_compatible(self, filename, audio_data, sample_rate, channels, bits):
        """保存混合音頻數據為WAV檔案（使用與單一聲音導出相同的C#兼容格式）"""
        try:
            import numpy as np
        except ImportError:
            raise Exception("需要numpy庫")

        # 確保音頻數據是正確的格式
        if len(audio_data) == 0:
            raise Exception("音頻數據為空")

        # 轉換音頻數據為字節（與原始SAF音頻數據格式一致）
        if bits == 16:
            # 16位有符號整數，小端序（與SAF原始數據一致）
            audio_bytes = audio_data.astype('<i2').tobytes()
        elif bits == 8:
            # 8位無符號整數
            audio_bytes = (audio_data + 128).astype('uint8').tobytes()
        else:
            # 預設使用16位
            audio_bytes = audio_data.astype('<i2').tobytes()

        data_len = len(audio_bytes)

        # 創建與單一聲音導出相同的WAV頭部（C#兼容格式）
        header = bytearray([
            0x52,0x49,0x46,0x46,0,0,0,0,0x57,0x41,0x56,0x45,0x66,0x6D,0x74,0x20,
            0x10,0x00,0x00,0x00,0x01,0x00,0x01,0x00,0x22,0x56,0x00,0x00,0x44,0xAC,0x00,0x00,
            0x02,0x00,0x10,0x00,0x64,0x61,0x74,0x61,0,0,0,0
        ])

        # 動態填入頭部信息（與_make_csharp_wav_header相同的邏輯）
        header[0x16] = channels
        header[0x18:0x1A] = sample_rate.to_bytes(2, 'big')  # C#用大端序
        header[0x20] = (bits // 8) * channels
        header[0x22] = bits
        header[0x28:0x2C] = data_len.to_bytes(4, 'big')  # 數據長度，大端序
        header[0x4:0x8] = (data_len + 0x1C).to_bytes(4, 'big')  # 檔案大小-8，大端序

        # 寫入檔案
        with open(filename, 'wb') as f:
            f.write(header)
            f.write(audio_bytes)

    def _save_wav_file(self, filename, audio_data, sample_rate, channels, bits):
        """保存音頻數據為WAV檔案（標準格式，保留用於兼容性）"""
        try:
            import wave
            import struct
        except ImportError:
            raise Exception("需要wave和struct庫")

        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bits // 8)
            wav_file.setframerate(sample_rate)

            # 轉換音頻數據為字節
            if bits == 16:
                audio_bytes = audio_data.astype('<i2').tobytes()
            elif bits == 8:
                audio_bytes = (audio_data + 128).astype('uint8').tobytes()
            else:
                # 預設使用16位
                audio_bytes = audio_data.astype('<i2').tobytes()

            wav_file.writeframes(audio_bytes)