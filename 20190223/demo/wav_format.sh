#!/bin/bash

wav_dir='wav'

for sub_dir in `ls $wav_dir`
do
  for wav_file in `ls $wav_dir/$sub_dir/*.wav`
  do
    sox $wav_file -r 16000 -c 1 -b 16 -e signed-integer temp.wav
    mv temp.wav $wav_file
  done
done
