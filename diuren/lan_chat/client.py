import socket,threading
import time,sys

running = False

def send(c):
    time.sleep(0.5)
    while True:
        data = input('')
        c.send(data.encode("utf-8"))
        if data == "-!-quit-!-":
            running = False
            break

def recv(c,t2):
    username = input("输入用户名： ")
    c.send(username.encode("utf-8"))
    t2.start()
    while running:
        try:
            data = c.recv(1024).decode("utf-8")
            if not data:
                break
            print(data)
        except:
            break


if __name__ == "__main__":
    ip = ""
    addrs = socket.getaddrinfo(socket.gethostname(), None)
    print("开始扫描可用的服务器")
    for i in range(100,200):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(0.1)
        temp = "192.168.1.%s" % i
        try:
            data = client.connect_ex((temp, 12345))
            if data == 0:
                print("找到服务器%s" % temp)
                a = input("是否连接 y/n")
                if a == "y":
                    ip = temp
                    break
                else:
                    continue
        except:
            print("2")
        client.close()
    if ip == "":
        print("未连接任何服务器")
        sys.exit()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 导入 socket 模块
    try:
        client.connect((ip, 12345))
        running = True
        t2 = threading.Thread(target=send, args=(client,))
        t1 = threading.Thread(target=recv, args=(client,t2))
        t1.start()
        t1.join()
        t2.join()
    except:
        pass
    finally:
        print("连接已被关闭")
        client.close()