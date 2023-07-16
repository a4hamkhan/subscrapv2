import threading
import subprocess
import os
import sys

domain_with_backslash = sys.argv[1].replace(".", "\\.")
fetch_data_completed = threading.Event()  
command3_completed = threading.Event()  
command7_completed = threading.Event()  
#gt_token = YOUR GITHUB TOKEN HERE

def create_directories():
    os.makedirs(".output/webarc", exist_ok=True)
    os.makedirs(".output/domains", exist_ok=True)
    print("Directories created - Done")
    fetch_data_completed.set() 

def fetch_data():
    fetch_data_completed.wait() 
    subprocess.run(
        "curl 'https://web.archive.org/cdx/search/cdx?url=*."+sys.argv[1]+"&output=text&fl=original&collapse=urlkey&from=' > .output/webarc/output.txt 2>/dev/null",
        shell=True
    )
    print("Fetch data - Done")

def command3():
    os.makedirs(".output/domains", exist_ok=True) 
    subprocess.run(
        "github-subdomains -d "+sys.argv[1]+" -t "+gt_token+" | grep '\."+domain_with_backslash+"' | awk '{print $2}' > .output/domains/2.txt 2>/dev/null ; rm -r "+sys.argv[1]+".txt",
        shell=True
    )
    print("Command 3 - Done")
    command3_completed.set()  

def command4():
    command3_completed.wait()  
    subprocess.run(
        "crt -s -json "+sys.argv[1]+" | jq -r \'.[].subdomain\' | sed -e 's/^\\*\\.//' > .output/domains/3.txt 2>/dev/null",
        shell=True
    )
    print("Command 4 - Done")

def command5():
    fetch_data_completed.wait()  
    subprocess.run(
        "cat .output/webarc/output.txt | unfurl --unique domains > .output/domains/6.txt 2>/dev/null",
        shell=True
    )
    print("Command 5 - Done")
    
def command6():
    command3_completed.wait()  
    subprocess.run(
        "cat .output/domains/*.txt | grep '"+domain_with_backslash+"' | sort -u > .output/domains/domains.txt 2>/dev/null",
        shell=True
    )
    print("Command 6 [domains saved in a file] - Done")

def command7():
    command3_completed.wait() 
    subprocess.run(
        "amass enum -passive -norecursive -noalts -silent -d "+sys.argv[1]+" -config ~/.config/amass/config.ini -o .output/domains/7.txt",
        shell=True
    )
    print("Command 7 - Done")
    command7_completed.set() 


thread_create_directories = threading.Thread(target=create_directories)
thread_fetch_data = threading.Thread(target=fetch_data)
thread_command3 = threading.Thread(target=command3)
thread_command4 = threading.Thread(target=command4)
thread_command5 = threading.Thread(target=command5)
thread_command6 = threading.Thread(target=command6)
thread_command7 = threading.Thread(target=command7)

thread_create_directories.start()
thread_fetch_data.start()
thread_command3.start()
thread_command4.start()
thread_command5.start()
thread_command7.start()

thread_command3.join()
thread_command7.join()

thread_command6.start()

thread_create_directories.join()
thread_fetch_data.join()
thread_command4.join()
thread_command5.join()
thread_command6.join()

print("All processes completed")
