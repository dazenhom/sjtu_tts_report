#!/usr/bin/python


import os

def load_name_list(list_name):
  fin = open(list_name, 'r')
  name_list = fin.read().strip().split('\n')
  fin.close()

  return name_list

def read_lines(file_name):
  fin = open(file_name, 'r')
  lines = fin.read().strip().split('\n')
  fin.close()

  return lines

def execute_command(command):
  r = os.popen(command)
  text = r.read()
  r.close()
  return text.strip()

def int_to_fix_len(value, fix_len=4):
  ret = '%d' % value
  if len(ret) > fix_len:
    raise ValueError('Value length larger than the fix length.')

  return '0' * (fix_len - len(ret)) + ret 

def string_to_vector(line):
  tokens = line.strip().split(' ')
  vector = [0] * len(tokens)
  for i in range(len(tokens)):
    vector[i] = float(tokens[i])
  return vector
