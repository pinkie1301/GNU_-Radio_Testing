"""
Embedded Python Block: One-Second Logger
功能：接收 Float dB 值，每收到一筆數據就寫入一行 Log，包含時間戳記。
"""

import numpy as np
from gnuradio import gr
import time
import datetime

class blk(gr.sync_block):  
    def __init__(self, filename='noise_log.csv'):  
        gr.sync_block.__init__(
            self,
            name='1-Sec dB Logger',   
            in_sig=[np.float32], # 接收 Float
            out_sig=None
        )
        self.filename = filename
        self.file = None

    def start(self):
        # 改為 'w' 模式：每次啟動都會清空舊檔
        self.file = open(self.filename, 'w', buffering=1) 
        
        # 直接寫入標頭，不需要判斷檔案是否為空
        self.file.write("Timestamp_ISO,Unix_Time,iss_dbm\n")
        return True


    def stop(self):
        if self.file:
            self.file.close()
        return True

    def work(self, input_items, output_items):
        in0 = input_items[0]
        
        # 由於前端已經做了 Keep 1 in N，這裡進來的資料量會非常少 (通常只有 1 點)
        if len(in0) > 0:
            now = time.time()
            iso_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for val in in0:
                # 格式：YYYY-MM-DD HH:MM:SS, UnixTimeStamp, dB
                log_line = f"{iso_time},{now:.3f},{val:.3f}\n"
                self.file.write(log_line)
                
            # 強制將資料寫入硬碟，避免卡在記憶體
            self.file.flush()
            
        return len(in0)
