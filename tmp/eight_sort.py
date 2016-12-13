# coding:utf-8
# 8中基本排序算法

class BubBleSort:
    """
    冒泡排序
    """
    def sort(self, array):
        llen = len(array)
        for i in xrange(llen):
            for j in xrange(i, llen):
                if array[i] > array[j]:
                    array[i],array[j] = array[j], array[i]
        print array


class InsertSort:
    """
    插入排序
    将数组分成两部分,左边是已经排好序的,右边是待排序的,每次排一个数字
    插入前面部分,并以此后挪
    """
    def sort(self, array):
        llen = len(array)
        for i in xrange(llen):
            for j in xrange(0, i):
                if array[i] < array[j]:
                    array[i], array[j] = array[j],array[i]
        print array


# 好麻烦,不写了
class ShellSort:
    def sort(self, array):
        llen = len(array)
        if llen < 2:
            return array
        step = 2
        group = llen / 2
        while group > 0:
            for i in xrange(group):
                start = i * step
                self.insert_sort(array, start, start+step, llen)
                print array
            group /= 2
            step *= 2
        return array

    def insert_sort(self, array, start, stop, size):
        if stop > size:
            stop = size
        llen = stop - start
        if llen < 2:
            return
        for i in xrange(start, stop):
            for j in xrange(start, i):
                if array[i] < array[j]:
                    array[i], array[j] = array[j], array[i]


class QuickSort:
    def sort_oneline(self, array):
        # 小技巧,一行实现快排
        return self.sort_oneline([_ for _ in array[1:] if _ <= array[0]]) + [array[0]] + self.sort_oneline([_ for _ in array[1:] if _ > array[0]]) if array else []

    def sort(self, array):
        # 用第 0 个元素作为 povit ,找出小于他的元素放在左边,大于他的元素放在右边,然后跟上面一样
        llen = len(array)
        if llen < 2:
            return array
        pos = 0 # 最后一个小于等于 povit 的地方
        for i in xrange(1, llen):
            if array[i] < array[0]:
                pos += 1
                array[i], array[pos] = array[pos], array[i]
        array[0], array[pos] = array[pos],array[0]
        return self.sort(array[:pos]) + [array[pos]] + self.sort(array[pos+1:])

class SelectSort:
    # 每次选取最小的放在第一位
    def sort(self, array):
        llen = len(array)
        if llen < 2:
            return array
        for i in xrange(llen):
            pos = i
            for j in xrange(i, llen):
                if array[j] < array[pos]:
                    pos = j
            array[i], array[pos] = array[pos], array[i]
        return array

class HeapSort:
    # 堆排序,关键在于建堆
    # 建好堆之后,每次将对顶元素跟最后一个元素互换
    def sort(self, array):
        size = len(array)
        self.build_heap(array, size)
        for i in xrange(size-1, -1, -1):
            array[0], array[i] = array[i], array[0]
            self.adjust_heap(array, 0, i - 1)
        return array

    def build_heap(self, array, size):
        # 从后往前简堆,保证堆顶是最大的
        for i in xrange(size, -1, -1):
            self.adjust_heap(array, i, size)

    def adjust_heap(self, array, index, size):
        # 构造最大根堆
        # 从左孩子\右孩子\自身选一个最大的放在最顶
        # 这里有左右孩子是已经建立好的堆
        while True:
            child = index * 2 + 1
            if child >= size:
                break
            if child + 1 < size and array[child+1] > array[child]:
                child += 1
            if array[index] < array[child]:
                array[index], array[child] = array[child], array[index]
                index = child
            else:
                break

class MergeSort:
    """
    两路归并排序,也要注意如何递归
    """
    def sort(self, array):
        llen = len(array)
        if llen < 2:
            return array
        num = llen / 2
        left = self.sort(array[:num])
        right = self.sort(array[num:])
        return self.merge(left, right)

    def merge(self, left, right):
        l, r = 0, 0
        lenl, lenr = len(left), len(right)
        res = []
        while l < lenl and r < lenr:
            if left[l] < right[r]:
                res.append(left[l])
                l += 1
            else:
                res.append(right[r])
                r += 1
        if l < lenl:
            res.extend(left[l:])
        if r < lenr:
            res.extend(right[r:])
        return res


a = [10, 9, 8, 7, 5, 6, 5, 4, 3, 2, 1]
#BubBleSort().sort(a)
#InsertSort().sort(a)
print ShellSort().sort(a)
#print QuickSort().sort(a)
#print SelectSort().sort(a)
#print HeapSort().sort(a)
#print MergeSort().sort(a)
