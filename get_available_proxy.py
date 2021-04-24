import requests

input_file = "proxy.txt"
out_file = "valid_proxy.txt"

test_proxies = [line.strip() for line in open(input_file,'r').readlines()]
valid_proxies = []

headers = {"User-Agent": "Mozilla/5.0"}
for proxy in test_proxies:
    try:
        res = requests.get('http://www.baidu.com',proxies={"http":"127.0.0.1:1080"},headers=headers,timeout=2)
    except:
        print("[404] invalid proxy:",proxy)
        continue
    else:
        print("[200] valid proxy:",proxy)
        valid_proxies.append(proxy)

out = "\n".join(valid_proxies)
with open(out_file,'w') as f:
    f.write(out)