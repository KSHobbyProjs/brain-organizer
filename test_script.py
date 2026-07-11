#!/usr/bin/env python3 

from src.parser import KeepParser
import numpy as np

parser = KeepParser("/home/keanan/brain-organizer/tests/keep/")
parser.get_keepjson_files()
notes = parser.create_notes()

# # of double spaces
nn = []
# length of text
text_len = []
# number of times there were occurences of more than 3 spaces
ss = []
for note in notes:
    text = note.text
    nn.append(len(text.strip().split('\n\n')))
    text_len.append(len(text))
    ss.append(len(text.strip().split("  ")))

nn = np.array(nn)
text_len = np.array(text_len)
ss = np.array(ss)

labels = ["double new line characters",
          "length of text",
          "double space characters"
          ]
for i, data in enumerate([nn, text_len, ss]):
    min_, max_ = np.min(data), np.max(data)
    avg, std = np.mean(data), np.std(data)
    print(f"(Min, Max, Mean, Std) for {labels[i]}:"
          f"({min_}, {max_}, {avg:.3f}, {std:.3f})"
          )



