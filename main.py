import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from saf_info import SAFInfo
from fb2_info import FB2Info
import sys

class SAFEditorApp:
    """SAF編輯器主應用程式"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("天地劫神魔至尊傳編輯器")

        # 設置現代化主題樣式
        self.setup_styles()

        # 支援 PyInstaller 打包後的圖標路徑
        icon_path = os.path.join(getattr(sys, '_MEIPASS', ''), 'tdj.ico') if hasattr(sys, '_MEIPASS') else 'tdj.ico'
        try:
            self.root.iconbitmap(icon_path)
        except Exception as e:
            # 若.ico失敗，嘗試用iconphoto+png
            try:
                png_icon_path = icon_path.replace('.ico', '.png')
                if os.path.exists(png_icon_path):
                    img = Image.open(png_icon_path)
                    icon = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, icon)
            except Exception as e2:
                print(f'無法設定視窗圖標: {e}, {e2}')

        self.root.geometry("1200x800")
        self.root.minsize(800, 600)  # 設置最小視窗大小

        # 初始化變數
        self.saf_info = None
        self.fb2_info = None
        self.current_frame_index = -1
        self.current_bitmap = None
        self.bitmap_scale = 1
        self.current_file_name = ""

        # 自動播放相關變數
        self.is_playing = False
        self.play_timer = None
        self.play_speed = 100  # 毫秒

        self.setup_ui()

    def get_system_font(self):
        """獲取系統字體"""
        import platform
        system = platform.system()
        if system == "Darwin":  # macOS
            return "SF Pro Display"
        elif system == "Windows":
            return "Segoe UI"
        else:  # Linux
            return "Ubuntu"

    def setup_styles(self):
        """設置蘋果風格樣式"""
        style = ttk.Style()

        # 蘋果風格色彩定義
        self.colors = {
            'bg_primary': '#f5f5f7',      # 主背景色
            'bg_secondary': '#ffffff',     # 次要背景色
            'accent_blue': '#007AFF',      # 蘋果藍
            'button_secondary': '#f2f2f7', # 次要按鈕色
            'text_primary': '#1d1d1f',     # 主文字色
            'text_secondary': '#86868b',   # 次要文字色
            'border_light': '#d2d2d7',     # 淺邊框色
            'success': '#34c759',          # 成功色
            'warning': '#ff9500',          # 警告色
            'error': '#ff3b30'             # 錯誤色
        }

        # 設置根視窗背景
        self.root.configure(bg=self.colors['bg_primary'])

        # 設置基礎主題
        try:
            style.theme_use('clam')
        except:
            pass

        # 獲取系統字體
        system_font = self.get_system_font()

        # 配置主要按鈕樣式（蘋果藍）
        style.configure('Apple.TButton',
                       background=self.colors['accent_blue'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=(system_font, 10, 'normal'),
                       padding=(16, 8))

        style.map('Apple.TButton',
                 background=[('active', '#0056d6'),
                           ('pressed', '#004bb8')])

        # 配置次要按鈕樣式
        style.configure('AppleSecondary.TButton',
                       background=self.colors['button_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_light'],
                       focuscolor='none',
                       font=(system_font, 10, 'normal'),
                       padding=(16, 8))

        style.map('AppleSecondary.TButton',
                 background=[('active', '#e8e8ed'),
                           ('pressed', '#d8d8dd')])

        # 配置LabelFrame樣式
        style.configure('Apple.TLabelframe',
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border_light'])

        style.configure('Apple.TLabelframe.Label',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=(system_font, 11, 'bold'))

        # 配置Frame樣式
        style.configure('Apple.TFrame',
                       background=self.colors['bg_secondary'])

        # 配置Label樣式
        style.configure('AppleTitle.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=(system_font, 10, 'bold'))

        style.configure('AppleBody.TLabel',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'],
                       font=(system_font, 9, 'normal'))

        # 配置Combobox樣式
        style.configure('Apple.TCombobox',
                       fieldbackground=self.colors['bg_secondary'],
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       bordercolor=self.colors['border_light'],
                       font=(system_font, 9, 'normal'))

        # 配置Entry樣式
        style.configure('Apple.TEntry',
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=1,
                       bordercolor=self.colors['border_light'],
                       font=(system_font, 9, 'normal'))

        # 配置Checkbutton樣式
        style.configure('Apple.TCheckbutton',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=(system_font, 9, 'normal'),
                       focuscolor='none')
    
    def setup_ui(self):
        """設置蘋果風格用戶界面"""
        # 創建主框架
        main_frame = ttk.Frame(self.root, style='Apple.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 創建左側控制面板 - 使用簡單的滾動框架
        control_outer_frame = ttk.Frame(main_frame, style='Apple.TFrame')
        control_outer_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 16))
        control_outer_frame.configure(width=280)
        control_outer_frame.pack_propagate(False)

        # 創建滾動畫布
        canvas = tk.Canvas(control_outer_frame, bg=self.colors['bg_primary'],
                          highlightthickness=0, width=260)
        scrollbar = ttk.Scrollbar(control_outer_frame, orient="vertical", command=canvas.yview)

        # 創建可滾動的控制面板
        control_frame = ttk.LabelFrame(canvas, text="控制面板",
                                     style='Apple.TLabelframe', padding=10)

        # 配置滾動
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 將控制面板添加到畫布
        canvas.create_window((0, 0), window=control_frame, anchor="nw")

        # 綁定滾動事件
        def update_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        control_frame.bind("<Configure>", update_scroll_region)

        # 綁定滑鼠滾輪事件
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # 檔案操作區塊
        file_frame = ttk.LabelFrame(control_frame, text="檔案操作",
                                  style='Apple.TLabelframe', padding=8)
        file_frame.pack(fill=tk.X, pady=(0, 8))

        # 開啟檔案按鈕 - 主要操作
        open_frame = ttk.Frame(file_frame, style='Apple.TFrame')
        open_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(open_frame, text="開啟檔案", command=self.open_file_dialog,
                  style="Apple.TButton").pack(fill=tk.X)

        # 保存檔案按鈕組
        save_frame = ttk.Frame(file_frame, style='Apple.TFrame')
        save_frame.pack(fill=tk.X, pady=(0, 6))
        save_left = ttk.Frame(save_frame, style='Apple.TFrame')
        save_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        save_right = ttk.Frame(save_frame, style='Apple.TFrame')
        save_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(save_left, text="保存 SAF", command=self.save_saf_file,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(save_right, text="保存 FB2", command=self.save_fb2_file,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 匯出功能按鈕組
        export_frame = ttk.Frame(file_frame, style='Apple.TFrame')
        export_frame.pack(fill=tk.X)
        export_left = ttk.Frame(export_frame, style='Apple.TFrame')
        export_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        export_right = ttk.Frame(export_frame, style='Apple.TFrame')
        export_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(export_left, text="匯出地圖", command=self.export_fb2_map_image,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(export_right, text="匯出音效", command=self.export_saf_wave,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 幀操作區塊
        frame_frame = ttk.LabelFrame(control_frame, text="幀操作",
                                   style='Apple.TLabelframe', padding=8)
        frame_frame.pack(fill=tk.X, pady=(0, 8))

        # 導航按鈕
        nav_frame = ttk.Frame(frame_frame, style='Apple.TFrame')
        nav_frame.pack(fill=tk.X, pady=(0, 6))
        nav_left = ttk.Frame(nav_frame, style='Apple.TFrame')
        nav_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        nav_right = ttk.Frame(nav_frame, style='Apple.TFrame')
        nav_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(nav_left, text="上一幀", command=self.prev_frame,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(nav_right, text="下一幀", command=self.next_frame,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 自動播放控制
        play_frame = ttk.Frame(frame_frame, style='Apple.TFrame')
        play_frame.pack(fill=tk.X, pady=(0, 6))

        self.play_button = ttk.Button(play_frame, text="播放", command=self.toggle_play,
                                     style="Apple.TButton")
        self.play_button.pack(fill=tk.X)

        # 播放速度控制
        speed_frame = ttk.Frame(frame_frame, style='Apple.TFrame')
        speed_frame.pack(fill=tk.X, pady=(0, 6))

        speed_label_frame = ttk.Frame(speed_frame, style='Apple.TFrame')
        speed_label_frame.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(speed_label_frame, text="播放速度", style='AppleTitle.TLabel').pack(side=tk.LEFT)

        self.speed_var = tk.StringVar(value="100")
        speed_combo = ttk.Combobox(speed_frame, textvariable=self.speed_var,
                                  values=["50", "100", "200", "500", "1000"],
                                  state="readonly", style='Apple.TCombobox')
        speed_combo.pack(fill=tk.X)
        speed_combo.bind('<<ComboboxSelected>>', self.on_speed_changed)

        ttk.Button(frame_frame, text="重新繪製", command=self.redraw_frame,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 圖像處理區塊
        image_frame = ttk.LabelFrame(control_frame, text="圖像處理",
                                   style='Apple.TLabelframe', padding=8)
        image_frame.pack(fill=tk.X, pady=(0, 8))

        # 單張圖像操作
        single_frame = ttk.Frame(image_frame, style='Apple.TFrame')
        single_frame.pack(fill=tk.X, pady=(0, 6))
        single_left = ttk.Frame(single_frame, style='Apple.TFrame')
        single_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        single_right = ttk.Frame(single_frame, style='Apple.TFrame')
        single_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(single_left, text="導入圖像", command=self.import_image,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(single_right, text="導出圖像", command=self.export_image,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 批量操作
        batch_frame = ttk.Frame(image_frame, style='Apple.TFrame')
        batch_frame.pack(fill=tk.X)
        batch_left = ttk.Frame(batch_frame, style='Apple.TFrame')
        batch_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        batch_right = ttk.Frame(batch_frame, style='Apple.TFrame')
        batch_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(batch_left, text="批量導入", command=self.batch_import,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(batch_right, text="批量導出", command=self.batch_export,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        


        # 顯示控制區塊
        display_frame = ttk.LabelFrame(control_frame, text="顯示控制",
                                     style='Apple.TLabelframe', padding=8)
        display_frame.pack(fill=tk.X, pady=(0, 8))

        # 縮放控制
        scale_label_frame = ttk.Frame(display_frame, style='Apple.TFrame')
        scale_label_frame.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(scale_label_frame, text="縮放倍數", style='AppleTitle.TLabel').pack(side=tk.LEFT)

        self.scale_var = tk.StringVar(value="1")
        scale_combo = ttk.Combobox(display_frame, textvariable=self.scale_var,
                                  values=["1", "2", "3", "4", "5"], state="readonly",
                                  style='Apple.TCombobox')
        scale_combo.pack(fill=tk.X)
        scale_combo.bind('<<ComboboxSelected>>', self.on_scale_changed)

        # 輸出設置區塊
        size_frame = ttk.LabelFrame(control_frame, text="輸出設置",
                                  style='Apple.TLabelframe', padding=8)
        size_frame.pack(fill=tk.X, pady=(0, 8))

        # 統一大小選項
        uniform_frame = ttk.Frame(size_frame, style='Apple.TFrame')
        uniform_frame.pack(fill=tk.X, pady=(0, 6))

        self.uniform_size_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(uniform_frame, text="統一輸出大小",
                       variable=self.uniform_size_var, style='Apple.TCheckbutton').pack(side=tk.LEFT)

        ttk.Button(uniform_frame, text="自動檢測", command=self.auto_detect_size,
                  style="AppleSecondary.TButton").pack(side=tk.RIGHT)

        # 檢測結果顯示
        self.size_info_var = tk.StringVar(value="未檢測")
        size_info_frame = ttk.Frame(size_frame, style='Apple.TFrame')
        size_info_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(size_info_frame, text="檢測尺寸", style='AppleTitle.TLabel').pack(side=tk.LEFT)
        size_info_label = ttk.Label(size_info_frame, textvariable=self.size_info_var,
                                   foreground=self.colors['accent_blue'],
                                   font=(self.get_system_font(), 9, 'bold'),
                                   background=self.colors['bg_secondary'])
        size_info_label.pack(side=tk.RIGHT)

        # 對齊方式
        align_label_frame = ttk.Frame(size_frame, style='Apple.TFrame')
        align_label_frame.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(align_label_frame, text="對齊方式", style='AppleTitle.TLabel').pack(side=tk.LEFT)

        self.align_var = tk.StringVar(value="top-left")
        align_combo = ttk.Combobox(size_frame, textvariable=self.align_var,
                                  values=["top-left", "center", "top-right", "bottom-left", "bottom-right"],
                                  state="readonly", style='Apple.TCombobox')
        align_combo.pack(fill=tk.X, pady=(0, 6))

        # 背景顏色
        bg_label_frame = ttk.Frame(size_frame, style='Apple.TFrame')
        bg_label_frame.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(bg_label_frame, text="背景顏色", style='AppleTitle.TLabel').pack(side=tk.LEFT)

        self.bg_color_var = tk.StringVar(value="transparent")
        bg_combo = ttk.Combobox(size_frame, textvariable=self.bg_color_var,
                               values=["transparent", "black", "white", "gray"],
                               state="readonly", style='Apple.TCombobox')
        bg_combo.pack(fill=tk.X)

        # 初始化內部變量（用於存儲檢測到的尺寸）
        self.detected_width = 256
        self.detected_height = 256

        # 檔案信息顯示
        info_frame = ttk.LabelFrame(control_frame, text="檔案信息",
                                  style='Apple.TLabelframe', padding=8)
        info_frame.pack(fill=tk.X, pady=(0, 8))

        self.file_path_label = ttk.Label(info_frame, text="未開啟檔案",
                                        wraplength=240, style='AppleBody.TLabel')
        self.file_path_label.pack(fill=tk.X, pady=(0, 4))

        self.file_info_label = ttk.Label(info_frame, text="", wraplength=240,
                                        foreground=self.colors['success'],
                                        font=(self.get_system_font(), 9, 'normal'),
                                        background=self.colors['bg_secondary'])
        self.file_info_label.pack(fill=tk.X, pady=(0, 4))

        self.current_frame_label = ttk.Label(info_frame, text="", wraplength=240,
                                           foreground=self.colors['accent_blue'],
                                           font=(self.get_system_font(), 9, 'normal'),
                                           background=self.colors['bg_secondary'])
        self.current_frame_label.pack(fill=tk.X)

        # 聲音分析面板
        audio_frame = ttk.LabelFrame(control_frame, text="聲音分析",
                                   style='Apple.TLabelframe', padding=8)
        audio_frame.pack(fill=tk.X)

        # 聲音信息顯示
        self.audio_info_label = ttk.Label(audio_frame, text="未載入聲音數據",
                                         wraplength=240, style='AppleBody.TLabel')
        self.audio_info_label.pack(fill=tk.X, pady=(0, 4))

        # 當前幀聲音信息
        self.current_audio_label = ttk.Label(audio_frame, text="", wraplength=240,
                                           foreground=self.colors['warning'],
                                           font=(self.get_system_font(), 9, 'normal'),
                                           background=self.colors['bg_secondary'])
        self.current_audio_label.pack(fill=tk.X, pady=(0, 6))

        # 聲音分析按鈕
        audio_buttons_frame = ttk.Frame(audio_frame, style='Apple.TFrame')
        audio_buttons_frame.pack(fill=tk.X)

        audio_left = ttk.Frame(audio_buttons_frame, style='Apple.TFrame')
        audio_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        audio_right = ttk.Frame(audio_buttons_frame, style='Apple.TFrame')
        audio_right.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

        ttk.Button(audio_left, text="播放順序", command=self.analyze_audio_sequence,
                  style="AppleSecondary.TButton").pack(fill=tk.X)
        ttk.Button(audio_right, text="聲音統計", command=self.show_audio_statistics,
                  style="AppleSecondary.TButton").pack(fill=tk.X)

        # 創建右側顯示區域
        display_frame = ttk.LabelFrame(main_frame, text="圖像顯示",
                                     style='Apple.TLabelframe', padding=16)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 創建圖像顯示區域
        canvas_frame = ttk.Frame(display_frame, style='Apple.TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_secondary'],
                               relief=tk.FLAT, bd=0, highlightthickness=1,
                               highlightbackground=self.colors['border_light'])
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # 創建滾動條
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        # 設置鍵盤快捷鍵
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """設置鍵盤快捷鍵"""
        # 檔案操作快捷鍵
        self.root.bind('<Control-o>', lambda e: self.open_file_dialog())
        self.root.bind('<Control-s>', lambda e: self.save_saf_file() if self.saf_info else self.save_fb2_file())

        # 幀導航快捷鍵
        self.root.bind('<Left>', lambda e: self.prev_frame())
        self.root.bind('<Right>', lambda e: self.next_frame())
        self.root.bind('<F5>', lambda e: self.redraw_frame())
        self.root.bind('<space>', lambda e: self.toggle_play())  # 空格鍵播放/暫停

        # 圖像操作快捷鍵
        self.root.bind('<Control-i>', lambda e: self.import_image())
        self.root.bind('<Control-e>', lambda e: self.export_image())

        # 縮放快捷鍵
        self.root.bind('<Control-1>', lambda e: self.set_scale(1))
        self.root.bind('<Control-2>', lambda e: self.set_scale(2))
        self.root.bind('<Control-3>', lambda e: self.set_scale(3))

        # 讓畫布獲得焦點以接收鍵盤事件
        self.canvas.focus_set()
        self.canvas.bind('<Button-1>', lambda e: self.canvas.focus_set())

    def set_scale(self, scale):
        """設置縮放倍數"""
        self.scale_var.set(str(scale))
        self.bitmap_scale = scale
        if self.current_bitmap:
            self.display_image(self.current_bitmap)

    def toggle_play(self):
        """切換播放/暫停狀態"""
        if not self.saf_info or self.saf_info.get_frame_count() == 0:
            messagebox.showwarning("警告", "請先開啟SAF檔案")
            return

        if self.is_playing:
            self.stop_play()
        else:
            self.start_play()

    def start_play(self):
        """開始自動播放"""
        self.is_playing = True
        self.play_button.config(text="暫停")
        self.auto_play_next_frame()

    def stop_play(self):
        """停止自動播放"""
        self.is_playing = False
        self.play_button.config(text="播放")
        if self.play_timer:
            self.root.after_cancel(self.play_timer)
            self.play_timer = None

    def auto_play_next_frame(self):
        """自動播放下一幀"""
        if not self.is_playing:
            return

        # 移動到下一幀
        if self.current_frame_index >= self.saf_info.get_frame_count() - 1:
            # 到達最後一幀，從頭開始
            self.current_frame_index = 0
        else:
            self.current_frame_index += 1

        self.update_frame_display()

        # 設置下一次播放的計時器
        if self.is_playing:
            self.play_timer = self.root.after(self.play_speed, self.auto_play_next_frame)

    def on_speed_changed(self, event):
        """播放速度改變事件"""
        try:
            self.play_speed = int(self.speed_var.get())
        except ValueError:
            self.play_speed = 100

    def open_file_dialog(self):
        """統一的檔案開啟對話框"""
        file_path = filedialog.askopenfilename(
            title="選擇SAF或FB2檔案",
            filetypes=[
                ("支援的檔案", "*.saf;*.fb2"),
                ("SAF檔案", "*.saf"),
                ("FB2檔案", "*.fb2"),
                ("所有檔案", "*.*")
            ]
        )

        if not file_path:
            return

        # 根據副檔名決定開啟方式
        file_ext = file_path.lower().split('.')[-1]
        if file_ext == 'saf':
            self._open_saf_file_internal(file_path)
        elif file_ext == 'fb2':
            self._open_fb2_file_internal(file_path)
        else:
            messagebox.showerror("錯誤", "不支援的檔案格式")

    def _open_saf_file_internal(self, file_path):
        """內部SAF檔案開啟方法"""
        try:
            # 停止自動播放
            if self.is_playing:
                self.stop_play()

            if self.saf_info:
                self.saf_info.dispose()

            self.saf_info = SAFInfo(file_path)
            self.current_file_name = file_path
            self.current_frame_index = 0

            # 更新界面信息
            self.file_path_label.config(text=f"{file_path}")
            self.file_info_label.config(text=f"SAF 檔案 - 共含有 {self.saf_info.get_frame_count()} 幀")

            # 更新聲音信息
            self.update_audio_info()

            if self.saf_info.get_frame_count() > 0:
                self.update_frame_display()

            if self.saf_info.has_multiplex_unit():
                messagebox.showwarning("警告", "此SAF中含有重複使用的圖元，導入修改後有可能出現問題。")

        except Exception as e:
            messagebox.showerror("錯誤", f"開啟SAF檔案時發生錯誤：{str(e)}")

    def _open_fb2_file_internal(self, file_path):
        """內部FB2檔案開啟方法"""
        try:
            if self.fb2_info:
                self.fb2_info.dispose()

            self.fb2_info = FB2Info(file_path)
            self.current_file_name = file_path

            # 更新界面信息
            self.file_path_label.config(text=f"{file_path}")
            self.file_info_label.config(text=f"FB2 檔案 - 地圖尺寸: {self.fb2_info.map_x} x {self.fb2_info.map_y}")

            # 顯示地圖
            self.display_fb2_map()

        except Exception as e:
            messagebox.showerror("錯誤", f"開啟FB2檔案時發生錯誤：{str(e)}")
    
    def open_saf_file(self):
        """開啟SAF檔案（保留向後兼容）"""
        file_path = filedialog.askopenfilename(
            title="選擇SAF檔案",
            filetypes=[("SAF檔案", "*.saf"), ("所有檔案", "*.*")]
        )

        if file_path:
            self._open_saf_file_internal(file_path)

    def open_fb2_file(self):
        """開啟FB2檔案（保留向後兼容）"""
        file_path = filedialog.askopenfilename(
            title="選擇FB2檔案",
            filetypes=[("FB2檔案", "*.fb2"), ("所有檔案", "*.*")]
        )

        if file_path:
            self._open_fb2_file_internal(file_path)
    
    def display_fb2_map(self):
        """顯示FB2地圖"""
        if not self.fb2_info:
            return
        
        try:
            map_bitmap = self.fb2_info.get_map_bitmap()
            if map_bitmap:
                self.display_image(map_bitmap)
        except Exception as e:
            messagebox.showerror("錯誤", f"顯示地圖時發生錯誤：{str(e)}")
    
    def update_frame_display(self):
        """更新幀顯示"""
        if not self.saf_info or self.current_frame_index < 0:
            return
        
        try:
            frame_bitmap = self.saf_info.get_frame_bitmap(self.current_frame_index)
            if frame_bitmap:
                # 直接使用 SAF 處理後的圖像，不進行額外的透明度處理
                self.current_bitmap = frame_bitmap
                self.display_image(self.current_bitmap)
                
                # 更新幀信息
                frame_x = self.saf_info.get_frame_x(self.current_frame_index)
                frame_y = self.saf_info.get_frame_y(self.current_frame_index)
                self.current_frame_label.config(
                    text=f"當前繪製第 {self.current_frame_index + 1} 幀\t解析度為 {frame_x} * {frame_y}"
                )

                # 更新當前幀聲音信息
                self.update_current_frame_audio_info()
        except Exception as e:
            messagebox.showerror("錯誤", f"更新幀顯示時發生錯誤：{str(e)}")
    
    def make_black_transparent(self, image):
        """後製濾鏡：將圖像中的純黑像素變為透明（僅用於導出）"""
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        new_image = image.copy()
        pixels = new_image.load()
        if pixels is None:
            return image

        for y in range(new_image.height):
            for x in range(new_image.width):
                r, g, b, a = pixels[x, y]
                # 只處理完全不透明的黑色像素
                if r == 0 and g == 0 and b == 0 and a == 255:
                    pixels[x, y] = (0, 0, 0, 0)
        return new_image

    def resize_to_uniform_size(self, image):
        """將圖像調整為統一大小（優先左上角對齊，確保圖像顯示區域不偏移）"""
        if not self.uniform_size_var.get():
            return image

        # 使用檢測到的尺寸
        target_width = self.detected_width
        target_height = self.detected_height

        if target_width <= 0 or target_height <= 0:
            return image

        # 獲取背景顏色
        bg_color = self.bg_color_var.get()
        if bg_color == "transparent":
            background = (0, 0, 0, 0)
        elif bg_color == "black":
            background = (0, 0, 0, 255)
        elif bg_color == "white":
            background = (255, 255, 255, 255)
        elif bg_color == "gray":
            background = (128, 128, 128, 255)
        else:
            background = (0, 0, 0, 0)

        # 創建目標大小的畫布
        result = Image.new('RGBA', (target_width, target_height), background)

        # 優先使用左上角對齊，確保圖像顯示區域不會偏移
        align = self.align_var.get()

        # 如果原圖像太大，需要從左上角開始裁剪
        if image.width > target_width or image.height > target_height:
            # 從左上角開始裁剪，確保重要內容不丟失
            crop_width = min(target_width, image.width)
            crop_height = min(target_height, image.height)

            # 根據對齊方式決定裁剪起始位置
            if align == "center":
                crop_x = max(0, (image.width - target_width) // 2)
                crop_y = max(0, (image.height - target_height) // 2)
            elif align == "top-right":
                crop_x = max(0, image.width - target_width)
                crop_y = 0
            elif align == "bottom-left":
                crop_x = 0
                crop_y = max(0, image.height - target_height)
            elif align == "bottom-right":
                crop_x = max(0, image.width - target_width)
                crop_y = max(0, image.height - target_height)
            else:  # top-left 或其他情況，預設從左上角開始
                crop_x = 0
                crop_y = 0

            cropped_image = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))

            # 裁剪後的圖像放在畫布的左上角
            if cropped_image.mode == 'RGBA':
                result.paste(cropped_image, (0, 0), cropped_image)
            else:
                result.paste(cropped_image, (0, 0))
        else:
            # 小於或等於目標尺寸的圖像，根據對齊方式放置
            if align == "center":
                x = (target_width - image.width) // 2
                y = (target_height - image.height) // 2
            elif align == "top-right":
                x = target_width - image.width
                y = 0
            elif align == "bottom-left":
                x = 0
                y = target_height - image.height
            elif align == "bottom-right":
                x = target_width - image.width
                y = target_height - image.height
            else:  # top-left 或其他情況，預設左上角
                x, y = 0, 0

            # 確保位置不會超出邊界
            x = max(0, min(x, target_width - image.width))
            y = max(0, min(y, target_height - image.height))

            # 貼上原圖像
            if image.mode == 'RGBA':
                result.paste(image, (x, y), image)
            else:
                result.paste(image, (x, y))

        return result

    def auto_detect_size(self):
        """自動檢測最適合的尺寸（直接使用最大長寬）"""
        if not self.saf_info:
            messagebox.showwarning("警告", "請先開啟SAF檔案")
            return

        try:
            max_width = 0
            max_height = 0
            frame_count = 0

            # 檢查所有幀的大小
            for i in range(self.saf_info.get_frame_count()):
                frame_bitmap = self.saf_info.get_frame_bitmap(i)
                if frame_bitmap:
                    max_width = max(max_width, frame_bitmap.width)
                    max_height = max(max_height, frame_bitmap.height)
                    frame_count += 1

            if max_width > 0 and max_height > 0:
                # 更新內部變量
                self.detected_width = max_width
                self.detected_height = max_height

                # 更新顯示信息
                self.size_info_var.set(f"{max_width} x {max_height}")

                # 自動啟用統一大小功能
                self.uniform_size_var.set(True)

                # 預設設置為左上角對齊
                self.align_var.set("top-left")

                messagebox.showinfo("自動檢測完成",
                    f"檢測到最大尺寸: {max_width} x {max_height}\n"
                    f"共檢測 {frame_count} 幀\n"
                    f"已啟用統一輸出大小，對齊方式設為左上角")
            else:
                self.size_info_var.set("檢測失敗")
                messagebox.showwarning("警告", "無法檢測到有效的圖像尺寸")

        except Exception as e:
            self.size_info_var.set("檢測錯誤")
            messagebox.showerror("錯誤", f"自動檢測尺寸時發生錯誤：{str(e)}")

    def display_image(self, image):
        """顯示圖像"""
        if not image:
            return
        
        # 縮放圖像
        scaled_image = image.resize(
            (image.width * self.bitmap_scale, image.height * self.bitmap_scale),
            Image.Resampling.NEAREST
        )
        
        # 轉換為PhotoImage
        self.photo_image = ImageTk.PhotoImage(scaled_image)
        
        # 清除畫布並顯示新圖像
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)
        
        # 設置滾動區域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def prev_frame(self):
        """上一幀"""
        if not self.saf_info or self.current_frame_index <= 0:
            return

        # 手動切換時停止自動播放
        if self.is_playing:
            self.stop_play()

        self.current_frame_index -= 1
        self.update_frame_display()

    def next_frame(self):
        """下一幀"""
        if not self.saf_info or self.current_frame_index >= self.saf_info.get_frame_count() - 1:
            return

        # 手動切換時停止自動播放
        if self.is_playing:
            self.stop_play()

        self.current_frame_index += 1
        self.update_frame_display()
    
    def redraw_frame(self):
        """重繪幀"""
        self.update_frame_display()
    
    def import_image(self):
        """導入圖像"""
        if not self.saf_info or self.current_frame_index < 0:
            messagebox.showwarning("警告", "請先開啟SAF檔案並選擇幀")
            return
        
        if not self.current_bitmap:
            messagebox.showwarning("警告", "沒有當前幀圖像")
            return
        
        file_path = filedialog.askopenfilename(
            title="選擇圖像檔案",
            filetypes=[("PNG檔案", "*.png"), ("所有檔案", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            import_image = Image.open(file_path)
            
            if (import_image.width != self.current_bitmap.width or 
                import_image.height != self.current_bitmap.height):
                messagebox.showerror("錯誤", "導入圖像的尺寸必須與當前幀一致")
                return
            
            # 保存到幀
            self.saf_info.save_bitmap_to_frame(import_image, self.current_frame_index)
            self.update_frame_display()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"導入圖像時發生錯誤：{str(e)}")
    
    def export_image(self):
        """導出圖像"""
        if not self.current_bitmap:
            messagebox.showwarning("警告", "沒有可導出的圖像")
            return

        file_path = filedialog.asksaveasfilename(
            title="保存圖像檔案",
            defaultextension=".png",
            filetypes=[("PNG檔案", "*.png"), ("所有檔案", "*.*")]
        )

        if not file_path:
            return

        try:
            # 應用統一大小設置
            processed_bitmap = self.resize_to_uniform_size(self.current_bitmap)
            processed_bitmap.save(file_path)
            messagebox.showinfo("成功", "圖像導出成功")
        except Exception as e:
            messagebox.showerror("錯誤", f"導出圖像時發生錯誤：{str(e)}")
    
    def batch_export(self):
        """批量導出"""
        if not self.saf_info:
            messagebox.showwarning("警告", "請先開啟SAF檔案")
            return

        folder_path = filedialog.askdirectory(title="選擇導出資料夾")
        if not folder_path:
            return

        try:
            exported_count = 0
            for i in range(self.saf_info.get_frame_count()):
                frame_bitmap = self.saf_info.get_frame_bitmap(i)
                if frame_bitmap:
                    # 後製處理：將黑色背景變為透明
                    processed_bitmap = self.make_black_transparent(frame_bitmap)
                    # 應用統一大小設置
                    final_bitmap = self.resize_to_uniform_size(processed_bitmap)
                    file_path = os.path.join(folder_path, f"frame_{i:04d}.png")
                    final_bitmap.save(file_path)
                    exported_count += 1

            size_info = ""
            if self.uniform_size_var.get():
                size_info = f" (統一大小: {self.detected_width}x{self.detected_height})"

            messagebox.showinfo("成功", f"批量導出完成，共導出 {exported_count} 幀{size_info}")
        except Exception as e:
            messagebox.showerror("錯誤", f"批量導出時發生錯誤：{str(e)}")
    
    def batch_import(self):
        """批量導入"""
        if not self.saf_info:
            messagebox.showwarning("警告", "請先開啟SAF檔案")
            return
        
        folder_path = filedialog.askdirectory(title="選擇導入資料夾")
        if not folder_path:
            return
        
        try:
            imported_count = 0
            for i in range(self.saf_info.get_frame_count()):
                file_path = os.path.join(folder_path, f"frame_{i:04d}.png")
                if os.path.exists(file_path):
                    import_image = Image.open(file_path)
                    self.saf_info.save_bitmap_to_frame(import_image, i)
                    imported_count += 1
            
            messagebox.showinfo("成功", f"批量導入完成，共導入 {imported_count} 幀")
            self.update_frame_display()
        except Exception as e:
            messagebox.showerror("錯誤", f"批量導入時發生錯誤：{str(e)}")
    
    def save_saf_file(self):
        """保存SAF檔案"""
        if not self.saf_info:
            messagebox.showwarning("警告", "沒有可保存的SAF檔案")
            return
        
        try:
            backup_file = self.saf_info.save_saf_to_file(False)
            if backup_file:
                messagebox.showinfo("成功", f"SAF檔案保存成功，備份檔案：{backup_file}")
            else:
                messagebox.showerror("錯誤", "保存SAF檔案失敗")
        except Exception as e:
            messagebox.showerror("錯誤", f"保存SAF檔案時發生錯誤：{str(e)}")
    
    def save_fb2_file(self):
        """保存FB2檔案"""
        if not self.fb2_info:
            messagebox.showwarning("警告", "沒有可保存的FB2檔案")
            return
        
        try:
            backup_file = self.fb2_info.save_fb2_to_file()
            if backup_file:
                messagebox.showinfo("成功", f"FB2檔案保存成功，備份檔案：{backup_file}")
            else:
                messagebox.showerror("錯誤", "保存FB2檔案失敗")
        except Exception as e:
            messagebox.showerror("錯誤", f"保存FB2檔案時發生錯誤：{str(e)}")
    
    def on_scale_changed(self, event):
        """縮放改變事件"""
        try:
            self.bitmap_scale = int(self.scale_var.get())
            if self.current_bitmap:
                self.display_image(self.current_bitmap)
        except ValueError:
            pass

    def export_fb2_map_image(self):
        """匯出FB2地圖圖片"""
        if not self.fb2_info:
            messagebox.showwarning("警告", "沒有已載入的FB2地圖")
            return
        try:
            map_bitmap = self.fb2_info.get_map_bitmap()
            if not map_bitmap:
                messagebox.showerror("錯誤", "無法取得地圖圖像")
                return
            file_path = filedialog.asksaveasfilename(
                title="儲存地圖圖片",
                defaultextension=".png",
                filetypes=[("PNG檔案", "*.png"), ("所有檔案", "*.*")]
            )
            if not file_path:
                return
            map_bitmap.save(file_path)
            messagebox.showinfo("成功", f"地圖圖片已成功匯出：{file_path}")
        except Exception as e:
            messagebox.showerror("錯誤", f"匯出地圖圖片時發生錯誤：{str(e)}")

    def export_saf_wave(self):
        """匯出 SAF 動畫音效檔案"""
        if not self.saf_info:
            messagebox.showwarning("警告", "沒有已載入的SAF檔案")
            return

        if not self.saf_info.wave_data:
            messagebox.showwarning("警告", "SAF檔案中沒有音效資料")
            return

        # 創建導出選項對話框
        try:
            dialog = tk.Toplevel()
            dialog.title("音效導出選項")
            dialog.geometry("400x350")
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中顯示
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

            # 標題
            title_label = tk.Label(dialog, text="請選擇音效導出方式：", font=("Arial", 12, "bold"))
            title_label.pack(pady=10)

            # 導出選項
            export_var = tk.StringVar(value="sequence")

            # 按播放順序混合導出
            sequence_frame = ttk.LabelFrame(dialog, text="按播放順序混合導出（推薦）")
            sequence_frame.pack(fill=tk.X, padx=20, pady=5)

            ttk.Radiobutton(sequence_frame, text="導出完整混合音頻",
                           variable=export_var, value="sequence").pack(anchor=tk.W, padx=10, pady=5)

            sequence_desc = tk.Label(sequence_frame,
                                   text="根據SAF幀序列的真正播放順序，\n將聲音按時間軸混合成完整音頻檔案",
                                   justify=tk.LEFT, fg="blue")
            sequence_desc.pack(anchor=tk.W, padx=20, pady=(0, 10))

            # 幀時長設置
            duration_frame = ttk.Frame(sequence_frame)
            duration_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

            ttk.Label(duration_frame, text="每幀時長 (毫秒):").pack(side=tk.LEFT)
            self.frame_duration_var = tk.StringVar(value="100")
            duration_entry = ttk.Entry(duration_frame, textvariable=self.frame_duration_var, width=8)
            duration_entry.pack(side=tk.LEFT, padx=5)
            ttk.Label(duration_frame, text="(建議: 50-200ms)").pack(side=tk.LEFT, padx=5)

            # 單個音效導出
            single_frame = ttk.LabelFrame(dialog, text="單個音效導出")
            single_frame.pack(fill=tk.X, padx=20, pady=5)

            ttk.Radiobutton(single_frame, text="導出單個音效檔案",
                           variable=export_var, value="single").pack(anchor=tk.W, padx=10, pady=5)

            single_desc = tk.Label(single_frame,
                                 text="選擇並導出SAF中的單個音效檔案\n（原始格式，未混合）",
                                 justify=tk.LEFT, fg="gray")
            single_desc.pack(anchor=tk.W, padx=20, pady=(0, 10))

            def export_sequence_audio():
                """導出按播放順序混合的音頻"""
                try:
                    frame_duration = int(self.frame_duration_var.get())
                    if frame_duration < 10 or frame_duration > 1000:
                        messagebox.showwarning("警告", "每幀時長應在10-1000毫秒之間")
                        return

                    file_path = filedialog.asksaveasfilename(
                        title="儲存混合音效檔案",
                        defaultextension=".wav",
                        filetypes=[("WAV音效檔案", "*.wav"), ("所有檔案", "*.*")]
                    )
                    if not file_path:
                        return

                    # 顯示進度
                    progress_dialog = tk.Toplevel(dialog)
                    progress_dialog.title("處理中...")
                    progress_dialog.geometry("300x100")
                    progress_dialog.transient(dialog)
                    progress_dialog.grab_set()

                    progress_label = tk.Label(progress_dialog, text="正在分析音頻播放順序...")
                    progress_label.pack(pady=20)

                    progress_dialog.update()

                    # 執行混合導出
                    result = self.saf_info.export_sequence_mixed_audio(file_path, frame_duration)

                    progress_dialog.destroy()
                    dialog.destroy()

                    # 顯示結果
                    info_text = f"混合音效已成功匯出：{file_path}\n\n"
                    info_text += f"總幀數: {result['total_frames']}\n"
                    info_text += f"總時長: {result['total_duration']:.2f} 秒\n"
                    info_text += f"格式: {result['channels']}聲道, {result['bits']}bit, {result['sample_rate']}Hz"

                    messagebox.showinfo("成功", info_text)

                except ValueError:
                    messagebox.showerror("錯誤", "請輸入有效的數字")
                except Exception as e:
                    if 'progress_dialog' in locals():
                        progress_dialog.destroy()
                    messagebox.showerror("錯誤", f"匯出混合音效時發生錯誤：{str(e)}")

            def export_single_audio():
                """導出單個音效檔案"""
                dialog.destroy()
                self._export_single_wave_dialog()

            def on_export():
                """根據選擇執行導出"""
                if export_var.get() == "sequence":
                    export_sequence_audio()
                else:
                    export_single_audio()

            def on_cancel():
                dialog.destroy()

            # 按鈕框架
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=20)

            tk.Button(button_frame, text="導出", command=on_export, width=10).pack(side=tk.LEFT, padx=10)
            tk.Button(button_frame, text="取消", command=on_cancel, width=10).pack(side=tk.LEFT, padx=10)

        except Exception as e:
            messagebox.showerror("錯誤", f"創建導出對話框時發生錯誤：{str(e)}")

    def _export_single_wave_dialog(self):
        """顯示單個音效選擇對話框"""
        try:
            # 創建選擇對話框
            dialog = tk.Toplevel()
            dialog.title("選擇要匯出的音效檔案")
            dialog.geometry("500x400")
            dialog.transient(self.root)
            dialog.grab_set()

            # 居中顯示
            dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

            tk.Label(dialog, text="請選擇要匯出的音效檔案：", font=("Arial", 12)).pack(pady=10)

            # 創建列表框和滾動條
            list_frame = ttk.Frame(dialog)
            list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

            listbox = tk.Listbox(list_frame, height=12, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)

            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 添加音效檔案選項（包含使用統計）
            usage_stats = self._get_audio_usage_stats()

            for i, wave in enumerate(self.saf_info.wave_data):
                try:
                    if wave.sample_rate > 0 and wave.channels > 0 and wave.bits > 0:
                        duration = wave.data_length / wave.channels / (wave.bits // 8) / wave.sample_rate
                    else:
                        duration = 0

                    usage_info = usage_stats.get(i, {'count': 0, 'frames': []})
                    usage_text = f"使用{usage_info['count']}次" if usage_info['count'] > 0 else "未使用"

                    item_text = f"音效 #{i}: {wave.channels}聲道 {wave.bits}bit {wave.sample_rate}Hz {duration:.3f}秒 ({usage_text})"
                    listbox.insert(tk.END, item_text)
                except:
                    listbox.insert(tk.END, f"音效 #{i}: 格式錯誤")

            if len(self.saf_info.wave_data) > 0:
                listbox.selection_set(0)  # 預設選擇第一個

            # 顯示使用說明
            info_label = tk.Label(dialog, text="提示：顯示每個音效的格式信息和在動畫中的使用次數",
                                fg="gray", font=("Arial", 9))
            info_label.pack(pady=5)

            def export_selected():
                if not self.saf_info:
                    messagebox.showwarning("警告", "沒有已載入的SAF檔案")
                    return
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("警告", "請選擇一個音效檔案")
                    return

                wave_index = selection[0]
                file_path = filedialog.asksaveasfilename(
                    title="儲存音效檔案",
                    defaultextension=".wav",
                    filetypes=[("WAV音效檔案", "*.wav"), ("所有檔案", "*.*")]
                )
                if not file_path:
                    return

                try:
                    self.saf_info.export_single_wave(wave_index, file_path)
                    messagebox.showinfo("成功", f"音效已成功匯出：{file_path}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("錯誤", f"匯出音效時發生錯誤：{str(e)}")

            def cancel():
                dialog.destroy()

            # 按鈕框架
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=15)

            tk.Button(button_frame, text="匯出選中音效", command=export_selected, width=12).pack(side=tk.LEFT, padx=10)
            tk.Button(button_frame, text="取消", command=cancel, width=12).pack(side=tk.LEFT, padx=10)

        except Exception as e:
            messagebox.showerror("錯誤", f"創建音效選擇對話框時發生錯誤：{str(e)}")

    def _get_audio_usage_stats(self):
        """獲取音效使用統計"""
        usage_stats = {}

        if not self.saf_info or not self.saf_info.frame_parameter:
            return usage_stats

        for i, fp in enumerate(self.saf_info.frame_parameter):
            wave_index = fp.wave_index
            if wave_index >= 0 and wave_index < len(self.saf_info.wave_data):
                if wave_index not in usage_stats:
                    usage_stats[wave_index] = {'count': 0, 'frames': []}
                usage_stats[wave_index]['count'] += 1
                usage_stats[wave_index]['frames'].append(i)

        return usage_stats

    def update_audio_info(self):
        """更新聲音信息顯示"""
        if not self.saf_info:
            self.audio_info_label.config(text="未載入聲音數據")
            return

        try:
            wave_count = len(self.saf_info.wave_data)
            if wave_count == 0:
                self.audio_info_label.config(text="此SAF檔案無聲音數據")
            else:
                # 計算總時長
                total_duration = 0
                for wave in self.saf_info.wave_data:
                    if wave.sample_rate > 0 and wave.channels > 0 and wave.bits > 0:
                        bytes_per_sample = wave.bits // 8
                        audio_data_size = wave.data_length
                        total_samples = audio_data_size // (wave.channels * bytes_per_sample)
                        duration = total_samples / wave.sample_rate
                        total_duration += duration

                self.audio_info_label.config(
                    text=f"聲音數量: {wave_count}\n總時長: {total_duration:.2f}秒"
                )
        except Exception as e:
            self.audio_info_label.config(text=f"聲音信息錯誤: {str(e)}")

    def update_current_frame_audio_info(self):
        """更新當前幀聲音信息"""
        if not self.saf_info or self.current_frame_index < 0:
            self.current_audio_label.config(text="")
            return

        try:
            if self.current_frame_index < len(self.saf_info.frame_parameter):
                frame_param = self.saf_info.frame_parameter[self.current_frame_index]
                wave_index = frame_param.wave_index

                if wave_index == -1:
                    audio_text = f"幀 {self.current_frame_index + 1}: 靜音"
                elif 0 <= wave_index < len(self.saf_info.wave_data):
                    wave = self.saf_info.wave_data[wave_index]
                    audio_text = f"幀 {self.current_frame_index + 1}: 聲音#{wave_index}\n"
                    audio_text += f"格式: {wave.channels}聲道 {wave.bits}bit {wave.sample_rate}Hz"
                else:
                    audio_text = f"幀 {self.current_frame_index + 1}: 無效聲音索引#{wave_index}"

                self.current_audio_label.config(text=audio_text)
            else:
                self.current_audio_label.config(text="")
        except Exception as e:
            self.current_audio_label.config(text=f"聲音信息錯誤: {str(e)}")

    def analyze_audio_sequence(self):
        """分析聲音播放順序"""
        if not self.saf_info:
            messagebox.showwarning("警告", "請先載入SAF檔案")
            return

        try:
            # 創建新窗口顯示分析結果
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("聲音播放順序分析")
            analysis_window.geometry("800x600")

            # 創建文本顯示區域
            text_frame = ttk.Frame(analysis_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 分析聲音播放順序
            analysis_text = self._generate_audio_sequence_analysis()
            text_widget.insert(tk.END, analysis_text)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("錯誤", f"分析聲音播放順序時發生錯誤：{str(e)}")

    def show_audio_statistics(self):
        """顯示聲音使用統計"""
        if not self.saf_info:
            messagebox.showwarning("警告", "請先載入SAF檔案")
            return

        try:
            # 創建新窗口顯示統計結果
            stats_window = tk.Toplevel(self.root)
            stats_window.title("聲音使用統計")
            stats_window.geometry("600x500")

            # 創建文本顯示區域
            text_frame = ttk.Frame(stats_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 生成統計信息
            stats_text = self._generate_audio_statistics()
            text_widget.insert(tk.END, stats_text)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("錯誤", f"生成聲音統計時發生錯誤：{str(e)}")

    def _generate_audio_sequence_analysis(self):
        """生成聲音播放順序分析報告"""
        if not self.saf_info:
            return "無SAF數據"

        report = []
        report.append("=== SAF聲音播放順序分析 ===\n")
        report.append(f"檔案: {self.current_file_name}\n")
        report.append(f"總幀數: {len(self.saf_info.frame_parameter)}")
        report.append(f"聲音數量: {len(self.saf_info.wave_data)}\n")

        # 聲音數據信息
        report.append("--- 聲音數據信息 ---")
        for i, wave in enumerate(self.saf_info.wave_data):
            duration = 0
            if wave.sample_rate > 0 and wave.channels > 0 and wave.bits > 0:
                bytes_per_sample = wave.bits // 8
                total_samples = wave.data_length // (wave.channels * bytes_per_sample)
                duration = total_samples / wave.sample_rate

            report.append(f"聲音 #{i}: {wave.channels}聲道, {wave.bits}bit, {wave.sample_rate}Hz, {duration:.3f}秒")

        report.append("\n--- 播放順序分析 ---")

        # 分析播放順序
        current_audio = None
        audio_changes = []

        for i, fp in enumerate(self.saf_info.frame_parameter):
            wave_index = fp.wave_index

            # 檢測聲音變化
            if wave_index != current_audio:
                audio_changes.append({
                    'frame': i,
                    'from': current_audio,
                    'to': wave_index
                })
                current_audio = wave_index

        # 顯示聲音切換點
        report.append("聲音切換點:")
        for change in audio_changes:
            frame = change['frame']
            from_audio = change['from']
            to_audio = change['to']

            if from_audio is None:
                if to_audio == -1:
                    report.append(f"  幀 {frame}: 開始靜音")
                else:
                    report.append(f"  幀 {frame}: 開始播放聲音 #{to_audio}")
            elif to_audio == -1:
                report.append(f"  幀 {frame}: 停止聲音 #{from_audio}")
            else:
                report.append(f"  幀 {frame}: 聲音切換 #{from_audio} → #{to_audio}")

        # 顯示完整播放序列（前50幀）
        report.append(f"\n播放序列 (前50幀):")
        for i in range(min(50, len(self.saf_info.frame_parameter))):
            fp = self.saf_info.frame_parameter[i]
            wave_index = fp.wave_index

            if wave_index == -1:
                report.append(f"  幀 {i:3d}: 靜音")
            elif 0 <= wave_index < len(self.saf_info.wave_data):
                report.append(f"  幀 {i:3d}: 播放聲音 #{wave_index}")
            else:
                report.append(f"  幀 {i:3d}: 無效索引 #{wave_index}")

        if len(self.saf_info.frame_parameter) > 50:
            report.append(f"  ... (還有 {len(self.saf_info.frame_parameter) - 50} 幀)")

        return "\n".join(report)

    def _generate_audio_statistics(self):
        """生成聲音使用統計報告"""
        if not self.saf_info:
            return "無SAF數據"

        report = []
        report.append("=== SAF聲音使用統計 ===\n")
        report.append(f"檔案: {self.current_file_name}\n")

        # 統計每個聲音的使用情況
        usage_stats = {}
        for i, fp in enumerate(self.saf_info.frame_parameter):
            wave_index = fp.wave_index

            if wave_index not in usage_stats:
                usage_stats[wave_index] = {
                    'count': 0,
                    'frames': []
                }

            usage_stats[wave_index]['count'] += 1
            usage_stats[wave_index]['frames'].append(i)

        # 顯示統計結果
        report.append("--- 聲音使用統計 ---")
        for wave_index in sorted(usage_stats.keys()):
            stats = usage_stats[wave_index]
            frames = stats['frames']
            count = stats['count']

            if wave_index == -1:
                report.append(f"靜音幀:")
            elif 0 <= wave_index < len(self.saf_info.wave_data):
                report.append(f"聲音 #{wave_index}:")
            else:
                report.append(f"無效聲音 #{wave_index}:")

            report.append(f"  使用次數: {count} 幀")
            report.append(f"  使用率: {count/len(self.saf_info.frame_parameter)*100:.1f}%")

            # 顯示使用的幀（限制顯示數量）
            if len(frames) <= 20:
                report.append(f"  使用幀: {frames}")
            else:
                report.append(f"  使用幀: {frames[:10]} ... {frames[-10:]} (共{len(frames)}幀)")

            # 分析使用模式
            if len(frames) > 1:
                gaps = [frames[i+1] - frames[i] for i in range(len(frames)-1)]
                if len(set(gaps)) == 1 and gaps[0] > 1:
                    report.append(f"  模式: 循環播放 (每 {gaps[0]} 幀重複)")
                elif all(gap == 1 for gap in gaps):
                    report.append(f"  模式: 連續播放 ({len(frames)} 幀)")
                else:
                    unique_gaps = list(set(gaps))
                    if len(unique_gaps) <= 5:
                        report.append(f"  模式: 不規則 (間隔: {unique_gaps})")
                    else:
                        report.append(f"  模式: 複雜不規則")

            report.append("")

        # 總結
        used_audio = [idx for idx in usage_stats.keys()
                     if idx >= 0 and idx < len(self.saf_info.wave_data)]
        unused_audio = [i for i in range(len(self.saf_info.wave_data))
                       if i not in used_audio]

        report.append("--- 總結 ---")
        report.append(f"使用的聲音: {sorted(used_audio)}")
        if unused_audio:
            report.append(f"未使用的聲音: {sorted(unused_audio)}")

        silent_frames = usage_stats.get(-1, {'count': 0})['count']
        report.append(f"靜音幀數: {silent_frames}")
        report.append(f"有聲音幀數: {len(self.saf_info.frame_parameter) - silent_frames}")

        return "\n".join(report)

def main():
    """主函數"""
    root = tk.Tk()
    app = SAFEditorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 