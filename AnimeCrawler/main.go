package main

import "animeee/crawler/mixsite"

func main()  {
	crawler := mixsite.NewMixsiteCrawler()
	crawler.Setup()
	crawler.Start()
	crawler.Wait()
}
