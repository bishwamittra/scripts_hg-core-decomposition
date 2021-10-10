def memory_usage_psutil():
    # return the memory usage in MB
    import psutil, os
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / float(2 ** 20)
    return mem

print(memory_usage_psutil())

def another_func():
    """Undecorated function that allocates memory"""
    c = [1] * (10 ** 6)
    d = [1] * (10 ** 7)
    return c, d

if __name__ == '__main__':
    another_func()




# import os, psutil
# process = psutil.Process(os.getpid())

# def another_func():
#     """Undecorated function that allocates memory"""
#     c = [1] * (10 ** 6)
#     d = [1] * (10 ** 7)
#     return c, d

# if __name__ == '__main__':
#     another_func()



# print(process.memory_info().rss)