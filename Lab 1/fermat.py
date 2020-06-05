import math
import random


def prime_test(N, k):
    # This is main function, that is connected to the Test button. You don't need to touch it.
    return fermat(N, k), miller_rabin(N, k)


def mod_exp(x, y, N):
    # Time complexity of this function is n^3
    # n is the length of N in bits
    # O(n) from the recursive call
    # O(n^2) from the multiplication
    # O(n^2) from the %
    # O(n*(n^2+n^2) => O(n^3) overall
    #
    # Space complexity of this function is n^2
    # n is the length of N in bits
    # n^2 comes from having to store the data during the recursion calls

    if y == 0:
        return 1
    z = mod_exp(x, math.floor(y/2), N)
    if y % 2 == 0:
        temp = z * z
        return temp % N
    else:
        temp = x * z * z
        return temp % N


def fprobability(k):
    # You will need to implement this function and change the return value.
    return 1-(1/pow(2, k))


def mprobability(k):
    # You will need to implement this function and change the return value.   
    return 1-(1/pow(4, k))


def fermat(N, k):
    # Time complexity of this function is k*(n^3)
    # n is the length of N in bits
    # k is the number of times it goes through the for loop
    # O(k) from the for loop
    # O(n^3) from the mod_exp function
    # O(k*(n^3)) overall
    #
    # Space complexity of this function is n^2
    # n is the length of N in bits
    # n^2 comes from having to store the data during mod_exp

    y = int(N-1)

    for(i) in range(k):
        x = int(random.randint(1, y))
        if mod_exp(x, y, N) == 1:
            continue
        else:
            return 'composite'

    return 'prime'


def miller_rabin(N, k):
    # Time complexity of this function is k*(n^4)
    # n is the length of N in bits
    # k is the number of times it goes through the for loop
    # Space complexity of this function is n^2
    # n^2 comes from having to store the data during mod_exp

    y = int(N - 1)
    temp = y
    for (i) in range(k):
        y = temp
        helper = 0
        x = int(random.randint(2, N-1))
        if mod_exp(x, y, N) == 1:
            while (y % 2) == 0:
                y = y/2
                if mod_exp(x, y, N) == 1:
                    continue
                else:
                    if mod_exp(x, y, N) == N-1:
                        helper = 1
                    else:
                        if helper == 1:
                            continue
                        else:
                            return 'composite'
        else:
            return 'composite'
    return 'prime'
