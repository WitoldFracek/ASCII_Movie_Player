import numpy as np
from numba import vectorize, int32
import random


@vectorize(['int32(int32)'], target='cuda')
def increase_random(num):
    ret = num
    return ret


def get_array(length):
    return np.asarray([1 for _ in range(length)], dtype=np.int)


if __name__ == '__main__':
    ar = get_array(300)
    print(increase_random(ar))
