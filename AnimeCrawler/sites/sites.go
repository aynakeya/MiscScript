package sites

import (
	"animeee/crawler"
	"animeee/crawler/mixsite"
)

var SiteList = map[string]func()crawler.Crawler{
	"mixsite":mixsite.NewMixsiteCrawler,
}

func GetCrawlerByName(name string) crawler.Crawler{
	val,ok := SiteList[name]
	if !ok{
		return nil
	}
	c := val()
	return c
}

