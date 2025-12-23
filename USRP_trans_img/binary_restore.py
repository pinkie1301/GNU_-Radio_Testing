from tkinter import filedialog, messagebox
import tkinter as tk
import os
import mimetypes

def detect_file_type(data):
    """嘗試偵測二進位資料的檔案類型"""
    # 檢查圖片檔案的特徵碼
    image_signatures = {
        b'\xFF\xD8\xFF': '.jpg',  # JPEG
        b'\x89PNG\r\n\x1a\n': '.png',  # PNG
        b'BM': '.bmp',  # BMP
        b'GIF87a': '.gif',  # GIF
        b'GIF89a': '.gif'  # GIF
    }

    # 檢查檔案特徵碼
    for signature, ext in image_signatures.items():
        if data.startswith(signature):
            return ext

    # 嘗試檢測是否為文字檔案
    try:
        data[:1000].decode('utf-8')  # 嘗試解碼前1000個字節
        return '.txt'
    except UnicodeDecodeError:
        pass

    # 如果無法確定類型，預設為二進位檔案
    return '.bin'

def convert_from_binary():
    # 建立主視窗但不顯示
    root = tk.Tk()
    root.withdraw()

    # 開啟檔案選擇對話框
    input_file = filedialog.askopenfilename(
        title='選擇要還原的二進位檔案',
        filetypes=[
            ('二進位檔案', '*.bin'),
            ('所有檔案', '*.*')
        ]
    )
    
    if input_file:  # 如果使用者有選擇檔案
        try:
            # 讀取二進位檔案
            with open(input_file, 'rb') as bin_file:
                data = bin_file.read()

            # 取得檔案的基本名稱（不含副檔名）
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            
            # 偵測檔案類型並決定輸出副檔名
            ext = detect_file_type(data)
            
            # 建立輸出檔案的完整路徑
            output_file = os.path.join(os.curdir, f'{base_name}_restored{ext}')

            # 儲存檔案
            with open(output_file, 'wb') as out_file:
                out_file.write(data)

            messagebox.showinfo('還原成功', 
                f'檔案已成功還原！\n\n'
                f'輸入檔案：{input_file}\n'
                f'輸出檔案：{output_file}\n'
                f'偵測到的檔案類型：{ext}')

        except Exception as e:
            messagebox.showerror('錯誤', f'還原過程發生錯誤：\n{str(e)}')
    else:
        print('未選擇檔案，程式結束')

if __name__ == "__main__":
    convert_from_binary()
