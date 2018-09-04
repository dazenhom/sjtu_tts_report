#!/usr/bin/python

"""Generate html for waveforms."""

import os
from optparse import OptionParser

audio_template = '<audio src="%s" controls="controls">Audio Tag not supported.</audio>'

html_head = '<!DOCTYPE HTML>\n<html>\n<body>\n'
html_end = '</body>\n</html>\n'

table_head = '<table border="1">'
table_end = '</table>'

row_head = '<tr>'
row_end = '</tr>'

column_head = '<th>'
column_end = '</th>'

def column(content):
  return '%s%s%s\n' % (column_head, content, column_end)

def row(content):
  return '%s\n%s\n%s\n' % (row_head, content, row_end)

def table(content):
  return '%s%s%s\n' % (table_head, content, table_end)

def html(content):
  return '%s%s%s\n' % (html_head, content, html_end)

def audio(wave_file):
  return audio_template % wave_file

def add_options(parser):
  parser.add_option(
    '-p',
    '--pre-tag',
    dest='pred_tag',
    default='predicted.wav',
    help='The suffix tag of the predicted waveform.')
  parser.add_option(
    '-e',
    '--extra-tags',
    dest='extra_tag',
    default='target.wav',
    help='The suffix tag of the extra wavform, splitted by ",".')
  parser.add_option(
    '-m',
    '--mode',
    dest='mode',
    default='list',
    help='The mode to create the html [list|compare]. list; list 1 column, compare: list multy column.')

def write_compare_html(wave_dir, options):
  # in 'compare' mode. compare the waveforms with different tags.
  files = os.listdir(wave_dir)
  files.sort()
  wav_tag = options.pred_tag
  all_tags = [wav_tag] + options.extra_tag.split(',')

  table_data = ''
  for wave_file in files:
    #print(wave_file)
    if not wave_file.endswith(wav_tag):
      continue
    flag = 0
    for tag in options.extra_tag.split(','):
      if wave_file.endswith(tag):
        flag = 1
        break
    if flag == 1:
      continue

    basename = wave_file[:-len(wav_tag)]
    print(basename)
    # Create name row
    row_data = ''
    for tag in all_tags:
      row_data += column('%s%s' % (basename, tag))
    table_data += row(row_data)

    # Create audio row
    row_data = ''
    for tag in all_tags:
      audio_file = '%s/%s%s' % (wave_dir, basename, tag)
      print(audio_file)
      if os.path.isfile(audio_file):
        row_data += column(audio(audio_file))
      else:
        row_data += column('No audio.')
    table_data += row_data
  content = html(table(table_data))

  return content

def write_list_html(wave_dir, options):
  # in 'list' mode. list all the waveforms in the dir.
  files = os.listdir(wave_dir)
  files.sort()
  wav_tag = options.pred_tag

  table_data = ''
  for wave_file in files:
    if not wave_file.endswith(wav_tag):
      continue

    # Create name row
    row_data = column(wave_file)
    table_data += row(row_data)

    # Create audio row
    row_data = column(audio('%s/%s' % (wave_dir, wave_file)))
    table_data += row_data
  content = html(table(table_data))

  return content

def main():
  usage = 'usage: %prog [options] wave_dir html_file\n'
  usage += 'note: it is better to put html_file in wave_dir.'
  parser = OptionParser(usage=usage)
  add_options(parser)
  (options, args) = parser.parse_args()

  if len(args) < 2:
    parser.print_help()
    exit()

  mode = options.mode
  wave_dir = args[0]
  html_file = args[1]

  if mode == 'list':
    with open(html_file, 'w') as fout:
      content = write_list_html(wave_dir, options)
      fout.write(content)
  elif mode == 'compare':
    with open(html_file, 'w') as fout:
      content = write_compare_html(wave_dir, options)
      fout.write(content)
  else:
    raise ValueError('mode [%s] is not supported!' % mode)

if __name__ == '__main__':
    main()
