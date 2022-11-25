package model

import (
	"animeee/config"
	"animeee/utils"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"gorm.io/gorm/schema"
	"log"
)

var db *gorm.DB

func GetDB() *gorm.DB {
	return db
}

type DataModel struct {
	Index int `gorm:"primaryKey" json:"index"`
	ID    string
	Data  string `json:"data"`
}

func init() {
	var err error
	db, err = gorm.Open(sqlite.Open(config.ServerDBConfig.SqlitePath), &gorm.Config{
		NamingStrategy: schema.NamingStrategy{
			TablePrefix:   config.ServerDBConfig.TablePrefix,
			SingularTable: true,
		},
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		log.Println(err)
	}
	err = db.AutoMigrate(&DataModel{})
	if err != nil {
		log.Println(err)
		return
	}
	err = db.AutoMigrate(&AnimeDB{})
	if err != nil {
		log.Println(err)
		return
	}
}

func AddData(anime Anime) {
	text, _ := utils.MarshalIndentUnescape(anime,"","  ")
	var data DataModel
	db.Where(DataModel{ID: anime.ID}).First(&data)
	if data.Index > 0 {
		data.Data = text
		db.Save(&data)
	}else{
		data := &DataModel{ID: anime.ID,Data:text }
		if err := db.Create(data).Error; err != nil {
			return
		}
	}
	return
}
