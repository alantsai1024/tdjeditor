#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天地劫神魔至尊傳編輯器 - 打包腳本
使用 PyInstaller 將程序打包成 exe 文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_dirs():
    """清理之前的構建目錄"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目錄: {dir_name}")
            shutil.rmtree(dir_name)
    
    # 清理 .spec 文件
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        print(f"清理文件: {spec_file}")
        os.remove(spec_file)

def build_exe():
    """構建 exe 文件"""
    print("開始打包天地劫編輯器...")

    # 獲取當前目錄的絕對路徑
    current_dir = os.path.abspath('.')
    icon_path = os.path.join(current_dir, 'tdj.ico')

    # PyInstaller 命令參數
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包成單個exe文件
        '--windowed',                   # 不顯示控制台窗口
        f'--icon={icon_path}',         # 設置圖標（使用絕對路徑）
        '--name=天地劫編輯器',           # 設置exe文件名
        '--distpath=release',          # 輸出目錄
        '--clean',                     # 清理臨時文件
        '--noconfirm',                 # 不詢問覆蓋
        'main.py'                      # 主程序文件
    ]
    
    print("執行命令:", ' '.join(cmd))
    
    try:
        # 執行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("打包成功！")
        print(result.stdout)
        
        # 檢查輸出文件
        exe_path = Path('release/天地劫編輯器.exe')
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"\n✅ 打包完成！")
            print(f"📁 輸出位置: {exe_path.absolute()}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            
            # 創建發布說明
            create_release_info()
        else:
            print("❌ 錯誤：未找到生成的exe文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失敗：{e}")
        print("錯誤輸出:", e.stderr)
        return False
    
    return True

def create_release_info():
    """創建發布說明文件"""
    readme_content = """# 天地劫神魔至尊傳編輯器

## 功能特色
- 🎮 SAF/FB2 檔案編輯支持
- 🖼️ 圖像導入/導出功能
- 🎬 自動播放動畫預覽
- 📊 聲音分析功能
- 🍎 現代化蘋果風格界面
- ⚙️ 豐富的輸出設置選項

## 使用方法
1. 雙擊 `天地劫編輯器.exe` 啟動程序
2. 點擊「開啟檔案」選擇 SAF 或 FB2 檔案
3. 使用各種功能編輯和處理檔案

## 快捷鍵
- Ctrl+O: 開啟檔案
- Ctrl+S: 保存檔案
- 空格鍵: 播放/暫停動畫
- 左/右箭頭: 切換幀
- F5: 重新繪製

## 系統需求
- Windows 7 或更高版本
- 無需安裝 Python 環境

## 版本信息
- 版本: 1.0.0
- 構建時間: """ + str(Path().absolute()) + """

---
© 2024 天地劫編輯器 - 基於 Python + Tkinter 開發
"""
    
    with open('release/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("📝 已創建 README.txt 說明文件")

def main():
    """主函數"""
    print("=" * 50)
    print("🎮 天地劫神魔至尊傳編輯器 - 打包工具")
    print("=" * 50)
    
    # 檢查必要文件
    required_files = ['main.py', 'tdj.ico']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    # 清理舊的構建文件
    clean_build_dirs()
    
    # 創建輸出目錄
    os.makedirs('release', exist_ok=True)
    
    # 開始打包
    if build_exe():
        print("\n🎉 打包完成！可以在 release 目錄中找到 exe 文件。")
    else:
        print("\n❌ 打包失敗，請檢查錯誤信息。")

if __name__ == "__main__":
    main()
