def bubble_sort(nums):
    for i in range(len(nums)):
        for j in range(len(nums)-1,i,-1):
            if nums[j] > nums[j-1]:
                nums[j],nums[j-1] = nums[j-1],nums[j]
    return nums

def merge_sort(nums):
    if len(nums) == 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid:])
    right = merge_sort(nums[mid::])
    result = []
    l,r = 0,0
    while True:
        if left[l] < right[r]:
            result.append(left[l])
            l += 1
            if l == len(left):
                break
        else:
            result.append(right[r])
            r += 1
            if r == len(right):
                result = result + left[l::]
                break
    #print(result)
    return result

def quick_sort(L, low, high):
    i = low
    j = high
    if i >= j:
        return L
    key = L[i]
    while i < j:
        while i < j and L[j] >= key:
            j = j-1
        L[i] = L[j]
        while i < j and L[i] <= key:
            i = i+1
        L[j] = L[i]
    L[i] = key
    quick_sort(L, low, i-1)
    quick_sort(L, j+1, high)
    return L