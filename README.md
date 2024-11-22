# ProXer
ProXer is a tool designed to evaluate the quality and validity of proxies by detecting their type (HTTP, HTTPS, SOCKS4, SOCKS5), checking their functionality, and retrieving additional details like country, anonymity status, and VPN association using external APIs. Valid proxies are categorized and saved into organized files for easy access, and the tool uses multi-threading to efficiently process large proxy lists.
# Buy Proxies
- Free Proxies Static Residental: 
1. [WebShare](https://www.webshare.io/?referral_code=p7k7whpdu2jg)
2. [ProxyScrape](https://proxyscrape.com/?ref=odk1mmj)
3. [MonoSans](https://github.com/monosans/proxy-list)
- Paid Premium Static Residental:
1. [922proxy](https://www.922proxy.com/register?inviter_code=d03d4fed)
2. [Proxy-Cheap](https://app.proxy-cheap.com/r/JysUiH)
3. [Infatica](https://dashboard.infatica.io/aff.php?aff=544)
# Setup Tutorial
- Install Python For Windows: [Python](https://www.python.org/ftp/python/3.13.0/python-3.13.0-amd64.exe)
- For Unix: ``apt install python3 python3-pip -y``
- Download this script: [ProXer](https://github.com/im-hanzou/ProXer/archive/refs/heads/main.zip) or ``git clone https://github.com/im-hanzou/ProXer``
- Open your Terminal/CMD and make sure you at ProXer directory
- Installing requirements:
>Windows
```bash
python -m pip install -r requirements.txt
```
>Unix
```bash
python3 -m pip install -r requirements.txt
```
# Run
- Run the script:
>Windows
```bash
python main.py
```
>Unix
```bash
python3 main.py
```
>You can try main-v2.py for better performance
- Insert your proxies filename
>Supported Format
```bash
http://host:port
http://user:pass@host:port
socks4://host:port
socks4://user:pass@host:port
socks5://host:port
socks5://user:pass@host:port
```
- Proxies result will saved to folder named ``proxy_results``
- Good Proxies will saved to ``good-proxies.txt``
- Bad Proxies will saved to ``bad-proxies.txt``
### Run this bot at your own risk, I'm not responsible for any loss or damage caused by this bot. This bot is for educational purposes only.
