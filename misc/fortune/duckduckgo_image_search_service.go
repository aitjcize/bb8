// DuckDuckGo Image Searching service
//
// An image searching service based on the duckduckgo search engine.
// All traffic are proxied through TOR to prevent being banned by DuckDuckGo.
//
// Copyright 2017 bb8 Authors

package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"time"

	"github.com/gorilla/handlers"
	"github.com/hashicorp/golang-lru"
	"golang.org/x/net/proxy"
)

const (
	CACHE_SIZE = 10240
	PROXY_ADDR = "127.0.0.1:9050"
)

var vqd_re *regexp.Regexp = regexp.MustCompile("vqd='(.*?)'")

type ImageSearchService struct {
	httpClient *http.Client
	lruCache   *lru.ARCCache
}

func NewImageSearchService() *ImageSearchService {
	dialer, err := proxy.SOCKS5("tcp", PROXY_ADDR, nil, proxy.Direct)
	if err != nil {
		log.Fatalf("Can't connect to the proxy: %s\n", err)
	}

	httpTransport := &http.Transport{}
	httpClient := &http.Client{
		Transport: httpTransport,
		Timeout:   time.Second * 10,
	}

	// set our socks5 as the dialer
	httpTransport.Dial = dialer.Dial

	lruCache, err := lru.NewARC(CACHE_SIZE)
	if err != nil {
		panic(err)
	}

	return &ImageSearchService{httpClient, lruCache}
}

func (s *ImageSearchService) duckduckgoImageSearch(query string) ([]byte, error) {
	url := fmt.Sprintf("https://duckduckgo.com/?q=%s&iax=1&ia=images", query)
	resp, err := s.httpClient.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, errors.New(resp.Status)
	}
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	matches := vqd_re.FindStringSubmatch(string(body))

	if len(matches) == 0 {
		return nil, errors.New("no vqd token found")
	}

	vqd := matches[1]
	url = fmt.Sprintf("https://duckduckgo.com/i.js?l=zh-tw&o=json&q=%s&vqd=%s",
		query, vqd)

	resp, err = s.httpClient.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, errors.New(resp.Status)
	}
	return ioutil.ReadAll(resp.Body)
}

func (s *ImageSearchService) Run() {

	imageSearchHandler := func(w http.ResponseWriter, r *http.Request) {
		var body []byte
		var err error

		vars := r.URL.Query()
		query := vars.Get("q")

		if query == "" {
			http.Error(w, "Not found", http.StatusNotFound)
			return
		}

		if value, ok := s.lruCache.Get(query); ok {
			body, ok = value.([]byte)
			if !ok {
				s.lruCache.Remove(query)
			}
		}

		if body == nil {
			body, err = s.duckduckgoImageSearch(query)
			if err != nil {
				log.Println(err)
				http.Error(w, "Not found", http.StatusNotFound)
				return
			}
			s.lruCache.Add(query, body)
		}

		w.Header().Set("Content-Type", "application/json")
		w.Write(body)
	}

	http.HandleFunc("/image_search", imageSearchHandler)

	log.Fatal(http.ListenAndServe("0.0.0.0:7005",
		handlers.LoggingHandler(os.Stdout, http.DefaultServeMux)))
}

func main() {
	service := NewImageSearchService()
	service.Run()
}
