package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/gin-gonic/gin"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"os/signal"
	"strings"
	"time"
)

type ProxySetting struct {
	Prefix          string
	Host            string
	HeaderOverwrite map[string]string
}

type Proxy struct {
	Setting ProxySetting
	proxy   *httputil.ReverseProxy
}

func NewProxy(setting ProxySetting) (*Proxy, error) {
	p := &Proxy{
		Setting: setting,
	}
	uri, err := url.Parse(setting.Host)
	if err != nil {
		return nil, err
	}
	proxy := httputil.NewSingleHostReverseProxy(uri)
	proxy.Director = func(req *http.Request) {
		realPath := req.URL.Path[len(p.Setting.Prefix):]
		if realPath == "" {
			realPath = "/"
		}
		req.URL.Scheme = uri.Scheme
		req.URL.Host = uri.Host
		req.URL.Path = realPath
		req.Host = uri.Host
		req.Header.Set("referer", req.URL.String())
		req.Header.Set("origin", uri.Host)
		req.Header.Set("X-Forwarded-For", req.RemoteAddr)
		for k, v := range p.Setting.HeaderOverwrite {
			req.Header.Set(k, v)
		}
	}
	p.proxy = proxy
	return p, nil
}

func (p *Proxy) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	p.proxy.ServeHTTP(w, r)
}

type MulitDomainProxyServer struct {
	ProxyPath string
	ApiPath   string
	Proxies   map[string]*Proxy
}

func (s *MulitDomainProxyServer) handleProxy(resp http.ResponseWriter, req *http.Request) {
	base := strings.Split(req.URL.Path[len(s.ProxyPath):], "/")
	if len(base) == 0 {
		http.NotFound(resp, req)
		return
	}
	if base[0] == "" {
		base = base[1:]
	}
	proxy, ok := s.Proxies["/"+base[0]]
	if !ok {
		http.NotFound(resp, req)
		return
	}
	req.URL.Path = "/" + strings.Join(base, "/")
	req.URL.RawPath = ""
	proxy.ServeHTTP(resp, req)
}

func (s *MulitDomainProxyServer) AddProxy(setting ProxySetting) error {
	proxy, err := NewProxy(setting)
	if err != nil {
		return err
	}
	s.Proxies[setting.Prefix] = proxy
	return nil
}

func (s *MulitDomainProxyServer) handleApi(resp http.ResponseWriter, req *http.Request) {
	var setting ProxySetting
	err := json.NewDecoder(req.Body).Decode(&setting)
	if err != nil {
		http.Error(resp, err.Error(), http.StatusBadRequest)
		return
	}
	err = s.AddProxy(setting)
	if err != nil {
		http.Error(resp, err.Error(), http.StatusBadRequest)
	}
	resp.WriteHeader(http.StatusOK)
	_, _ = resp.Write([]byte("ok"))
}

func createGinRouter(s *MulitDomainProxyServer) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.GET(s.ApiPath, func(context *gin.Context) {
		s.handleApi(context.Writer, context.Request)
	})
	router.Any(fmt.Sprintf("%s/*any", s.ProxyPath), func(context *gin.Context) {
		s.handleProxy(context.Writer, context.Request)
	})
	router.NoRoute(func(context *gin.Context) {
		context.Status(http.StatusNotFound)
	})
	return router
}

func main() {
	configFile := flag.String("config", "config.json", "config file")
	port := flag.Int("port", 5000, "listen port")
	ip := flag.String("host", "localhost", "host ip")
	pp := flag.String("proxy", "/proxy", "proxy path")
	ap := flag.String("api", "/api", "api path")
	flag.Parse()

	s := &MulitDomainProxyServer{
		ProxyPath: *pp,
		ApiPath:   *ap,
		Proxies:   make(map[string]*Proxy),
	}

	proxySettings := []ProxySetting{}
	data, err := os.ReadFile(*configFile)
	if err == nil {
		err = json.Unmarshal(data, &proxySettings)
	}
	if err != nil {
		log.Println("load settings fail, using default: ", err)
	}

	for _, setting := range proxySettings {
		err := s.AddProxy(setting)
		if err != nil {
			log.Printf("add proxy %s fail: %s\n", setting.Prefix, err)
		}
	}

	router := createGinRouter(s)

	srv := &http.Server{
		Addr:    fmt.Sprintf("%s:%d", *ip, *port),
		Handler: router,
	}
	log.Println("server start at ", srv.Addr)
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	// 等待中断信号以优雅地关闭服务器（设置 5 秒的超时时间）
	quit := make(chan os.Signal)
	signal.Notify(quit, os.Interrupt)
	<-quit
	log.Println("Shutdown Server ...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server Shutdown:", err)
	}
	log.Println("Saving settings")
	proxySettings = []ProxySetting{}
	for _, proxy := range s.Proxies {
		proxySettings = append(proxySettings, proxy.Setting)
	}
	data, err = json.Marshal(proxySettings)
	if err == nil {
		err = os.WriteFile(*configFile, data, 0644)
	}
	if err != nil {
		log.Println("save settings fail: ", err)
	}
	log.Println("Server exiting")
}
