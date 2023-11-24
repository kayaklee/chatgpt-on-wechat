# encoding:utf-8

import time
import random
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import traceback

#布局规划
##################################################
a4_width, a4_height = A4
total_x_start = 12*mm
total_x_end = a4_width - 12 * mm
total_y_start = a4_height - 20 * mm
total_y_end = 20 * mm

eng_cell_height = 3*3*mm
cn_cell_height = 12*mm
cell_cnt_per_line = 5
cell_height = eng_cell_height+cn_cell_height
cell_width = (total_x_end-total_x_start)/cell_cnt_per_line
lineN = int((total_y_start-total_y_end)/cell_height)

def get_cn_pos_of_cell(cell_num, output_width, output_height):
    row = (int)(cell_num / cell_cnt_per_line)
    col = cell_num % cell_cnt_per_line
    cell_x = total_x_start + cell_width * col
    cell_y = total_y_start - eng_cell_height - cell_height * row
    print_x = cell_x + (cell_width/2 - output_width/2)
    print_y = cell_y - (cell_height/2 - output_height/2)
    #print("row={} col={} x={} y={}".format(row, col, print_x, print_y))
    return print_x, print_y
##################################################

def DrawPDF(word_file, output_dir, spec_latest_unit, unit_filter = []):
    try:
        # 从文本文件中读取所有单词的中文和英文
        with open(word_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        total_words = [line.strip().split(",") for line in lines]
        words = []
        if spec_latest_unit and 0 <= len(total_words):
            unit = total_words[-1][0]
            for w in total_words:
                if w[0] == unit and w[1] == 'key':
                    words.append(w)
        elif unit_filter[0] == '所有单元':
            for w in total_words:
                words.append(w)
        else:
            unit_filter_dict = {}
            for u in unit_filter:
                unit_filter_dict[u] = None
            for w in total_words:
                if w[0] in unit_filter_dict and w[1] == 'key':
                    words.append(w)

        time_string = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
        output_file_path = output_dir + "/" + time_string + ".pdf"
        c = canvas.Canvas(output_file_path, pagesize=A4)

        # 画英文四线三格
        ##################################################
        c.setLineWidth(0.2)
        
        wline_x_start = total_x_start
        wline_x_end = total_x_end
        wline_y = total_y_start
        for i in range(lineN):
            c.line(wline_x_start, wline_y, wline_x_end, wline_y); wline_y -= eng_cell_height/3
            c.line(wline_x_start, wline_y, wline_x_end, wline_y); wline_y -= eng_cell_height/3
            c.line(wline_x_start, wline_y, wline_x_end, wline_y); wline_y -= eng_cell_height/3
            c.line(wline_x_start, wline_y, wline_x_end, wline_y); wline_y -= cn_cell_height
        
        hline_y_start = total_y_start
        hline_y_end = total_y_end
        hline_x = total_x_start + cell_width
        c.line(hline_x, hline_y_start, hline_x, hline_y_end); hline_x += cell_width
        c.line(hline_x, hline_y_start, hline_x, hline_y_end); hline_x += cell_width
        c.line(hline_x, hline_y_start, hline_x, hline_y_end); hline_x += cell_width
        c.line(hline_x, hline_y_start, hline_x, hline_y_end)
        ##################################################
        
        font = 'SimSun'
        size = 12
        pdfmetrics.registerFont(TTFont(font, './SimSun.ttf'))
        c.setFont(font, size)
        font_height = pdfmetrics.getAscent(font, size) - pdfmetrics.getDescent(font, size)
        
        #Page1
        current_words = random.sample(words, min(50, len(words)))
        unit_dict = {}
        for i,word in enumerate(current_words):
            unit = word[0]
            word_type = word[1]
            eng = word[2]
            cn = word[3].encode('utf-8')
            cn_width = pdfmetrics.stringWidth(cn, fontName=font, fontSize=size)
            #print("cn_height={} cn_width={}".format(font_height, cn_width))
            x, y = get_cn_pos_of_cell(i, cn_width, font_height) 
            c.drawString(x, y+2*mm, cn)
            unit_dict[unit] = None
        
        #Page1 页面头
        unit_list = []
        for u in unit_dict:
            unit_list.append(u)
        unit_list.sort()
        c.setFont(font, size*0.75)
        unit_string = time_string + " 包含单元："
        for u in unit_list:
            unit_string += (u+" ")
        c.drawString(total_x_start, total_y_start + 10*mm, unit_string.encode('utf-8'))
        
        #Page2
        c.showPage()
        c.setFont(font, size)
        #current_words.sort(key=lambda x: x[0])
        word_print_y = total_y_start
        for i in range(0, len(current_words), 2):
            w = current_words[i]
            word2print = "{}  {}\t{}".format(w[0],w[3],w[2]).encode('utf-8')
            c.drawString(total_x_start, word_print_y, word2print)
            if (i < (len(current_words) - 1)):
                w = current_words[i+1]
                word2print = "{}  {}\t{}".format(w[0],w[3],w[2]).encode('utf-8')
                c.drawString(total_x_start + (total_x_end-total_x_start)/2, word_print_y, word2print)
            word_print_y -= (font_height-1*mm)
            c.line(total_x_start, word_print_y, total_x_end, word_print_y)
            word_print_y -= (6*mm)
        
        #Save PDF
        c.save()
        return None, output_file_path
    except Exception as e:
        return "exception: {} {}".format(e, traceback.format_exc()), None

#output_file_path = DrawPDF("alvin_words", "./", False, ['U8L1', 'U7L1', 'U7L2'])
#print("Output:{}".format(output_file_path))
