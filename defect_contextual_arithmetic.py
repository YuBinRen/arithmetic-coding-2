from math import floor, ceil
from sys import stdout as so
from bisect import bisect
import itertools

kappa = 3


def encode(x):

    #------------------------------------------------------------------------------------
    #INITIALISAITION
    #------------------------------------------------------------------------------------

    #implementing Laplace estimator, intialising frequencies range
    frequencies = []
    for i in range(kappa):
        frequencies.append({})
    frequencies[0]['escape'] = 1
    #frequencies have the following structure: frequencies[number of context alphabets][context name][alphabet][frequency]

    #initialising precisions
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter

    #print(frequencies)

    y = [] # initialise output list

    lo,hi = 0,one # initialise lo and hi to be [0,1.0)
    straddle = 0 # initialise the straddle counter to 0


    #------------------------------------------------------------------------------------
    #ITERATION
    #------------------------------------------------------------------------------------

    for k in range(len(x)): # for every symbol
        #print(k)

        # UPDATING DISTRIBUTIONS
        #---------------------------------------------------------------------------        
        a = []
        for i in range(kappa):
            if k-i >= 0:
                a.append(x[k-i])
            else:
                a.append('')

        p = update_prob(frequencies, a)

        # debugging
        # if k <= 5:
        # 	summation = sum(p.values())
        # 	print(summation)
        # 	print(p)

        f = update_culm_prob_enc(p)
        #print(p)

        # if f[-1] > 1:
        #     raise ValueError('The probablities don't add up to 1!'')

        lohi_range = hi-lo + 1
        
        #Lo Hi Calculations
        #--------------------------------------------------------------------------- 
       
        
        lo = lo + int(ceil(f[a[0]]*lohi_range))
        hi = lo + int(floor(p[a[0]]*lohi_range))


        if (lo > one or hi > one):
        	raise ValueError('Probabilities greater than one!')


        if (lo == hi):
            raise NameError('Zero interval!')

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

        #This should be the last step, where the context frequency distribution should be calculated
        frequencies = update_freq(a, frequencies)

        #debugging
        if k <= 10:
            print(x[k])
            print(frequencies)

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
    frequencies = []
    for i in range(kappa):
        frequencies.append({})
    frequencies[0]['escape'] = 1
    #frequencies have the following structure: frequencies[number of context alphabets][context name][alphabet][frequency]

    #initialising precisions
    precision = 32
    one = int(2**precision - 1)
    quarter = int(ceil(one/4))
    half = 2*quarter
    threequarters = 3*quarter

    y.extend(precision*[0]) # dummy zeros to prevent index out of bound errors
    x = []
    a = ['']*kappa

    # initialise by taking first 'precision' bits from y and converting to a number
    value = int(''.join(str(a) for a in y[0:precision]), 2) 
    position = precision # position where currently reading y

    lo,hi = 0,one # initialise lo and hi to be [0,1.0)

    #------------------------------------------------------------------------------------
    #CALCULATION
    #------------------------------------------------------------------------------------

    while True: # for every symbol
        p = update_prob(frequencies, a)
        f = update_culm_prob_dec(p)

        #print(f)
        lohi_range = hi - lo + 1

        a.insert(0, bisect(f, (value-lo)/lohi_range)-1)

        if len(a) > kappa:
            a.pop(-1)

        # debugging
        #print(a[0])

        lo = lo + int(ceil(f[a[0]]*lohi_range))
        hi = lo + int(floor(p[a[0]]*lohi_range))

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
                return(cut(x))

            #------------------------------------------------------------------------------------
            #UPDATE
            #------------------------------------------------------------------------------------
            x.append(a[0])

            update_freq(a, frequencies)

            #debugging
            if len(x) <= 10:
                print(x[-1])
                print(a)
                print(frequencies)
    return(x)

def update_prob(frequencies, a):
    p = {}
    context = list(a)
    context.reverse()
    for i in range(127):
        if tuple(a) in frequencies[kappa-1]:
            if i in frequencies[kappa-1][tuple(context)]:
                prob = frequencies[kappa-1][tuple(a)][i]/sum(frequencies[kappa-1][tuple(context)].values())
            else:
                prob = 1/sum(frequencies[kappa-1][tuple(context)].values())
        else:
            prob = 1/128
        p[i] = prob
    n = sum([p[a] for a in p])
    p = dict([(a,p[a]/n) for a in p])
    return p

def update_culm_prob_enc(p):
    f = [0]    

    for a in p: # for every probability in p
        f.append(f[-1]+p[a])
    f.pop(-1)
    
    f = dict([(a,mf) for a,mf in zip(p,f)])
    return f

def update_culm_prob_dec(p):
    f = [0]    

    for a in p: # for every probability in p
        f.append(f[-1]+p[a])
    f.pop(-1)

    return f

def update_freq(a, frequencies):
    for i in range(kappa):
        #print(i, a)
        if (a[i] == ''):
            break
        elif i == 0:
            frequencies[0][a[i]] = frequencies[0].setdefault(a[i], 0) + 1
        elif i == 1:            
            context = a[i]
            frequencies[i].setdefault(context, {})
            if a[0] not in frequencies[i][context]:
                frequencies[i][context].setdefault(a[0],0)
                frequencies[i][context]['escape'] = 1
            frequencies[i][context][a[0]] += 1
        else:
            #print(a[1:i+1])
            context_list = a[1:i+1]
            #context_list.reverse()
            context_tuple = tuple(context_list)
            #print(type(context_tuple)) 
            frequencies[i].setdefault(context_tuple, {})
            if a[0] not in frequencies[i][context_tuple]:
                frequencies[i][context_tuple].setdefault(a[0],0)
                frequencies[i][context_tuple]['escape'] = 1
            frequencies[i][context_tuple][a[0]] += 1
    return frequencies


def cut(x):
    output = []
    for i in range(len(x)):
        if i%7 == 0:
            output.append(x[i])
    return(output)



if __name__ == "__main__":
    filename = 'hamlet.txt'
    with open(filename, 'rb') as fin:
        x = fin.read()
    output = encode(x)