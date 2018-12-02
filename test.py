from camzip import camzip
from camunzip import camunzip
from filecmp import cmp

import time

filename = "hamlet.txt"

start_time = time.time()

method = "context"

#filename = "hamlet.txt"

camzip(method, filename)
print("Encoded")

# print("Arith: --- %s seconds ---" % (time.time() - start_time))


# start2_time = time.time()

# method = "dapt"

# camzip(method, filename)

# print("Adapt: --- %s seconds ---" % (time.time() - start2_time))

camunzip(filename + '.cz' + method[0])
print("Decoded")


if cmp(filename,filename+'.cuz'):
    print('The two files are the same')
else:
    print('The files are different')