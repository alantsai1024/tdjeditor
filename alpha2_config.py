#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha=2 增強效果配置文件
用戶可以通過修改這個文件來調整alpha=2的視覺效果
"""

class Alpha2Config:
    """Alpha=2 效果配置類"""
    
    # 預設配置 - 平衡的增強效果
    DEFAULT = {
        'base_alpha': 0.85,         # 基礎透明度 (0.0-1.0) - 調整為0.85，減少透明度
        'highlight_factor': 1.3,    # 高亮增強係數 (1.0-2.0)
        'saturation_boost': 1.5,    # 飽和度提升係數 (1.0-3.0)
        'overlay_intensity': 0.4,   # 重複疊加強度 (0.0-1.0)
        'overlay_count': 3,         # 重複疊加次數 (1-5)
        'name': '預設增強'
    }
    
    # 強烈高亮配置 - 適合需要突出顯示的元素
    STRONG_HIGHLIGHT = {
        'base_alpha': 0.9,          # 調整為0.9，減少透明度
        'highlight_factor': 1.8,
        'saturation_boost': 1.3,
        'overlay_intensity': 0.3,
        'overlay_count': 2,
        'name': '強烈高亮'
    }

    # 適中明亮配置 - alpha=2元素明亮但不過度
    MODERATE_BRIGHT = {
        'base_alpha': 0.85,         # 較高不透明度
        'highlight_factor': 1.6,    # 適中高亮
        'saturation_boost': 1.4,    # 適中飽和度
        'overlay_intensity': 0.4,   # 適中疊加
        'overlay_count': 2,         # 適中疊加次數
        'name': '適中明亮'
    }

    # 超級飽和配置 - 適合需要鮮豔色彩的裝飾效果
    SUPER_SATURATED = {
        'base_alpha': 0.8,          # 調整為0.8，減少透明度
        'highlight_factor': 1.2,
        'saturation_boost': 2.0,
        'overlay_intensity': 0.5,
        'overlay_count': 4,
        'name': '超級飽和'
    }

    # 重疊加強配置 - 適合需要強烈視覺衝擊的特效
    OVERLAY_ENHANCED = {
        'base_alpha': 0.85,         # 調整為0.85，減少透明度
        'highlight_factor': 1.1,
        'saturation_boost': 1.2,
        'overlay_intensity': 0.8,
        'overlay_count': 5,
        'name': '重疊加強'
    }

    # 柔和增強配置 - 適合需要保持細節的半透明效果
    SOFT_ENHANCED = {
        'base_alpha': 0.95,         # 調整為0.95，減少透明度
        'highlight_factor': 1.1,
        'saturation_boost': 1.2,
        'overlay_intensity': 0.2,
        'overlay_count': 2,
        'name': '柔和增強'
    }

    # 極致鮮豔配置 - 最大化色彩效果
    ULTRA_VIVID = {
        'base_alpha': 0.75,         # 調整為0.75，減少透明度
        'highlight_factor': 2.0,
        'saturation_boost': 2.5,
        'overlay_intensity': 0.7,
        'overlay_count': 4,
        'name': '極致鮮豔'
    }

    # 遊戲特效配置 - 適合遊戲中的特殊效果
    GAME_EFFECT = {
        'base_alpha': 0.8,          # 調整為0.8，減少透明度
        'highlight_factor': 1.6,
        'saturation_boost': 1.8,
        'overlay_intensity': 0.6,
        'overlay_count': 3,
        'name': '遊戲特效'
    }
    
    # 當前使用的配置 - 用戶可以修改這個來改變效果
    CURRENT = MODERATE_BRIGHT  # 改為適中明亮配置
    
    @classmethod
    def get_config(cls):
        """獲取當前配置"""
        return cls.CURRENT.copy()
    
    @classmethod
    def set_config(cls, config_name):
        """設置配置"""
        configs = {
            'DEFAULT': cls.DEFAULT,
            'STRONG_HIGHLIGHT': cls.STRONG_HIGHLIGHT,
            'MODERATE_BRIGHT': cls.MODERATE_BRIGHT,
            'SUPER_SATURATED': cls.SUPER_SATURATED,
            'OVERLAY_ENHANCED': cls.OVERLAY_ENHANCED,
            'SOFT_ENHANCED': cls.SOFT_ENHANCED,
            'ULTRA_VIVID': cls.ULTRA_VIVID,
            'GAME_EFFECT': cls.GAME_EFFECT
        }
        
        if config_name in configs:
            cls.CURRENT = configs[config_name]
            return True
        return False
    
    @classmethod
    def set_custom_config(cls, base_alpha=None, highlight_factor=None,
                         saturation_boost=None, overlay_intensity=None,
                         overlay_count=None, name="自定義"):
        """設置自定義配置"""
        config = cls.CURRENT.copy()

        if base_alpha is not None:
            config['base_alpha'] = max(0.0, min(1.0, base_alpha))
        if highlight_factor is not None:
            config['highlight_factor'] = max(1.0, min(3.0, highlight_factor))
        if saturation_boost is not None:
            config['saturation_boost'] = max(1.0, min(3.0, saturation_boost))
        if overlay_intensity is not None:
            config['overlay_intensity'] = max(0.0, min(1.0, overlay_intensity))
        if overlay_count is not None:
            config['overlay_count'] = max(1, min(5, overlay_count))

        config['name'] = name
        cls.CURRENT = config
    
    @classmethod
    def list_presets(cls):
        """列出所有預設配置"""
        presets = [
            ('DEFAULT', cls.DEFAULT),
            ('STRONG_HIGHLIGHT', cls.STRONG_HIGHLIGHT),
            ('MODERATE_BRIGHT', cls.MODERATE_BRIGHT),
            ('SUPER_SATURATED', cls.SUPER_SATURATED),
            ('OVERLAY_ENHANCED', cls.OVERLAY_ENHANCED),
            ('SOFT_ENHANCED', cls.SOFT_ENHANCED),
            ('ULTRA_VIVID', cls.ULTRA_VIVID),
            ('GAME_EFFECT', cls.GAME_EFFECT)
        ]
        
        print("可用的 Alpha=2 效果預設:")
        for name, config in presets:
            print(f"  {name}: {config['name']}")
            print(f"    透明度: {config['base_alpha']:.1f}")
            print(f"    高亮: {config['highlight_factor']:.1f}")
            print(f"    飽和度: {config['saturation_boost']:.1f}")
            print(f"    疊加: {config['overlay_intensity']:.1f}")
            print()
    
    @classmethod
    def print_current_config(cls):
        """打印當前配置"""
        config = cls.CURRENT
        print(f"當前 Alpha=2 配置: {config['name']}")
        print(f"  基礎透明度: {config['base_alpha']:.2f}")
        print(f"  高亮增強係數: {config['highlight_factor']:.2f}")
        print(f"  飽和度提升係數: {config['saturation_boost']:.2f}")
        print(f"  重複疊加強度: {config['overlay_intensity']:.2f}")
        print(f"  重複疊加次數: {config.get('overlay_count', 3)}")

# 使用示例
if __name__ == "__main__":
    print("=== Alpha=2 配置管理 ===")
    
    # 顯示所有預設
    Alpha2Config.list_presets()
    
    # 顯示當前配置
    print("=" * 40)
    Alpha2Config.print_current_config()
    
    # 切換到不同配置
    print("\n切換到強烈高亮配置:")
    Alpha2Config.set_config('STRONG_HIGHLIGHT')
    Alpha2Config.print_current_config()
    
    # 設置自定義配置
    print("\n設置自定義配置:")
    Alpha2Config.set_custom_config(
        base_alpha=0.8,
        highlight_factor=1.5,
        saturation_boost=1.7,
        overlay_intensity=0.5,
        name="我的自定義效果"
    )
    Alpha2Config.print_current_config()
