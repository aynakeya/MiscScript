package crawler

type Crawler interface {
	Setup(args ...string) error
	Start()
	Wait()
}
