import requests
import os
import sys
import time
from urllib.parse import urlparse
from colorama import init, Fore, Style
from multiprocessing import Process, Queue, Manager, Value, Lock, freeze_support
import multiprocessing as mp
import ctypes
import warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

init(autoreset=True)

def check_single_proxy(proxy_url):
    try:
        parsed_url = urlparse(proxy_url)
        proxy_type = parsed_url.scheme.lower()
        if proxy_type not in ['http', 'https', 'socks4', 'socks5']:
            proxy_type = 'http'
            
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        
        session = requests.Session()
        session.verify = False
        
        ip_response = session.get('https://api64.ipify.org/?format=json', 
                                proxies=proxies, 
                                timeout=10)
        ip_data = ip_response.json()
        ip_address = ip_data.get('ip')
        
        if not ip_address:
            return None
        
        proxy_details_response = session.get(
            f'https://proxycheck.io/v2/{ip_address}?vpn=1&asn=1',
            proxies=proxies,
            timeout=10
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
    except:
        return None
    finally:
        session.close()

def worker(proxy_chunk, result_queue, progress_queue, total_proxies):
    for proxy in proxy_chunk:
        if proxy.strip():
            result = check_single_proxy(proxy)
            if result:
                result_queue.put(result)
            progress_queue.put(proxy)

class ProxyChecker:
    def __init__(self):
        self.proxy_results_dir = 'proxy_results'
        os.makedirs(self.proxy_results_dir, exist_ok=True)
        self.num_processes = mp.cpu_count()
        self.lock = Lock()

    def print_banner(self):
        banner = f"""{Fore.CYAN}
  , __           _                
 /|/  \\         (_\\  /            
  |___/ ,_    __   \\/    _   ,_   
  |    /  |  /  \\_ /\\   |/  /  |  
  |       |_/\\__/_/  \\_/|__/   |_/
                                  
                                  
{Fore.WHITE}Static Proxy Quality Checker v2 - IM-Hanzou{Style.RESET_ALL}
"""
        print(banner)

    def write_proxy_result(self, result):
        if result['proxy_status'].lower() == 'yes':
            filename = "bad-proxies.txt"
            color = Fore.RED
        else:
            filename = "good-proxies.txt"
            color = Fore.GREEN

        filepath = os.path.join(self.proxy_results_dir, filename)
        
        with self.lock:
            with open(filepath, 'a') as f:
                f.write(f"{result['proxy_url']}\n")
            
            print(f"\n{color}✔ {result['proxy_url']} | {result['ip']} | {result['country']} | {result['provider']}{Style.RESET_ALL}")

    def chunks(self, lst, n):
        avg = len(lst) // n
        remainder = len(lst) % n
        result = []
        i = 0
        for _ in range(n):
            chunk_size = avg + 1 if remainder > 0 else avg
            result.append(lst[i:i + chunk_size])
            i += chunk_size
            remainder = max(0, remainder - 1)
        return result

    def process_proxy_list(self, input_file):
        try:
            with open(input_file, 'r') as f:
                proxies = f.read().splitlines()
        except FileNotFoundError:
            print(f"{Fore.RED}File not found: {input_file}{Style.RESET_ALL}")
            return

        total_proxies = len(proxies)
        start_time = time.time()

        result_queue = Queue()
        progress_queue = Queue()

        proxy_chunks = self.chunks(proxies, self.num_processes)
        
        processes = []
        for chunk in proxy_chunks:
            p = Process(target=worker, args=(chunk, result_queue, progress_queue, total_proxies))
            processes.append(p)
            p.start()

        processed_count = 0
        while processed_count < total_proxies:
            while not result_queue.empty():
                result = result_queue.get()
                self.write_proxy_result(result)

            while not progress_queue.empty():
                proxy = progress_queue.get()
                processed_count += 1
                sys.stdout.write(f"\r{Fore.YELLOW}Processing: [{processed_count}/{total_proxies}] {proxy}{Style.RESET_ALL}")
                sys.stdout.flush()

            time.sleep(0.1) 

        for p in processes:
            p.join()

        while not result_queue.empty():
            result = result_queue.get()
            self.write_proxy_result(result)

        end_time = time.time()
        print(f"\n{Fore.CYAN}===== Checking Complete ====={Style.RESET_ALL}")
        print(f"{Fore.GREEN}Total Proxies: {total_proxies}")
        print(f"{Fore.YELLOW}Time Taken: {end_time - start_time:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Processes Used: {self.num_processes}{Style.RESET_ALL}")

    def main(self):
        self.print_banner()

        while True:
            try:
                input_file = input(f"{Fore.CYAN}Proxy list filename: {Style.RESET_ALL}").strip()
                
                if not os.path.exists(input_file):
                    print(f"{Fore.RED}File not found. Please try again.{Style.RESET_ALL}")
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
    warnings.filterwarnings('ignore')
    
    freeze_support()
    try:
        checker = ProxyChecker()
        checker.main()
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
