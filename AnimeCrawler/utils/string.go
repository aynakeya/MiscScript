package utils

func SliceString(str string, from int, to int) (string, bool) {
	sList := []rune(str)
	if to <= 0 {
		to = len(sList) + to
	}
	if from >= len(sList) || to > len(sList) {
		return "", false
	}
	return string(sList[from:to]), true
}

func LenString(str string) int {
	return len([]rune(str))
}
