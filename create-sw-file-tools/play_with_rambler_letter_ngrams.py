#!/usr/bin/env python3

#######################################################################
# Create rambler letter ngrams
#
# Author: Garry Morrison
# Date: 2015-7-19
# Update: 2015-8-2
# Copyright: GPLv3
#
# Usage:
#  sa: load ngram-letter-pairs--sherlock-holmes--add-learn.sw
#  sa: letter-ramble |*> #=> merge-labels(|_self> + weighted-pick-elt next-2-letters extract-3-tail-chars |_self>)
#  sa: letter-ramble^1000 |The>
#  sa: letter-ramble^500 |Here >
# 
# Sample data here:
# http://semantic-db.org/sw-examples/ngram-letter-pairs--sherlock-holmes--add-learn.sw
# 
#
#######################################################################

import sys

from the_semantic_db_code import *
from the_semantic_db_functions import *
from the_semantic_db_processor import *

import re

C = context_list("rambler letter ngrams")


# create ngram pairs:
# eg:
# "a b c", "d e"
def create_ngram_pairs(s):
  return [[" ".join(s[i:i+3])," ".join(s[i+3:i+5])] for i in range(len(s) - 4)]

# quick test: Yup! seems to work!
# print(create_ngram_pairs("a b c d e f g h".split()))
# print(create_ngram_pairs("a b c d e".split()))


# plan: 
# next-2 |a b c> => |d e>
#

# create ngram letter pairs:
# eg:
# "abc", "de"
def create_ngram_letter_pairs(s):
  return [["".join(s[i:i+3]),"".join(s[i+3:i+5])] for i in range(len(s) - 4)]

# plan:
# next-2-letters |abc> => |de>


# source file:
#filename = "text/WP-Adelaide.txt"
#filename = "text/ebook-Tom_Sawyer_74.txt"
#filename = "text/all.txt"  # used too much RAM. Not sure how much in total it would need. test later.
#filename = "text/ebook-moby-shakespeare.txt"
#filename = "text/ebook-Gone-with-the-wind--0200161.txt"
filename = "text/ebook-Sherlock-Holmes.txt"


# learn ngram pairs:
def learn_ngram_pairs(context,filename):
  with open(filename,'r') as f:
    text = f.read()
#    words = [w for w in re.split('[^a-z0-9_\']',text.lower()) if w]  # need to change this!!
#    words = text.strip('<').strip('>').strip('|').split()
    words = re.sub('[<|>=\r\n]',' ',text)
    for ngram_pairs in create_ngram_pairs(words.split()):
      try:
        head,tail = ngram_pairs
        context.add_learn("next-2",head,tail)
      except:
        continue

# learn ngram letter pairs:
def learn_ngram_letter_pairs(context,filename):
  with open(filename,'r') as f:
    text = f.read()
    clean_text = re.sub('[<|>=\r\n]',' ',text)
    for ngram_pairs in create_ngram_letter_pairs(list(clean_text)):
      try:
        head,tail = ngram_pairs
        context.add_learn("next-2-letters",head,tail)
      except:
        continue
    
learn_ngram_letter_pairs(C,filename)

dest = "sw-examples/ngram-letter-pairs--sherlock-holmes.sw"
save_sw(C,dest)

