import requests, os, sys, time, re, random
from cfonts import render
from concurrent.futures import ThreadPoolExecutor

# Colors
R = '\033[1;31m' # Red
G = '\033[1;32m' # Green
Y = '\033[1;33m' # Yellow
B = '\033[1;34m' # Blue
W = '\033[1;37m' # White
P = '\033[1;35m' # Purple

accounts = [] 
deleted_count = 0
failed_count = 0

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def logo():
    clear()
    print(P + "┌" + "─"*58 + "┐")
    print(render(' FAYSAL ', colors=['magenta', 'cyan'], align='center', font='block'))
    print(P + "└" + "─"*58 + "┘")
    print(f" {B}» {W}Developer : {G}FAYSAL Saidi")
    print(f" {B}» {W}System    : {G}Infinite Turbo Cleaner")
    print(f" {B}» {W}Order     : {G}Newest to Oldest")
    print(f" {B}» {W}Status    : {P}Ready to Work")
    print(P + "─"*60)

def add_accounts():
    global accounts
    logo()
    try:
        num = int(input(f"{W} [?] How many accounts to add: {G}"))
        for i in range(num):
            print(f"\n{Y} [~] Setup Account #{i+1}:")
            cookie = input(f"{W} [?] Enter Account Cookies: {G}").strip()
            
            head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Cookie': cookie}
            print(f"{Y} [~] Extracting token & verifying...")
            
            res = requests.get('https://business.facebook.com/business_locations', headers=head)
            token_match = re.search('(EAAG\w+)', res.text)
            
            if token_match:
                token = token_match.group(1)
                verify_url = f"https://graph.facebook.com/v19.0/me?access_token={token}"
                verify_res = requests.get(verify_url, cookies={'cookie': cookie}).json()
                
                if 'id' in verify_res:
                    name = verify_res.get('name', 'Unknown')
                    accounts.append({'token': token, 'cookie': cookie})
                    print(f"{G} [✓] Success! Account Linked: {W}{name}")
                else:
                    print(f"{R} [×] Token found but Cookies expired.")
            else:
                print(f"{R} [×] Failed to extract token.")
        time.sleep(2)
    except Exception as e:
        print(f"{R} [!] Input Error: {e}")

def delete_process(data):
    global deleted_count, failed_count
    post_id = data['post_id']
    post_date = data['date']
    acc = data['acc']
    
    try:
        # Anti-Ban delay
        time.sleep(random.uniform(0.3, 0.8))
        
        url = f"https://graph.facebook.com/v19.0/{post_id}"
        res = requests.delete(url, params={'access_token': acc['token']}, 
                             cookies={'cookie': acc['cookie']}, timeout=15).json()
        
        if res.get('success'):
            deleted_count += 1
            sys.stdout.write(f"\r {W}[+] Deleted Date: {Y}{post_date} {W}| Total: {G}{deleted_count} {W}")
            sys.stdout.flush()
        else:
            failed_count += 1
    except:
        failed_count += 1

def start_turbo_cleaning():
    global accounts, deleted_count, failed_count
    if not accounts:
        print(f"{R} [!] Please add accounts first!"); time.sleep(2); return

    logo()
    print(f"{Y} [!] Tip: Use Numeric Group ID for best results.")
    group_id = input(f"{W} [?] Group ID or URL: {G}").strip()
    
    if 'groups/' in group_id:
        group_id = group_id.split('groups/')[1].split('/')[0].split('?')[0]

    next_page_url = f"https://graph.facebook.com/v19.0/{group_id}/feed?fields=id,created_time&limit=50&access_token={accounts[0]['token']}"

    print(f"\n{P} [🚀] Starting Infinite Cleaning Mode...")
    print(f"{P} " + "─"*60)
    
    try:
        while next_page_url:
            res = requests.get(next_page_url, cookies={'cookie': accounts[0]['cookie']}).json()
            
            if 'error' in res:
                print(f"\n{R} [!] FB Error: {res['error'].get('message')}")
                break

            if 'data' not in res or not res['data']:
                print(f"\n{G} [✓] All posts have been cleared.")
                break

            tasks = []
            for i, item in enumerate(res['data']):
                post_id = item['id']
                raw_date = item.get('created_time', 'Unknown')
                clean_date = raw_date.split('T')[0] if 'T' in raw_date else raw_date
                
                acc = accounts[i % len(accounts)]
                tasks.append({'post_id': post_id, 'date': clean_date, 'acc': acc})

            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.map(delete_process, tasks)

            next_page_url = res.get('paging', {}).get('next')
                
    except KeyboardInterrupt:
        print(f"\n{Y} [!] Process stopped by user.")
    except Exception as e:
        print(f"\n{R} [!] Error: {e}")

    print(f"\n{G} [✓] Done! {deleted_count} Deleted | {failed_count} Failed.")
    input(f"{W} Press Enter to back...")

def main():
    while True:
        logo()
        print(f"{W} [1] Add & Verify Accounts")
        print(f"{W} [2] Start Infinite Turbo Cleaning")
        print(f"{W} [0] Exit")
        c = input(f"\n{B} [?] Choice: {G}")
        if c == '1': add_accounts()
        elif c == '2': start_turbo_cleaning()
        elif c == '0': break

if __name__ == "__main__":
    main()
