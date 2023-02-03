# -*- coding: utf-8 -*-

# TODO:
# 1. Figures and Tables not extracted
# 2. Flags are too aggressive in whole paragraphs
"""
PDF document reader.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextLine, LTTextBox, LTChar, LTAnno, LTTextLineHorizontal
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from collections import Counter, OrderedDict
import re
import numpy as np


class Reader:
    """Reader that reads in PDF files"""

    def __init__(self, showPublisher=None):
        """
        :param publishers: Publisher identifiers used to detect publisher
        :param bool publisher_state: Weather publisher is found. Default False
        :param showPublisher: A flag to control if the name of the publisher is showed
        :param universal_sequence: Sequence number assigned to each text block to show its location on Document level
        """
        self.publishers = ['elsevier', 'rsc.', 'acs', 'chem. eur. j', 'wiley-vch ', 'angewandte', 'springer']
        self.publisher_state = False
        self.showPublisher = showPublisher
        self.universal_sequence = 0

    def detect(self, fstring, fname=None):
        """Detect if file passed into the pipeline is a pdf file"""
        if fname and not fname.endswith('.pdf'):
            return False
        return True

    def font_name_size(self, current_lt_obj):
        """
        Font analysis of each text block

        :param current_lt_obj: # The pdfminer.layout.object
        :param fonts_size: A list that stores the font sizes of each character
        :param fonts_name: A list that stores the font names of each character
        :param text: A list that stores each character
        :param final: A list that stores characters that have the largest font sizes in a text block
        """

        fonts_size, fonts_name, text, final = [], [], [], []

        # for page_layout in extract_pages("test.pdf"):
        #     for element in page_layout:
        #         if isinstance(element, LTTextContainer):
        #             for text_line in element:
        #                 for character in text_line:
        #                     if isinstance(character, LTChar):
        #                         print(character.fontname)
        #                         print(character.size)

        # for o in current_lt_obj._objs:
        #     if o.get_text().strip():  # Check if the current text block is empty
        #         for char in o._objs:  # For each characters in the text block
        #             if isinstance(char, LTChar):
        #                 if char.size != 0:
        #                     fonts_size.append(char.size)
        #                     fonts_name.append(char.fontname)
        #                     text.append(char.get_text())
        #
        #             elif isinstance(char, LTAnno):
        #                 fonts_size.append(-100)  # Just to occupy a space
        #                 text.append(char.get_text())

        for o in current_lt_obj:
            if isinstance(o, LTTextLineHorizontal):
                if o.get_text().strip():  # Check if the current text block is empty
                    for char in o._objs:  # For each characters in the text block
                        if isinstance(char, LTChar):
                            if char.size != 0:
                                fonts_size.append(char.size)
                                fonts_name.append(char.fontname)
                                text.append(char.get_text())

                        elif isinstance(char, LTAnno):
                            fonts_size.append(-100)  # Just to occupy a space
                            text.append(char.get_text())
            elif isinstance(o, LTChar):
                pass
        # Replace -100 to max font size
        fonts_size = [max(fonts_size) if x == -100 else x for x in fonts_size]

        # Add characters to the list
        for i in [index for index, value in enumerate(fonts_size) if value == max(fonts_size)]:
            final.append(text[i])

        if fonts_size:
            return {'font_size_max': max(fonts_size),
                    'font_size_min': min(fonts_size),
                    'font_size_ave': sum(fonts_size) / float(len(fonts_size)),
                    'font_name_most': Counter(fonts_name).most_common(),
                    'max_out_of_mixed': ''.join(final).replace('\n', ' ').strip()
                    }

    def detect_publisher(self, input_text):
        """Detect the publisher of the input file"""
        for publisher in self.publishers:
            if publisher in input_text.lower():
                if self.showPublisher == True:
                    print('Publisher: ***', publisher, '***')
                self.publisher_state = True
                self.publishers = self.publishers[self.publishers.index(publisher)]
                return
            else:
                continue
        return

    def span_across(self, textblock):
        return

    def single_page_layout(self, layout, page_seq, page_x, page_y):
        """
        Process an LTPage layout and return a list of elements

        :param layout: device.get_result() returned by PDFMiner
        :param page_seq: Current page number
        :param page_x: Middle point of current page on the x axis
        :param page_y: Middle point of current page on the y axis
        :param dic_page: A dictionary that stores the results, keys are page number and textblock number; Values are features generated at this step
        """

        print("Page Number", page_seq)
        dic_page = {}

        for lt_obj_seq, lt_obj in enumerate(layout):
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):

                
                #print(lt_obj.get_text())

                if not self.publisher_state:
                    if page_seq == 0:
                        self.detect_publisher(lt_obj.get_text())  # Pass current text to function
                    else:
                        pass

                x0, y0 = lt_obj.bbox[0], lt_obj.bbox[1]  # Coordinates of bottom left point
                x1, y1 = lt_obj.bbox[2], lt_obj.bbox[3]  # Coordinates of top right point
                horizontal = abs((x1 - x0))
                vertical = abs((y1 - y0))
                area = horizontal * vertical
                self.universal_sequence += 1

                dic_page[int(page_seq), int(lt_obj_seq)] = {  # i -> page_number, j-> obj_number on each page
                    'position_x': (x0, y0),  # Coordinates of bottom left point
                    'position_y': (x1, y1),  # Coordinates of top right point
                    'text': str(lt_obj.get_text().rstrip('\n')),  # Plain text of the current object
                    'horizontal': horizontal,  # Horizontal length
                    'vertical': vertical,  # Vertical length
                    'area': area,  # Area of current object
                    'sequence': (page_seq, lt_obj_seq),  # Page number and current object number
                    'universal_sequence': self.universal_sequence,# Universal sequence number across the whole PDF dcocument
                    'font': self.font_name_size(lt_obj),  # Font analysis of text block
                    'number_of_char': len(lt_obj.get_text().rstrip('\n')),  # Number of characters in the text block
                    'number_of_word': len(lt_obj.get_text().replace('\n', '').split(' ')),# Number of words in the text block
                    'obj_mid': ((x0 + x1) / 2),  # Centre point of text block
                    'page_x': page_x,  # Middle point of current page on the x axis
                    'page_y': page_y,  # Middle point of current page on the y axis
                    'publisher': self.publishers
                }
            else:
                pass

        return dic_page

    def PDFsetup(self):
        dic = {}
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        return device, interpreter, dic

    def dic_sorting(self, dic_unsorted):
        return OrderedDict(sorted(dic_unsorted.items()))

    def extract_title(self, dict):
        """Extract title from the input file"""
        # Extract text from the first page
        font_size_max = 0
        title = None
        title_key = None
        for key, value in dict.items():            
            if key[0] != 0:
                break
            if len(value['text']) > 4 and value['font'] != None:
                if value['font']['font_size_max'] > font_size_max:
                    title = value['text'].replace('\n', ' ').strip()
                    title_key = key
                    font_size_max = value['font']['font_size_max']
        return title, title_key

    def find_start_and_end(self, dic):
        """Find the start and end of the PDF"""
        start_strings = ['Abstract:', 'Introduction:', 'Title:']
        end_strings = ['Reference', 'References', 'Acknowledgement', 'Acknowledgements']

        # Find the beginning and end of the PDF
        start_keys = []
        start_text = []
        end_keys = []
        end_text = []
        start_key = None
        end_key = None
        for key,value in dic.items():
            for start in start_strings:
                if re.search(start, value['text']):
                    start_keys.append(key)
                    start_text.append(value['text'])
            for end in end_strings:
                if re.search(end, value['text'], re.IGNORECASE):
                    end_keys.append(key)
                    end_text.append(value['text'])

        if start_keys != []:
            start_key = min(start_keys)
            if start_key[0] != 0:
                start_key = None
        if end_keys != []:
            end_key = max(end_keys)
        return start_key, end_key

    def extract_header(self, dic):
        # Extract font size and content of header
        header = []
        header_font = []

        for key, value in dic.items():
            if key[1] == 0:
                header.append(value['text'])
                header_font.append(value['font']['font_size_max'])
        for font in header_font:
            if font == None:
                header_font.remove(font)
        # font = max(set(header_font), key = header_font.count)
        # median_font = np.median(np.array(header_font))
        return header

    def extract_font_size(self, dic):
        """Extract font size from the input file"""
        font_size = []
        for key, value in dic.items():
            if value['font'] != None:
                font_size.append(value['font']['font_size_max'])
        font = max(set(font_size), key = font_size.count)
        return font

    def remove_figures(self, dic):
        """Remove figures from the input file"""
        flags = ['Figure', 'Table', 'figure', 'table', 'image', 'fig.', 'tab.']
        # Remove figures
        keys = []
        for key, value in dic.items():
            for flag in flags:
                if re.search(flag, value['text']):
                    keys.append(key)
                    break
        new_dic = {k: v for k, v in dic.items() if k not in keys}
        return new_dic

    def extract_body(self, dic, flags):
        """Extract body text from PDF"""
        print("Extracting body text")

        # Extract Title
        title, title_key = self.extract_title(dic)
        flags.append(title)
        print('Title: ', title)

        # Find the beginning and end of the PDF
        start, end = self.find_start_and_end(dic)
    
        # Filter out irrelevant text
        if start != None and end != None:
            dic = {k: v for k, v in dic.items() if (k[0] > start[0] and k[0] < end[0] or k[0] == start[0] and k[1] >= start[1] or k[0] == end[0] and k[1] < end[1])}
        elif start != None:
            dic = {k: v for k, v in dic.items() if (k[0] > start[0] or k[0] == start[0] and k[1] >= start[1])}
        elif end != None:
            dic = {k: v for k, v in dic.items() if (k[0] < end[0] or k[0] == end[0] and k[1] < end[1])}
        elif title_key != None:
            dic = {k: v for k, v in dic.items() if (k[0] > title_key[0] or k[0] == title_key[0] and k[1] > title_key[1])}
        else:
            pass

        # dic = self.remove_figures(dic)

        # Extract font size and content of header
        header = self.extract_header(dic)

        # Find most common font size
        body_font_size = self.extract_font_size(dic)

        # Extracts relevant text from the PDF
        raw_body = []
        it = 0
        for key, value in dic.items():
            it += 1
            value['text'] = value['text'].replace('-\n', '').strip()
            value['text'] = value['text'].replace('\n', ' ')
            value['text'] = value['text'].replace('  ', ' ')

            if (len(value['text']) > 4 and 7 <= value['font']['font_size_ave'] and value['text'][0].isdigit() == False and value['text'][1].isdigit() == False):
                raw_body.append(value['text'])

        # Remove repeted text
        items = set(raw_body)
        for item in items:
            if raw_body.count(item) > 1:
                flags.append(item)
                for i in range(raw_body.count(item)-1):
                    raw_body.remove(item)

        # Removes citations in ( ) and [ ] and remove flags
        for i in range(len(raw_body)):
            for flag in flags:
                raw_body[i] = re.sub(flag, '', raw_body[i])
            # Remove citations
            raw_body[i] = re.sub(r' [\(\[][^\(\[]*[0-9][0-9][0-9][0-9][^\(\[]*[\)\]]', '', raw_body[i])

            # Remove URLs, emails
            raw_body[i] = re.sub(r'(www|http:|https:)+[^\s]+[\w]', '', raw_body[i])
            raw_body[i] = re.sub(r'[^\s]+(\.com|\.ch|\.de)+[^\s]+[\w]', '', raw_body[i])
            raw_body[i] = re.sub(r'[^\s]+[A-Z|0-9][\/][A-Z|0-9]+[^\s]+[\w]', '', raw_body[i])
            raw_body[i] = re.sub(r'[^\s]+[\/]+[^\s]+[\/]+[^\s]+[\w]', '', raw_body[i])
            raw_body[i] = re.sub(r'[^\s]+@+[^\s]+[\w]', '', raw_body[i])

            # Remove special characters
            raw_body[i] = re.sub(r' (\W) ', ' ', raw_body[i])
            raw_body[i] = re.sub(r'[\(\[][.]{3}[\)\]]', '', raw_body[i])
            raw_body[i] = re.sub(r'[.]{3}', '', raw_body[i])
            raw_body[i] = re.sub(r'[\(\[][…][\)\]]', '', raw_body[i])
            raw_body[i] = re.sub(r'[…]', '', raw_body[i])
            raw_body[i] = re.sub(r'©', '', raw_body[i])
            raw_body[i]= re.sub(r'[\(\[].[\)\]]', '', raw_body[i])

            # Remove footnote numbers
            raw_body[i] = re.sub(r'([^ 0-9])([0-9])([^0-9])', '\g<1>\g<3>', raw_body[i])
            raw_body[i] = re.sub(r'([^ 0-9])([0-9]+)', '\g<1>', raw_body[i])

            # Testing Grounds
            # b = re.sub(r'([^ 0-9])([0-9]+)', '\g<1>', raw_body[i])
            # if b != raw_body[i]:
            #     print(raw_body[i])
            #     print(b)

        # Removes empty strings
        raw_body = list(filter(None, raw_body))

        # Merges the paragraphs that are split into two lines
        if title != None:
            raw_body = [title] + raw_body
        body = []
        next_it = True
        for i in range(len(raw_body)-2):
            if next_it == True:
                if raw_body[i][-1] not in ['.' , '!' , '?'] and raw_body[i+1][0].islower():
                    paragraph = raw_body[i] + ' ' + raw_body[i+1]
                    body.append(paragraph)
                    # skip the next iteration
                    next_it = False
                else:
                    body.append(raw_body[i])
            else:
                next_it = True
        body.append(raw_body[-1])

        # Remove strings that are shorter than 10 characters
        body = [x for x in body if len(x) > 10]

        text = '\n\n'.join(body)
        return text
    
    def extract_all(self, dic):
        # Extracts relevant text from the PDF
        raw_body = []
        it = 0
        for key, value in dic.items():
            it += 1
            value['text'] = value['text'].replace('-\n', '').strip()
            value['text'] = value['text'].replace('\n', ' ')
            value['text'] = value['text'].replace('  ', ' ')
            raw_body.append(value['text'])
        text = '\n\n'.join(raw_body)
        return text

    def read_file(self, file_name, flags):
        """
        Read in a file and process each page using 'single_page_layout()'
        """
        print('Reading: ', file_name)

        f = open(file_name, 'rb')
        device, interpreter, dic = self.PDFsetup()
        print('File opened')

        # Loop through every page of a PDF file
        for page_seq, page in enumerate(
                PDFPage.get_pages(f, pagenos=set(), maxpages=0, password='', caching=True, check_extractable=True)):
            interpreter.process_page(page)
            layout = device.get_result()
            page_x = (float(page.mediabox[2]) / 2)  # Middle point of current page on the x axis
            page_y = (float(page.mediabox[3]) / 2)  # Middle point of current page on the y axis

            dic.update(self.single_page_layout(layout, page_seq, page_x, page_y))  # Result for a single page
            print("Length of dic: ", len(dic))

        print('*** PDF processed ***')
        pdf = self.dic_sorting(dic)
        print('*** Dic sorted ***')

        # Comparison file which has all data in it:
        all_data = self.extract_all(pdf)
        with open(r'temp\all_data.txt', 'w+', encoding="utf-8") as f:
            f.write(all_data)

        # Extract the needed paragraphs
        body = self.extract_body(pdf, flags)
        #print(body)
        return body
