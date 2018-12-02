from camzip import camzip
from camunzip import camunzip
from filecmp import cmp

import os

import time

filename = "text.txt"

#filename = "hamlet_extended.txt"


print("Original file size:", os.path.getsize(filename))

start_time = time.time()

method = "arithmetic"

camzip(method, filename)
print("Encoded")

print("Arith: --- %s seconds ---" % (time.time() - start_time))

print("File size:", os.path.getsize(filename+ '.cz' + method[0]))


start2_time = time.time()

method = "context"

camzip(method, filename)

print("Context: --- %s seconds ---" % (time.time() - start2_time))

print("File size:", os.path.getsize(filename+ '.cz' + method[0]))

# camunzip(filename + '.cz' + method[0])
# print("Decoded")


# if cmp(filename,filename+'.cuz'):
#     print('The two files are the same')
# else:
#     print('The files are different')