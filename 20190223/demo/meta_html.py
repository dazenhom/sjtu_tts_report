#!/usr/bin/python

"""Generate html for waveforms."""

import os
from optparse import OptionParser

from utils import *

#css  = '<style type="text/css">\n    audio {width: 70px; display: block;}\n'
css  = '<style type="text/css">\n    audio {width: 65px; display: block;}\n'
css += '    table {\n        border-collapse: collapse;\n    }\n'
css += '    table, td, th {\n        border: 1px solid black;\n    }\n'
css += '</style>\n'

audio_template = '<audio src="%s" controls="controls">Audio Tag not supported.</audio>'
pic_template = '<img src="%s" alt="pics" />'

html_head = '<!DOCTYPE HTML>\n%s\n<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"/></head><html>\n<body>\n' % css
html_end = '</body>\n</html>\n'

table_head = '<table border="1">'
table_end = '</table>'

row_head = '<tr>'
row_end = '</tr>'

column_head = '<th rowspan="%d", colspan="%d">'
column_end = '</th>'

def make_column(content, rowspan=1, colspan=1):
    column_head_span = column_head % (rowspan, colspan)
    return '%s%s%s\n' % (column_head_span, content, column_end)

def make_row(content):
    return '%s\n%s\n%s\n' % (row_head, content, row_end)

def make_table(content):
    return '%s%s%s\n' % (table_head, content, table_end)

def make_html(content):
    return '%s%s%s\n' % (html_head, content, html_end)

def make_audio(wave_file):
    return audio_template % wave_file

def add_options(parser):
    parser.add_option(
        '-m',
        '--mode',
        dest='mode',
        default='meta',
        help='The mode to create the html [meta]')

class Dataset(object):
    def __init__(self, line):
        tokens = line.split('|')

        self.name = tokens[0].strip()
        self.superior = tokens[1].strip()
        self.list_file = tokens[2].strip()
        self.node_type = tokens[3].strip()
        self.comment = tokens[4].strip()
        self.children = []

        self.depth = 0
        self.branches = 0

def make_audio_list(root):
    audio_path = 'wav/%s' % root.name
    scp_path = 'scp/%s' % root.list_file

    files = os.listdir(audio_path)
    file_list = read_lines(scp_path)
    audio_html_list = ''
    for basename in file_list:
        name_match = False
        for file_name in files:
            if basename in file_name:
                name_match = True
                audio_html_list += make_column(make_audio('%s/%s' % (audio_path, file_name)))
        if not name_match:
            audio_html_list += make_column('')
    return audio_html_list

def make_text_list(root):
    scp_path = 'scp/%s' % root.list_file
    text_list = read_lines(scp_path)
    text_html_list = ''
    for text in text_list:
        text_html_list += make_column(text)
    return text_html_list


def build_tree(root, depth):
    root.depth = depth

    if len(root.children) == 0:
        root.branches = 1
    else:
        for child in root.children:
            build_tree(child, depth + 1)
            root.branches += child.branches

def build_html(root, table, max_depth, row_id):
    if len(root.children) == 0:
        # The node is a leave
        colspan = max_depth - root.depth + 1
        table[row_id] += make_column(root.comment, colspan=colspan)

        if root.node_type == 'wav':
            table[row_id] += make_audio_list(root)
        elif root.node_type == 'txt':
            table[row_id] += make_text_list(root)
    else:
        # The node is a branch
        #rowspan = len(root.children)
        rowspan = root.branches
        if root.name != '':
            table[row_id] += make_column(root.comment, rowspan=rowspan)

        shift = 0
        for child in root.children:
            build_html(child, table, max_depth, row_id + shift)
            #shift += max(1, len(child.children))
            shift += max(1, child.branches)


def create_meta_html(meta_file, head_file, options):
    # in 'list' mode. list all the waveforms in the dir.
    meta_lines = read_lines(meta_file)

    root = Dataset('||||')
    meta_dict = {'':root}
    meta_list = [] # This is a redundant variable, only to keep the order in the metadata
    for line in meta_lines:
        line = line.strip()
        if line == '' or line.startswith('#'):
            continue
        dataset = Dataset(line)
        assert dataset.name not in meta_dict
        meta_dict[dataset.name] = dataset
        meta_list.append(dataset)


    for dataset in meta_list:
        superior = meta_dict[dataset.superior]
        superior.children.append(dataset)
        #print(dataset.comment)

    build_tree(root, 0)
    max_depth = max([value.depth for value in meta_dict.values()])
    max_row = root.branches

    #print(max_depth, max_row)
    table = {}
    for i in range(0, max_row):
        table[i] = ''
    #print(table)

    build_html(root, table, max_depth, 0)

    buff = ''
    for index, row in table.items():
        #print('row index: %d' % index)
        #print(row)
        buff += make_row(row)

    with open(head_file, 'r') as fin:
        head_data = fin.read()
    buff = make_html(head_data + '\n' + make_table(buff))

    return buff



def main():
    usage  = 'usage: %prog [options] meta_file head_file html_file\n'
    usage += '  meta_file: the file storing TREEs of different experiment\n'
    usage += '  head_file: the discription of the html\n'
    usage += '  html_file: output html'
    parser = OptionParser(usage=usage)
    add_options(parser)
    (options, args) = parser.parse_args()

    if len(args) < 3:
        parser.print_help()
        exit()

    mode = options.mode
    meta_file = args[0]
    head_file = args[1]
    html_file = args[2]

    if mode == 'meta':
        with open(html_file, 'w') as fout:
            content = create_meta_html(meta_file, head_file, options)
            fout.write(content)
    else:
        raise ValueError('mode [%s] is not supported!' % mode)

if __name__ == '__main__':
    main()
