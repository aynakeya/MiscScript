from pyaria2 import Aria2RPC

rpc = Aria2RPC(url="http://localhost:6800/rpc")

def download(url,route,fn):
    rpc.addUri([url],{"dir":route,"out":fn,})