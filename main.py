import requests
import os
import sys
import time
import concurrent.futures
from urllib.parse import urlparse
from colorama import init, Fore, Style
from queue import Queue
import threading

init(autoreset=True)

class ProxyChecker:
    def __init__(self, max_workers=50):
        self.proxy_results_dir = 'proxy_results'
        os.makedirs(self.proxy_results_dir, exist_ok=True)
        self.max_workers = max_workers
        self.successful_proxies = Queue()
        self.lock = threading.Lock()

    def print_banner(self):
        banner = f"""{Fore.CYAN}
  , __           _                
 /|/  \\         (_\\  /            
  |___/ ,_    __   \\/    _   ,_   
  |    /  |  /  \\_ /\\   |/  /  |  
  |       |_/\\__/_/  \\_/|__/   |_/
                                  
                                  
{Fore.WHITE}Static Proxy Quality Checker - IM-Hanzou{Style.RESET_ALL}
"""
        print(banner)

    def detect_proxy_type(self, proxy_url):
        parsed_url = urlparse(proxy_url)
        proxy_type = parsed_url.scheme.lower()
        return proxy_type if proxy_type in ['http', 'https', 'socks4', 'socks5'] else 'http'

    def check_proxy(self, proxy_url):
        proxy_type = self.detect_proxy_type(proxy_url)
        
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        try:
            ip_response = requests.get('https://api64.ipify.org/?format=json', 
                                       proxies=proxies, 
                                       timeout=10,
                                       verify=False)
            ip_data = ip_response.json()
            ip_address = ip_data.get('ip')
            
            if not ip_address:
                return None
            
            proxy_details_response = requests.get(
                f'https://proxycheck.io/v2/{ip_address}?vpn=1&asn=1',
                proxies=proxies,
                timeout=10,
                verify=False
            )
            proxy_details = proxy_details_response.json()
            
            if proxy_details.get('status') == 'ok':
                ip_info = proxy_details.get(ip_address, {})
                return {
                    'ip': ip_address,
                    'asn': ip_info.get('asn', 'Unknown'),
                    'provider': ip_info.get('provider', 'Unknown'),
                    'organisation': ip_info.get('org', 'Unknown'),
                    'country': ip_info.get('country', 'Unknown'),
                    'proxy_status': ip_info.get('proxy', 'no'),
                    'type': ip_info.get('type', 'Unknown'),
                    'proxy_url': proxy_url,
                    'proxy_type': proxy_type
                }
            else:
                return None
        
        except:
            return None

    def process_proxy(self, proxy, total_proxies, processed_count):
        result = self.check_proxy(proxy)
        
        if not result:
            return None
        
        with self.lock:
            sys.stdout.write(f"\r{Fore.YELLOW}Processing: [{processed_count[0]}/{total_proxies}] {proxy}{Style.RESET_ALL}")
            sys.stdout.flush()
            processed_count[0] += 1
        
        return result

    def write_proxy_result(self, result):
        if result['proxy_status'].lower() == 'yes':
            filename = f"bad-proxies.txt"
            color = Fore.RED
        else:
            filename = f"good-proxies.txt"
            color = Fore.GREEN

        filepath = os.path.join(self.proxy_results_dir, filename)
        
        with open(filepath, 'a') as f:
            f.write(f"{result['proxy_url']}\n")
        
        print(f"\n{color}✔ {result['proxy_url']} | {result['ip']} | {result['country']} | {result['provider']}{Style.RESET_ALL}")

    def process_proxy_list(self, input_file):
        try:
            with open(input_file, 'r') as f:
                proxies = f.read().splitlines()
        except FileNotFoundError:
            return

        total_proxies = len(proxies)
        processed_count = [0]
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.process_proxy, proxy, total_proxies, processed_count): proxy 
                for proxy in proxies if proxy.strip()
            }

            for future in concurrent.futures.as_completed(future_to_proxy):
                result = future.result()
                if result:
                    self.write_proxy_result(result)

        end_time = time.time()
        print(f"\n{Fore.CYAN}===== Checking Complete ====={Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total Proxies: {total_proxies}")
        print(f"{Fore.YELLOW}Time Taken: {end_time - start_time:.2f} seconds{Style.RESET_ALL}")

    def main(self):
        self.print_banner()

        while True:
            try:
                input_file = input(f"{Fore.CYAN}Proxy list filename: {Style.RESET_ALL}").strip()
                
                if not os.path.exists(input_file):
                    continue

                self.process_proxy_list(input_file)
                
                continue_choice = input(f"{Fore.YELLOW}Process another proxies? (y/n): {Style.RESET_ALL}").strip().lower()
                if continue_choice != 'y':
                    break

            except KeyboardInterrupt:
                print(f"\n{Fore.RED}\nProcess terminated by user.{Style.RESET_ALL}")
                break

if __name__ == '__main__':
    requests.packages.urllib3.disable_warnings()
    try:
        checker = ProxyChecker()
        checker.main()
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
