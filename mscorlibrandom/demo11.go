package main

import (
	"fmt"
	"math"
)

const (
	MBIG  int = 2147483647
	MSEED int = 161803398
	MZ    int = 0
)

type mscorlibRandom struct {
	seed      int
	seedArray [56]int

	inext int
	inextp int
}

func new_random(seed int) *mscorlibRandom{
	var rand_obj *mscorlibRandom =  &mscorlibRandom{
		seed:      seed,
		seedArray: [56]int{},
		inext:     0,
		inextp:    31,
	}
	var ii int = 0
	var mj int = MSEED - int(math.Abs(float64(seed)))
	var mk int = 1
	rand_obj.seedArray[55] = mj
	for i:=1;i<56;i++{
		ii = (21 * i) % 55
		(*rand_obj).seedArray[ii] = mk
		mk = mj -mk
		if mk < 0 {
			mk += MBIG
		}
		mj = (*rand_obj).seedArray[ii]
	}
	for k:=1;k<5;k++{
		for i:=1;i<56;i++{
			(*rand_obj).seedArray[i] -= (*rand_obj).seedArray[1 + (i + 30) % 55]
			if (*rand_obj).seedArray[i] < 0{
				(*rand_obj).seedArray[i] += MBIG
			}
		}
	}
	return rand_obj
}

func (r *mscorlibRandom) sample() float32{
	if r.inext +1 >= 56 {
		r.inext = 1
	}else{
		r.inext +=1
	}
	if r.inextp +1 >= 56 {
		r.inextp = 1
	}else{
		r.inextp +=1
	}
	var retVal int = r.seedArray[r.inext] - r.seedArray[r.inextp]
	if retVal < 0 {
		retVal += MBIG
	}
	r.seedArray[r.inext] = retVal
	return float32(retVal) * 1.0 / float32(MBIG)
}

func get_percent(nums *[]float32,prob float32) float32{
	var count int = 0
	for _,val := range (*nums){
		if val < prob{
			count +=1
		}
	}
	return float32(count) / float32(len(*nums))
}

func get_diff(nums *[]float32,nums2 *[]float32,prob float32)  int{
	var count int = 0
	fmt.Println(len(*nums))
	for i:=0;i<len(*nums);i++ {
		a := (*nums)[i] < prob
		b := (*nums2)[i] < prob
		if a == b{
			count ++
		}
	}
	return count
}

func get_nums(seed int,count int) *[]float32{
	var rand *mscorlibRandom = new_random(seed)
	var nums []float32 = make([]float32,count)
	for i:=0;i<count;i++{
		nums = append(nums, rand.sample())
	}
	return &nums
}

func main() {
	//var rand *mscorlibRandom = new_random(3440934)
	var maxPercent float32 = 0
	var maxSeed int = 0
	var maxCount int = 0
	
	bestnums := get_nums(4050455,128)

	for i:=0;i<=9999999;i++{
		nums := get_nums(i,128)
		var p float32 = get_percent(nums,0.2)
		var c int = get_diff(bestnums,nums,0.2)
		if p > maxPercent{
			maxSeed = i
			maxPercent = p
			fmt.Println(i,p)
		}
		if c > maxCount{
			maxCount = c
			fmt.Println(i,c)
		}
	}
	fmt.Println(maxSeed,maxPercent)
}
