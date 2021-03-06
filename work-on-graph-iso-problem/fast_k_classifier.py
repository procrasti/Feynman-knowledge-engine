#!c:/Python34/python.exe

#######################################################################
# Given a list of sw files that are undirected, unlabeled, unweighted,
# put them into categories based on their k-similarity.
# works great for the examples I have tested.
# where k-similarity is a mapping from network structure to an integer
# if two sw files have different k-similarity for some k, then they are definitely not graph isomorphic
# if two sw files have the same k-similarity for say k = 3, then they are probably, but not definitely, graph isomorphic
# my algo might have collisions, where non-isomorphic graphs have the same k-similarity,
# but presumably this doesn't persist for all k.
# NB: what is the big-O for this code? Doesn't look too bad!
# Details here:
# http://write-up.semantic-db.org/194-introducing-network-k-similarity.html
#
# Author: Garry Morrison
# email: garry -at- semantic-db.org
# Date: 2016-03-16
# Update: 2016-03-18
# Copyright: GPLv3
#
# Usage: ./k_classifier.py k network-1.sw [network-2.sw network-3.sw ...]
#
# Hrmmm... the two Ramsey graphs given on this page:
# http://cstheory.stackexchange.com/questions/1064/polynomial-time-algorithm-for-graph-isomorphism-testing
# are in the same class for k in {0,1,...18}, but different for k >= 19
# So, is my algo broken? Is there a bug in the modulus code I used to speed it up?
# Hrmm... maybe the bug is in: v2 = int(r.count_sum())
# Fixed! It was indeed the float to int code that was the bug.
# Those two graphs now give the same signature up to k = 40.
# BTW, the fix was a temporary change in the ket() class. I had to change value to int(value) from float(value)
# this means, when I switch it back to float(value), which the full project needs, it will break again.
# Just a warning.
#
# Also, I suspect, we can stop roughly when v1 is equal to the number of nodes in the network.
# Or maybe one round after that. The idea being the op^k has reached the entire network.
# I don't know a clean way to make sure that all nodes have reached that point.
# Alternatively, maybe k = 3 or 4 is sufficient to pretty much prove isomorphism??
#
#######################################################################


import sys
import os
import math
import hashlib
from collections import OrderedDict

from the_semantic_db_code import *
from the_semantic_db_functions import *
from the_semantic_db_processor import *

#context = context_list("find k similarity")


try:
  k = int(sys.argv[1])
  list_of_files = sys.argv[2:]
except:
  print("\nUsage: ./k_classifier.py k network-1.sw [network-2.sw network-3.sw ...]\n")
  sys.exit(1)


# define our primes:
# from here: https://primes.utm.edu/lists/small/10000.txt
primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113]
primes += [127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229]
primes += [233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,349]
primes += [353,359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463]
primes += [467,479,487,491,499,503,509,521,523,541,547,557,563,569,571,577,587,593,599,601]


# check we have enough primes:
if 2*k + 2 > len(primes):
  print("We need",2*k+2,"primes. We only have",len(primes))
  sys.exit(1)

# hardwire in the operator label:
op = "op"

# define our modulus (a prime):
#m = 32416190071
m = 4257452468389
#m = 4257452468389*32416190071

# define our node to signature function:
# context is a context, node is a ket, op is a string, k is a positive integer
#
def node_to_signature(context,node,op,k):
  signature = 1
  r = node
  v_list = []
  for n in range(0,k+1):
    v1 = int(r.count())
    v2 = int(r.count_sum())
    v_list.append(v1)
    v_list.append(v2)

    print("n:",n)
    print("r:",r)
    print("v1:",v1)
    print("v2:",v2)
    r = r.apply_op(context,op)

  print("v_list:",v_list)
#  v_list.sort(reverse=True)        # we reverse sort the list, so largest v's are applied to smallest primes. This is quite a big saving.
#  v_list.reverse()                  # just reverse the list. Yeah, slightly bigger integers than reverse-sort, but reduces the chance of an accidental collision.
  print("v_list:",v_list)            # actually, using modular arithmetic, v_list.reverse() doesn't do much for us.
  for i,v in enumerate(v_list):
#    signature *= primes[i]**v
    signature = ((signature % m) * pow(primes[i],v,m) ) % m
  print("signature:",signature)
  return signature



def file_to_hash(filename,op,k):
  context = new_context("k classification")
  context.load(filename)

  signature = 1

  # walk the network:
  # NB: multiplication is Abelian, so the order we examine nodes does not matter.
  for x in context.relevant_kets(op):
#    signature *= node_to_signature(context,x,op,k)
    signature = ((signature % m) * node_to_signature(context,x,op,k) ) % m
  print("sig:",signature)
  return hashlib.sha1(str(signature).encode('utf-8')).hexdigest()



network_classes = OrderedDict()
for name in list_of_files:
  base = os.path.basename(name)
  base, ext = base.rsplit('.',1)
  file_hash = file_to_hash(name,"op",k)       # hardwired in the operator name "op"
  if file_hash in network_classes:
    network_classes[file_hash].append(base)
  else:
    network_classes[file_hash] = [base]

print("\nthe k = %s network classes:\n----------------------------" % str(k))
for hash in network_classes:
  the_class = network_classes[hash]
#  print(", ".join(the_class))
  print(hash + ": " + ", ".join(the_class))
print("----------------------------\n")

print("2nd-order-k%s-network:" % str(k))
for i,hash in enumerate(network_classes):
  the_class = network_classes[hash]
  the_class_sp = '|' + '> + |'.join(the_class) + '>'
  print('class |%s> => ' % str(i+1) + the_class_sp)

print()
for i,hash in enumerate(network_classes):
  print('hash |%s> => |%s>' % (str(i+1),hash))

