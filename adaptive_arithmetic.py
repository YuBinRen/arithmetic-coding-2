from math import floor, ceil
from sys import stdout as so
from bisect import bisect

def encode(x):

    #------------------------------------------------------------------------------------
    #INITIALISAITION
    #------------------------------------------------------------------------------------

    #implementing Laplace estimator, intialising frequencies range
    frequencies = dict([(key, 1) for key in range(1,128)])

    #initialising probabilities
    n = sum([frequencies[a] for a in frequencies])
    p = dict([(a,frequencies[a]/n) for a in frequencies])

    #initialising precisions
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter

    y = [] # initialise output list

    lo,hi = 0,one # initialise lo and hi to be [0,1.0)
    straddle = 0 # initialise the straddle counter to 0


    #------------------------------------------------------------------------------------
    #ITERATION
    #------------------------------------------------------------------------------------

    for k in range(len(x)): # for every symbol
        #print(x[k], frequencies)
        
        # arithmetic coding is slower than vl_encode, so we display a "progress bar"
        # to let the user know that we are processing the file and haven't crashed...
        # if k % 100 == 0:
        #     so.write('Adaptive Arithmetic encoded %d%%    \r' % int(floor(k/len(x)*100)))
        #     so.flush()


        # UPDATING DISTRIBUTIONS
        #---------------------------------------------------------------------------        
        f = [0]    

        for a in p: # for every probability in p
            f.append(f[-1]+p[a])
        f.pop(-1)
        
        f = dict([(a,mf) for a,mf in zip(p,f)])
        #---------------------------------------------------------------------------

        lohi_range = hi-lo + 1

        a = x[k]
        
        #update lo and hi
        lo = lo + int(ceil(f[a]*lohi_range))
        hi = lo + int(floor(p[a]*lohi_range))

        if (lo > one or hi > one):
            raise ValueError('Probabilities greater than one!')


        if (lo == hi):
            raise NameError('Zero interval!')

        # Now we need to re-scale the interval if its end-points have bits in common,
        # and output the corresponding bits where appropriate. We will do this with an
        # infinite loop, that will break when none of the conditions for output / straddle
        # are fulfilled

        while True:
            if hi < half: # if lo < hi < 1/2
                # stretch the interval by 2 and output a 0 followed by 'straddle' ones (if any)
                # and zero the straddle after that. In fact, HOLD OFF on doing the stretching:
                # we will do the stretching at the end of the if statement
                
                y.append(0) # append a zero to the output list y
                y.extend([1]*straddle) # extend by a sequence of 'straddle' ones
                straddle = 0 # zero the straddle counter
 
            elif lo >= half: # if hi > lo >= 1/2
                # stretch the interval by 2 and substract 1, and output a 1 followed by 'straddle'
                # zeros (if any) and zero straddle after that. Again, HOLD OFF on doing the stretching
                # as this will be done after the if statement, but note that 2*interval - 1 is equivalent
                # to 2*(interval - 1/2), so for now just substract 1/2 from the interval upper and lower
                # bound (and don't forget that when we say "1/2" we mean the integer "half" we defined
                # above: this is an integer arithmetic implementation!
                
                y.append(1) # append a 1 to the output list y
                y.extend([0]*straddle) # extend 'straddle' zeros
                straddle = 0 # reset the straddle counter
                lo -= half
                hi -= half # substract half from lo and hi
                
            elif lo >= quarter and hi < threequarters: # if 1/4 < lo < hi < 3/4
                # we can increment the straddle counter and stretch the interval around
                # the half way point. This can be impemented again as 2*(interval - 1/4),
                # and as we will stretch by 2 after the if statement all that needs doing
                # for now is to subtract 1/4 from the upper and lower bound
                straddle += 1 # increment straddle
                lo -= quarter
                hi -= quarter # subtract 'quarter' from lo and hi
            else:
                break # we break the infinite loop if the interval has reached an un-stretchable state
            
            # now we can stretch the interval (for all 3 conditions above) by multiplying by 2
            lo *= 2 # multiply lo by 2
            hi = hi*2 + 1 # multiply hi by 2 and add 1 (I DON'T KNOW WHY +1 IS NECESSARY BUT IT IS. THIS IS MAGIC.
                # A BOX OF CHOCOLATES FOR ANYONE WHO GIVES ME A WELL ARGUED REASON FOR THIS... It seems
                # to solve a minor precision problem.)


        #UPDATING FREQUENCIES 
        #------------------------------------------------------------------
        frequencies[x[k]] += 1
        n = sum([frequencies[a] for a in frequencies])
        p = dict([(a,frequencies[a]/n) for a in frequencies])



    # termination bits
    # after processing all input symbols, flush any bits still in the 'straddle' pipeline
    straddle += 1 # adding 1 to straddle for "good measure" (ensures prefix-freeness)
    if lo < quarter: # the position of lo determines the dyadic interval that fits
        y.append(0) # output a zero followed by "straddle" ones
        y.extend([1]*straddle)
    else:
        y.append(1)
        y.extend([0]*straddle) # output a 1 followed by "straddle" zeros

    return(y)



def decode(y):

    #------------------------------------------------------------------------------------
    #INITIALISAITION
    #------------------------------------------------------------------------------------

    #implementing Laplace estimator, intialising frequencies range
    frequencies = dict([(key, 1) for key in range(1,128)])

    #initialising precisions
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter


    # initialise by taking first 'precision' bits from y and converting to a number
    value = int(''.join(str(a) for a in y[0:precision]), 2) 
    position = precision # position where currently reading y

    #initialising frequencies and probabilities
    frequencies = dict([(key, 1) for key in range(1,128)])

    f, p , alphabet = update_freqs(frequencies)

    y.extend(precision*[0]) # dummy zeros to prevent index out of bound errors
    x = []

    lo,hi = 0,one # initialise lo and hi to be [0,1.0)

    #------------------------------------------------------------------------------------
    #ITERATION
    #------------------------------------------------------------------------------------
    #k = 0
    while True:
        #k += 1
        # if k % 100 == 0:
        #     so.write('Adaptive Arithmetic decoded %d%%    \r' % int(floor(k/len(y)*100)))
        #     so.flush()

        lohi_range = hi - lo + 1
        
        a = bisect(f, (value-lo)/lohi_range) - 1    
        #print(chr(x[-1]))

        lo = lo + int(ceil(f[a]*lohi_range))
        hi = lo + int(floor(p[a]*lohi_range))

        if (lo > one or hi > one):
            raise ValueError('Probabilities greater than one!')


        if (lo == hi):
            raise NameError('Zero interval!')

        while True:
            if hi < half:
                # do nothing
                pass
            elif lo >= half:
                lo = lo - half
                hi = hi - half
                value = value - half
            elif lo >= quarter and hi < threequarters:
                lo = lo - quarter
                hi = hi - quarter
                value = value - quarter
            else:
                break
            lo = 2*lo
            hi = 2*hi + 1
            value = 2*value + y[position]
            position += 1
            if position >= len(y):
                return(x)

        x.append(alphabet[a]) # output alphabet[a]
        frequencies[alphabet[a]] += 1
        f, p , alphabet = update_freqs(frequencies)

    

def update_freqs(frequencies):
    n = sum([frequencies[a] for a in frequencies])
    p = dict([(a,frequencies[a]/n) for a in frequencies])
    alphabet = list(p)
    f = [0]
    for a in p:
        f.append(f[-1]+p[a])
    f.pop()

    p = list(p.values())

    return f, p, alphabet


if __name__ == "__main__":
    filename = 'hamlet.txt'
    with open(filename, 'rb') as fin:
        x = fin.read()
    output = encode(x)