package mixsite

import (
	"animeee/crawler"
	"animeee/model"
	"fmt"
	"github.com/aynakeya/deepcolor"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

var urls = []string{
	"http://6868yyw.com/",
	"http://susudm.com/",
	"http://feijisu02.com/",
}

type MixsiteCrawler struct {
	crawler.Crawler
	StartID int
	EndID int
	waitGroup sync.WaitGroup
	InfoEngine  *deepcolor.Engine
	UrlEngine *deepcolor.Engine
	Data map[string]model.Anime
}

func NewMixsiteCrawler() crawler.Crawler {
	return &MixsiteCrawler{
		StartID:40000,
		EndID:70000,
		InfoEngine:  deepcolor.NewEngine(),
		UrlEngine: deepcolor.NewEngine(),
		Data: map[string]model.Anime{},
	}
}

func (c *MixsiteCrawler) Start()  {
	for c.StartID <= c.EndID {
		c.InfoEngine.FetchAsync(fmt.Sprintf("http://www.susudm.com/acg/%s/",c.parseId()))
		c.StartID ++
		if c.StartID % 10000 == 0 {
			fmt.Println("wait 10000 to complete")
			c.Wait()
		}
	}
}

func (c *MixsiteCrawler) Wait()  {
	c.UrlEngine.WaitUntilFinish()
	c.InfoEngine.WaitUntilFinish()
	c.waitGroup.Wait()
}

func (c *MixsiteCrawler) Setup(args ...string) error{
	if (len(args)) == 0 {
		c.StartID = 1
		c.EndID = 70000
	}
	if (len(args)) == 2 {
		if val,err := strconv.ParseInt(args[0],10,0);err == nil{
			c.StartID = int(val)
		}
		if val,err := strconv.ParseInt(args[1],10,0);err == nil{
			c.EndID = int(val)
		}
	}
	c.UrlEngine.SetPeriod(time.Millisecond*100)
	c.InfoEngine.SetPeriod(time.Millisecond*100)
	c.UrlEngine.OnRequest(func(tentacle deepcolor.Tentacle) bool {
		return true
	})
	c.UrlEngine.OnResponse(func(result deepcolor.TentacleResult) bool {
		id := result.GetSingle(playid)
		anime := c.Data[id]
		rawtext :=result.(deepcolor.TentacleTextResult).Data.(string)
		for i:=0;i<10;i++{
			var s string
			if i == 0{
				s = ""
			}else{
				s = fmt.Sprintf("_%d",i)
			}
			patt := fmt.Sprintf("playarr%s\\[[0-9]+\\]=\"[^\"]*\";",s)
			if datas:= regexp.MustCompile(patt).FindAllString(rawtext,-1);len(datas)>0{
				playlist := []model.EpisodeInfo{}
				for _,data := range datas{
					data = regexp.MustCompile(fmt.Sprintf("playarr%s\\[[0-9]+\\]=\"",s)).ReplaceAllString(data,"")
					data = regexp.MustCompile("\";").ReplaceAllString(data,"")
					datasplit := strings.Split(data,",")
					playlist = append(playlist,model.EpisodeInfo{
						Title: datasplit[len(datasplit)-1],
						Url:   strings.Join(datasplit[0:len(datasplit)-2],","),
					})
				}
				anime.Episodes = append(anime.Episodes,playlist)
			}
		}
		delete(c.Data,id)
		c.waitGroup.Add(1)
		go func() {
			model.AddAnime(anime)
			c.waitGroup.Done()
		}()
		return true
	})
	c.InfoEngine.OnResponse(func(result deepcolor.TentacleResult) bool {
		fmt.Println(result.GetRequest().Url)
		id := regexp.MustCompile("[0-9]+").FindString(result.GetRequest().Url)
		ya := result.GetSingle(areayaerR)
		tmp := strings.Split(ya, "---")
		intid,_ := strconv.Atoi(id)
		if result.GetSingle(titleR) == ""{
			return false
		}
		if len(tmp) <2 {
			tmp = strings.Split(result.GetSingle(areayaerR2), "---")
		}
		if len(tmp) <2 {
			tmp = []string{"",""}
		}
		c.Data[strconv.FormatInt(int64(intid),10)] = model.Anime{
			ID:          fmt.Sprintf("susu-%s",id),
			Title:       strings.TrimSpace(result.GetSingle(titleR)),
			Area:        tmp[0],
			Year:        tmp[1],
			Tags:        result.GetList(tagsR),
			Description: result.GetSingle(descR),
			Episodes:    [][]model.EpisodeInfo{},
		}
		c.UrlEngine.FetchTentacleAsync(deepcolor.Tentacle{
			Url:         fmt.Sprintf("http://d.gqyy8.com:8077/ne2/s%d.js?%d",intid,time.Now().Unix()),
			Charset:     "utf-8",
			ContentType: deepcolor.TentacleContentTypeText,
		})
		return true
	})
	return nil
}
func (c *MixsiteCrawler) parseId() string {
	return fmt.Sprintf("%05d", c.StartID)
}
