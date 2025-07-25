#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAF編輯器演示腳本
展示如何使用Python版本的SAF編輯器核心功能
"""

import sys
import os
from PIL import Image, ImageDraw

# 添加當前目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from util import Util
from base_unit_info import BaseUnitInfo

def demo_basic_operations():
    """演示基本操作"""
    print("=== SAF編輯器基本操作演示 ===")
    
    # 1. 創建測試圖像
    print("1. 創建測試圖像...")
    base_info = BaseUnitInfo()
    
    # 創建一個簡單的彩色圖像
    draw_data = bytearray()
    for i in range(BaseUnitInfo.BLOCK_X_LIMIT * BaseUnitInfo.BLOCK_Y_LIMIT):
        # 創建漸變色彩
        r = (i % 32) << 10
        g = ((i * 2) % 32) << 5
        b = (i * 3) % 32
        color = r | g | b
        draw_data.extend([color & 0xFF, (color >> 8) & 0xFF])
    
    # 創建位圖
    bitmap = base_info.make_bitmap(bytes(draw_data), 
                                  BaseUnitInfo.BLOCK_X_LIMIT, 
                                  BaseUnitInfo.BLOCK_Y_LIMIT)
    
    # 保存演示圖像
    demo_image_path = "demo_image.png"
    bitmap.save(demo_image_path)
    print(f"   已創建演示圖像：{demo_image_path}")
    print(f"   圖像尺寸：{bitmap.width} x {bitmap.height}")
    print(f"   圖像模式：{bitmap.mode}")
    
    # 2. 演示座標計算
    print("\n2. 演示座標計算...")
    for offset in [0, 60, 120, 180]:
        x, y = BaseUnitInfo.get_draw_coordinate(offset, 60, 48)
        print(f"   offset={offset} -> (x={x}, y={y})")
    
    # 3. 演示數據轉換
    print("\n3. 演示數據轉換...")
    test_bytes = bytes([0x12, 0x34, 0x56, 0x78])
    hex_str = Util.conv_bytes_to_hex_string(test_bytes, 0, 4)
    print(f"   位元組轉十六進制：{hex_str}")
    
    converted_bytes = Util.conv_hex_string_to_bytes(hex_str)
    print(f"   十六進制轉位元組：{list(converted_bytes)}")
    
    # 4. 演示壓縮功能
    print("\n4. 演示壓縮功能...")
    # 創建包含重複模式的數據
    test_data = bytearray()
    for i in range(5):
        # 重複的顏色
        color = 0x1234
        test_data.extend([color & 0xFF, (color >> 8) & 0xFF])
    
    compressed = base_info.compress_unit_data(test_data)
    print(f"   原始數據長度：{len(test_data)} 位元組")
    print(f"   壓縮後長度：{len(compressed)} 位元組")
    print(f"   壓縮率：{len(compressed)/len(test_data)*100:.1f}%")
    
    return demo_image_path

def demo_image_processing():
    """演示圖像處理功能"""
    print("\n=== 圖像處理功能演示 ===")
    
    # 創建一個新的測試圖像
    base_info = BaseUnitInfo()
    
    # 創建不同顏色的區塊
    draw_data = bytearray()
    colors = [
        0x7C00,  # 紅色
        0x03E0,  # 綠色
        0x001F,  # 藍色
        0x7FFF,  # 白色
        0x0000   # 黑色
    ]
    
    for y in range(BaseUnitInfo.BLOCK_Y_LIMIT):
        for x in range(BaseUnitInfo.BLOCK_X_LIMIT):
            # 根據位置選擇顏色
            color_index = (x + y) % len(colors)
            color = colors[color_index]
            draw_data.extend([color & 0xFF, (color >> 8) & 0xFF])
    
    # 創建位圖
    bitmap = base_info.make_bitmap(bytes(draw_data), 
                                  BaseUnitInfo.BLOCK_X_LIMIT, 
                                  BaseUnitInfo.BLOCK_Y_LIMIT)
    
    # 保存彩色圖像
    color_image_path = "demo_color_image.png"
    bitmap.save(color_image_path)
    print(f"已創建彩色演示圖像：{color_image_path}")
    
    return color_image_path

def demo_util_functions():
    """演示工具函數"""
    print("\n=== 工具函數演示 ===")
    
    # 測試數據
    test_data = bytes([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0])
    
    print("小端序讀取測試：")
    print(f"  get_le_int16(0) = {Util.get_le_int16(test_data, 0):04X}")
    print(f"  get_le_int16(2) = {Util.get_le_int16(test_data, 2):04X}")
    print(f"  get_le_int32(0) = {Util.get_le_int32(test_data, 0):08X}")
    
    # 測試寫入
    test_array = bytearray(8)
    Util.set_le_uint16(test_array, 0, 0x1234)
    Util.set_le_uint32(test_array, 2, 0x56789ABC)
    
    print("\n小端序寫入測試：")
    print(f"  寫入後的數據：{' '.join(f'{b:02X}' for b in test_array)}")

def main():
    """主演示函數"""
    print("SAF編輯器 - Python版本演示")
    print("=" * 50)
    
    try:
        # 演示基本操作
        demo_image_path = demo_basic_operations()
        
        # 演示圖像處理
        color_image_path = demo_image_processing()
        
        # 演示工具函數
        demo_util_functions()
        
        print("\n" + "=" * 50)
        print("演示完成！")
        print(f"創建的檔案：")
        print(f"  - {demo_image_path}")
        print(f"  - {color_image_path}")
        print("\n你可以使用以下命令啟動圖形界面：")
        print("  python main.py")
        
    except Exception as e:
        print(f"演示過程中發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 