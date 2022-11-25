package model

import (
	"animeee/utils"
	"encoding/json"
	"strings"
)

type Anime struct {
	ID          string          `json:"id"`
	Title       string          `json:"title"`
	Area        string          `json:"area"`
	Year        string          `json:"year"`
	Tags        []string        `json:"tags"`
	Description string          `json:"description"`
	Episodes    [][]EpisodeInfo `json:"episodes"`
}

type EpisodeInfo struct {
	Title string `json:"title"`
	Url   string `json:"url"`
}

type AnimeDB struct {
	Index       int `gorm:"primaryKey"`
	ID          string `json:"id"`
	Title       string `json:"title"`
	Area        string `json:"area"`
	Year        string `json:"year"`
	Tags        string `json:"tags"`
	Description string `json:"description"`
	Episodes    string `json:"episodes"`
}

func ToAnimeDB(anime Anime) AnimeDB {
	ep, _ := utils.MarshalUnescape(anime.Episodes)
	return AnimeDB{
		ID:          anime.ID,
		Title:       anime.Title,
		Area:        anime.Area,
		Year:        anime.Year,
		Tags:        strings.Join(anime.Tags,","),
		Description: anime.Description,
		Episodes:    ep,
	}
}

func UpdateAnimeDB(anime Anime,animeDB *AnimeDB)  {
	animeDB.Title = anime.Title
	animeDB.Area = anime.Area
	animeDB.Year = anime.Year
	animeDB.Tags = strings.Join(anime.Tags,",")
	animeDB.Description = anime.Description
	ep, _ := utils.MarshalUnescape(anime.Episodes)
	animeDB.Episodes = ep
}

func ToAnime(animeDB AnimeDB) Anime {
	var ep [][]EpisodeInfo
	err := json.Unmarshal([]byte(animeDB.Episodes),&ep)
	if err != nil {
		return Anime{}
	}
	return Anime{
		ID:          animeDB.ID,
		Title:       animeDB.Title,
		Area:        animeDB.Area,
		Year:        animeDB.Year,
		Tags:        strings.Split(animeDB.Tags,","),
		Description: animeDB.Description,
		Episodes:    ep,
	}
}

func AddAnime(anime Anime) {
	var data AnimeDB
	db.Where(AnimeDB{ID: anime.ID}).First(&data)
	if data.Index > 0 {
		UpdateAnimeDB(anime,&data)
		db.Save(&data)
	}else{
		data = ToAnimeDB(anime)
		if err := db.Create(&data).Error; err != nil {
			return
		}
	}
	return
}

func GetAnime(query AnimeDB) Anime{
	var animedb AnimeDB
	db.Where(query).First(&animedb)
	if animedb.Index > 0 {
		return ToAnime(animedb)
	}else{
		return Anime{}
	}
}
