from hgDecompose.utils import operator_H, operator_H_new, operator_H_quicksort, operator_H_priority_queue



H = operator_H_priority_queue
# H ([100, 2, 1, 1, 1, 1, 90, 4])
# quit()


assert H([1, 2]) == 1
assert H([1, 1, 1, 2]) == 1
assert H([1, 1, 2, 2]) == 2
assert H([2, 1, 1, 2]) == 2
assert H([1, 2, 2, 2]) == 2
assert H([2, 2, 2, 2]) == 2
assert H([1, 2, 3, 3]) == 2
assert H([1, 3, 3, 3]) == 3
assert H([100, 2, 1, 1, 1]) == 2
# print(H([0,0]))


