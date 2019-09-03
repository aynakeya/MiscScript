class Config:
    export = False
    exportFile = "files.txt"
    proxies = {"http": "127.0.0.1:1087", "https": "127.0.0.1:1087"}
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
        'Connection': 'close'
    }

    saveroute = "/Users/luyijou/Downloads"

    aria2rpc = "http://localhost:6800/rpc"
    aria2token = "takethisL"

    proxyDownload = False