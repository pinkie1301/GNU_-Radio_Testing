"""
Embedded Python Block: File Source to Tagged Stream
"""

import numpy as np
from gnuradio import gr
import time
import pmt
import os.path
import sys
import base64

"""
State definitions
    0   idle
    1   send preamble
    2   send file data
    3   send file name
    4   send post filler
"""

class blk(gr.sync_block):
    def __init__(self, FileName='None', Pkt_len=52):
        gr.sync_block.__init__(
            self,
            name='EPB: File Source to Tagged Stream',
            in_sig=None,
            out_sig=[np.uint8])
        
        
        self.FileName = FileName
        self.Pkt_len = Pkt_len
        self.state = 0      # idle state
        self.pre_count = 0
        self.indx = 0
        self._debug = 0     # debug
        self.data = ""

        if (os.path.exists(self.FileName)):
            # open input file
            self.f_in = open (self.FileName, 'rb')
            self._eof = False
            if (self._debug):
                print ("[EPB encode] File name:", self.FileName)
            self.state = 1
        else:
            print('[EPB encode] ', self.FileName, 'does not exist')
            self._eof = True
            self.state = 0

        # 交替的 pattern，確保 QPSK 星座圖有對角線跳變
        # 37 是 '%', 93 是 ']' 保持不變作為邊界
        # 中間填充 200 個位元組的交替數據
        pattern = [255, 0, 255, 0, 240, 15, 240, 15] * 25  # 混合 pattern
        
        self.char_list = [37] + pattern + [93]
        self.c_len = len (self.char_list)
        print ("[EPB encode] c_len: ", self.c_len)
        self.filler = [37,85,85,85, 35,69,79,70, 85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,85,85,85,85,85,85,85,85,85,85,85,85,85, 85,85,85,93]
        self.f_len = len (self.filler)

    def forecast(self, noutput_items, ninput_items_required):
        # 告訴 scheduler 我們需要至少 512 bytes 的輸出空間
        noutput_items = max(512, noutput_items)
        
    def work(self, input_items, output_items):

        if (self.state == 0):
            # idle
            return (0)

        elif (self.state == 1):
            # send preamble
            if (self._debug):
                print ("[EPB encode] state = 1", self.pre_count)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.c_len)
            self.add_item_tag(0, # Write to output port 0
                self.indx,   # Index of the tag
                key1,   # Key of the tag
                val1    # Value of the tag
                )
            self.indx += self.c_len
            i = 0
            while (i < self.c_len):
                output_items[0][i] = self.char_list[i]
                i += 1
            self.pre_count += 1
            if (self.pre_count > 128):
                self.pre_count = 0
                self.state = 2      # send msg
            return (self.c_len)

        elif (self.state == 2):
            while (not (self._eof)):
                buff = self.f_in.read (self.Pkt_len)
                b_len = len(buff)
                if b_len == 0:
                    print ('[EPB encode] End of file')
                    self._eof = True
                    self.f_in.close()
                    self.state = 3      # send file name
                    self.pre_count = 0
                    break
                # convert to Base64
                encoded = base64.b64encode (buff)
                e_len = len(encoded)
                if (self._debug):
                    print ('[EPB encode] b64 length =', e_len)
                key0 = pmt.intern("packet_len")
                val0 = pmt.from_long(e_len)
                self.add_item_tag(0, # Write to output port 0
                    self.indx,   # Index of the tag
                    key0,   # Key of the tag
                    val0    # Value of the tag
                    )
                self.indx += e_len
                i = 0
                while (i < e_len):
                    output_items[0][i] = encoded[i]
                    i += 1
                return (e_len)

        elif (self.state == 3):
            # send file name
            fn_len = len (self.FileName)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(fn_len+8)
            self.add_item_tag(0, # Write to output port 0
                self.indx,   # Index of the tag
                key1,   # Key of the tag
                val1    # Value of the tag
                )
            self.indx += (fn_len+8)
            i = 0
            while (i < 8):
                output_items[0][i] = self.filler[i]
                i += 1
            j = 0
            while (i < (fn_len+8)):
                output_items[0][i] = ord(self.FileName[j])
                i += 1
                j += 1
            self.state = 4
            return (fn_len+8)

        elif (self.state == 4):
            # send post filler
            if (self._debug):
                print ("[EPB encode] state = 4", self.pre_count)
            key1 = pmt.intern("packet_len")
            val1 = pmt.from_long(self.f_len)
            self.add_item_tag(0, # Write to output port 0
                self.indx,   # Index of the tag
                key1,   # Key of the tag
                val1    # Value of the tag
                )
            self.indx += self.f_len
            i = 0
            while (i < self.f_len):
                output_items[0][i] = self.filler[i]
                i += 1
            self.pre_count += 1
            if (self.pre_count > 16):
                self.pre_count = 0
                self.state = 0      # idle
            return (self.f_len)

        return (0)


