from hgDecompose.utils import operator_H

# H (1, 1, 1, 2) = 1 H (1, 1, 2, 2) = 2 H (1, 2, 2, 2) = 2 H(2,2,2,2)=2 H(1,2,3,3)=2 H (1, 3, 3, 3) = 3

assert operator_H([1, 1, 1, 2]) == 1
assert operator_H([1, 1, 2, 2]) == 2
assert operator_H([2, 1, 1, 2]) == 2
assert operator_H([1, 2, 2, 2]) == 2
assert operator_H([2, 2, 2, 2]) == 2
assert operator_H([1, 2, 3, 3]) == 2
assert operator_H([1, 3, 3, 3]) == 3
assert operator_H([100, 2, 1, 1, 1]) == 2
# print(operator_H([0,0]))


