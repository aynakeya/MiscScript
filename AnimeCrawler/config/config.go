package config

type Database struct {
	SqlitePath  string
	TablePrefix string
}

var ServerDBConfig *Database

func init() {
	ServerDBConfig = &Database{
		SqlitePath:  "./anime.db",
		TablePrefix: "anime_",
	}
}
