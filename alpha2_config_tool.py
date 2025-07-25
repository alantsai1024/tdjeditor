#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha=2 配置切換工具
提供交互式界面來調整alpha=2的效果參數
"""

import sys
from alpha2_config import Alpha2Config

def main():
    """主程序"""
    print("=" * 50)
    print("      Alpha=2 效果配置工具")
    print("=" * 50)
    
    while True:
        show_menu()
        choice = input("\n請選擇操作 (1-6): ").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            list_all_presets()
        elif choice == '3':
            switch_preset()
        elif choice == '4':
            create_custom_config()
        elif choice == '5':
            test_current_config()
        elif choice == '6':
            print("感謝使用！")
            break
        else:
            print("無效選擇，請重新輸入。")
        
        input("\n按Enter鍵繼續...")

def show_menu():
    """顯示主菜單"""
    print("\n" + "-" * 50)
    print("1. 查看當前配置")
    print("2. 列出所有預設")
    print("3. 切換預設配置")
    print("4. 創建自定義配置")
    print("5. 測試當前配置")
    print("6. 退出")
    print("-" * 50)

def show_current_config():
    """顯示當前配置"""
    print("\n當前配置詳情:")
    print("=" * 30)
    Alpha2Config.print_current_config()
    
    config = Alpha2Config.get_config()
    print(f"\n效果說明:")
    print(f"- 透明度: {get_alpha_description(config['base_alpha'])}")
    print(f"- 高亮: {get_highlight_description(config['highlight_factor'])}")
    print(f"- 飽和度: {get_saturation_description(config['saturation_boost'])}")
    print(f"- 疊加: {get_overlay_description(config['overlay_intensity'])}")

def list_all_presets():
    """列出所有預設配置"""
    print("\n所有可用預設:")
    print("=" * 40)
    Alpha2Config.list_presets()

def switch_preset():
    """切換預設配置"""
    presets = {
        '1': 'DEFAULT',
        '2': 'STRONG_HIGHLIGHT',
        '3': 'SUPER_SATURATED',
        '4': 'OVERLAY_ENHANCED',
        '5': 'SOFT_ENHANCED',
        '6': 'ULTRA_VIVID',
        '7': 'GAME_EFFECT'
    }
    
    print("\n選擇預設配置:")
    print("1. 預設增強 (DEFAULT)")
    print("2. 強烈高亮 (STRONG_HIGHLIGHT)")
    print("3. 超級飽和 (SUPER_SATURATED)")
    print("4. 重疊加強 (OVERLAY_ENHANCED)")
    print("5. 柔和增強 (SOFT_ENHANCED)")
    print("6. 極致鮮豔 (ULTRA_VIVID)")
    print("7. 遊戲特效 (GAME_EFFECT)")
    
    choice = input("\n請選擇 (1-7): ").strip()
    
    if choice in presets:
        preset_name = presets[choice]
        if Alpha2Config.set_config(preset_name):
            print(f"\n✓ 已切換到: {preset_name}")
            show_current_config()
        else:
            print("✗ 切換失敗")
    else:
        print("無效選擇")

def create_custom_config():
    """創建自定義配置"""
    print("\n創建自定義配置:")
    print("=" * 30)
    print("提示: 直接按Enter使用當前值")
    
    current = Alpha2Config.get_config()
    
    # 獲取自定義參數
    try:
        # 透明度
        alpha_input = input(f"基礎透明度 (0.0-1.0, 當前: {current['base_alpha']:.2f}): ").strip()
        base_alpha = float(alpha_input) if alpha_input else current['base_alpha']
        
        # 高亮係數
        highlight_input = input(f"高亮增強係數 (1.0-3.0, 當前: {current['highlight_factor']:.2f}): ").strip()
        highlight_factor = float(highlight_input) if highlight_input else current['highlight_factor']
        
        # 飽和度係數
        saturation_input = input(f"飽和度提升係數 (1.0-3.0, 當前: {current['saturation_boost']:.2f}): ").strip()
        saturation_boost = float(saturation_input) if saturation_input else current['saturation_boost']
        
        # 疊加強度
        overlay_input = input(f"重複疊加強度 (0.0-1.0, 當前: {current['overlay_intensity']:.2f}): ").strip()
        overlay_intensity = float(overlay_input) if overlay_input else current['overlay_intensity']

        # 疊加次數
        count_input = input(f"重複疊加次數 (1-5, 當前: {current.get('overlay_count', 3)}): ").strip()
        overlay_count = int(count_input) if count_input else current.get('overlay_count', 3)

        # 配置名稱
        name = input("配置名稱 (可選): ").strip() or "自定義配置"

        # 應用配置
        Alpha2Config.set_custom_config(
            base_alpha=base_alpha,
            highlight_factor=highlight_factor,
            saturation_boost=saturation_boost,
            overlay_intensity=overlay_intensity,
            overlay_count=overlay_count,
            name=name
        )
        
        print(f"\n✓ 自定義配置已創建: {name}")
        show_current_config()
        
    except ValueError:
        print("✗ 輸入格式錯誤，請輸入有效的數字")
    except Exception as e:
        print(f"✗ 創建配置時發生錯誤: {e}")

def test_current_config():
    """測試當前配置"""
    print("\n測試當前配置...")
    
    try:
        # 導入測試模塊
        from PIL import Image, ImageDraw
        from saf_info import SAFInfo, ParameterUnit
        
        # 創建簡單測試圖像
        test_image = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(test_image)
        
        # 繪製測試圖案
        colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]
        for i, color in enumerate(colors):
            x = i * 30 + 10
            draw.rectangle([x, 10, x+25, 35], fill=color)
        
        # 創建SAFInfo實例進行測試
        saf_info = SAFInfo.__new__(SAFInfo)
        saf_info.frame_parameter = []
        saf_info.frame_construct = []
        saf_info.unit_data_set = []
        saf_info.wave_data = []
        saf_info.unknown_data1 = []
        
        # 創建alpha=2參數
        param = ParameterUnit()
        param.alpha = 0x02
        
        # 應用當前配置
        processed_image = saf_info._apply_alpha2_enhanced_effects(test_image, param)
        
        # 保存測試結果
        test_filename = "config_test_result.png"
        processed_image.save(test_filename)
        
        print(f"✓ 測試完成，結果已保存到: {test_filename}")
        
        # 簡單分析
        pixels = processed_image.load()
        if pixels:
            brightness_sum = 0
            count = 0
            for y in range(processed_image.height):
                for x in range(processed_image.width):
                    r, g, b, a = pixels[x, y]
                    if a > 0:
                        brightness_sum += (r + g + b) / 3
                        count += 1
            
            if count > 0:
                avg_brightness = brightness_sum / count
                print(f"平均亮度: {avg_brightness:.1f}/255")
        
    except ImportError:
        print("✗ 無法導入必要的模塊進行測試")
    except Exception as e:
        print(f"✗ 測試時發生錯誤: {e}")

def get_alpha_description(value):
    """獲取透明度描述"""
    if value <= 0.3:
        return "高透明"
    elif value <= 0.6:
        return "中等透明"
    elif value <= 0.8:
        return "輕微透明"
    else:
        return "幾乎不透明"

def get_highlight_description(value):
    """獲取高亮描述"""
    if value <= 1.2:
        return "輕微高亮"
    elif value <= 1.5:
        return "中等高亮"
    elif value <= 1.8:
        return "強烈高亮"
    else:
        return "極強高亮"

def get_saturation_description(value):
    """獲取飽和度描述"""
    if value <= 1.3:
        return "輕微增強"
    elif value <= 1.7:
        return "中等增強"
    elif value <= 2.2:
        return "強烈增強"
    else:
        return "極致鮮豔"

def get_overlay_description(value):
    """獲取疊加描述"""
    if value <= 0.2:
        return "輕微疊加"
    elif value <= 0.5:
        return "中等疊加"
    elif value <= 0.7:
        return "強烈疊加"
    else:
        return "極強疊加"

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已中斷。")
    except Exception as e:
        print(f"\n程序發生錯誤: {e}")
        sys.exit(1)
