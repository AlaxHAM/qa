from django.test import TestCase

# from collections import Counter
#
# li = [1,2,3,2,2,2,5,4,2,3]
#
# print(Counter(li).most_common(2))   # most_common 取出最大一个数   [(2, 5)]


# li = [4,1,4,6]
#
# # print(0^4)    # 4    ^ 异或符号，任何一个数，与 0 做异或操作，得到的都是本身
# # print(0^3)    # 3
#
# li = [4,1,4,6,6]
#
# n = 0
# for i in li:
#     n ^= i    # 全遍历，每一次都与前一个数做异或，返回只出现一次的数，！！！前提这个列表只有一个元素，只出现一次
#
# print(n)  # 1


# li = [5,4,3,8,2,7,1,6]
# k = 4

# def findMinK(li, k):
#     for i in range(len(li)-1):
#         for j in range(i+1, len(li)):
#             if li[i] > li[j]:
#                 li[i], li[j] = li[j], li[i]
#     return li[:k]

# print(findMinK(li, k))


# def quick_sort(li):
#     if len(li) < 2: return li
#     mid = li[0]
#     left = [i for i in li[1:] if i <= mid]
#     right = [i for i in li[1:] if i > mid]
#     # left = quick_sort(left)
#     right = quick_sort(right)
#     return left + [mid] + right
#
# print(quick_sort(li))










