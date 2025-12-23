from tkinter import filedialog, messagebox
import tkinter as tk
import os
import mimetypes

def detect_file_type(file_path):
    """檢測檔案類型"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('text/'):
            return 'text'
    return 'binary'

def convert_to_binary():
    # 建立主視窗但不顯示
    root = tk.Tk()
    root.withdraw()

    # 開啟檔案選擇對話框
    input_file = filedialog.askopenfilename(
        title='選擇要轉換的檔案',
        filetypes=[
            ('文字檔案', '*.txt *.csv *.log'),
            ('圖片檔案', '*.jpg *.jpeg *.png *.bmp'),
            ('所有檔案', '*.*')
        ]
    )
    
    if input_file:  # 如果使用者有選擇檔案
        # 取得輸入檔案的目錄和檔名（不含副檔名）
        input_dir = os.path.dirname(input_file)
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # 建立輸出檔案的完整路徑
        output_file = os.path.join(os.curdir, f'{base_name}.bin')
        
        try:
            file_type = detect_file_type(input_file)
            
            if file_type == 'text':
                # 文字檔案處理：先讀取文字，再轉換為二進位
                try:
                    # 嘗試用 UTF-8 讀取
                    with open(input_file, 'r', encoding='utf-8') as text_file:
                        text_data = text_file.read()
                except UnicodeDecodeError:
                    # 如果 UTF-8 失敗，嘗試其他編碼
                    try:
                        with open(input_file, 'r', encoding='big5') as text_file:
                            text_data = text_file.read()
                    except UnicodeDecodeError:
                        # 如果都失敗，直接以二進位模式讀取
                        with open(input_file, 'rb') as binary_file:
                            data = binary_file.read()
                    else:
                        data = text_data.encode('utf-8')  # 將文字轉換為 UTF-8 二進位
                else:
                    data = text_data.encode('utf-8')  # 將文字轉換為 UTF-8 二進位
            else:
                # 圖片或其他二進位檔案直接讀取
                with open(input_file, 'rb') as binary_file:
                    data = binary_file.read()
                
            # 寫入二進位檔案
            with open(output_file, 'wb') as bin_file:
                bin_file.write(data)
                
            messagebox.showinfo('轉換成功', 
                f'檔案已成功轉換！\n\n'
                f'輸入檔案：{input_file}\n'
                f'輸出檔案：{output_file}\n'
                f'檔案類型：{file_type}')
                
        except Exception as e:
            messagebox.showerror('錯誤', f'轉換過程發生錯誤：\n{str(e)}')
    else:
        print('未選擇檔案，程式結束')

if __name__ == "__main__":
    convert_to_binary()
