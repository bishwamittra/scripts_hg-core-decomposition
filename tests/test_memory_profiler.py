#Load its magic function
%load_ext memory_profiler
from memory_profiler import profile

def addition():
    a = [1] * (10 ** 1)
    b = [2] * (3 * 10 ** 2)
    sum = a+b
    return sum
%memit addition()
# print(addition())