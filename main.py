import concurrent.futures
import requests
import re


# ========= Data structures to save to file ========= #
discovered_directories = []
extracted_data = {}
# ========= Data structures to save to file ========= #


# ============ SETTINGS AND STATISTICS ============= #
counter = 0
href_extract = re.compile('href="[A-Za-z0-9/\-_#.?:]*"')
src_extract = re.compile('src="[A-Za-z0-9/\-_#.?:]*"')
# ============ SETTINGS AND STATISTICS ============= #


# ================= EXTRACTION FUNCTIONS ================= #
def extract_domain(url):
    domain_extract = re.compile("[a-z]?[a-z]?[a-z]?\.?[A-Za-z0-9]*\.[a-zA-Z]*/?")
    tmp = url.split('/')
    found_domain = []
    for item in tmp:
        domain = re.findall(domain_extract, item)
        if len(domain) > 0:
            if domain[0][0:4] == "www.":
                found_domain = domain[0][4:]
            else:
                found_domain = domain[0]
    if len(found_domain) > 0:
        return found_domain[0]
    else:
        return ""


def extract(dir, response, href_ext, src_ext, domain=None):
    new_list = []
    list = re.findall(href_ext, response)
    list = list + re.findall(src_ext, response)
    for i in range(len(list)):
        if list[i][0] == "h":
            if "http" not in list[i]:
                new_list.append(list[i][6:-1])
        elif list[i][0] == "s":
            if "http" not in list[i]:
                new_list.append(list[i][5:-1])
        elif domain in list[i]:
            new_list.append(list[i])
    extracted_data[dir] = new_list
# ================= EXTRACTION FUNCTIONS ================= #


# =========== STARTUP/SCAN SETTINGS SELECTION =========== #
mode_not_selected = True
bRecursive = False
bInfoExtract = False
bPayloadTest = False

while mode_not_selected:
    print("1. Single-level Directory Scan")
    print("2. Recursive Directory Scan")
    print("3. Single-level scan with info extraction")
    print("4. Recursive scan with info extraction")
    print("5. Full scan with payload testing")
    mode_selection = input("Select a mode:")
    if mode_selection == "1" or mode_selection == "2" or mode_selection == "3" or mode_selection == "4" or mode_selection == "5":
        mode_not_selected = False

if mode_selection == "2":
    bRecursive = True
    levels_of_recursion = int(input("Enter the levels of recursion:"))
elif mode_selection == "3":
    bInfoExtract = True
elif mode_selection == "4":
    bInfoExtract = True
    bRecursive = True
elif mode_selection == "5":
    levels_of_recursion = int(input("Enter the levels of recursion:"))
    bRecursive = True
    bPayloadTest = True
    bInfoExtract = True
recursion_dict = {}
if bRecursive:
    for i in range(1, levels_of_recursion + 1):
        recursion_dict[str(i)] = []
else:
    recursion_dict[str(1)] = []

domain = ""
while len(domain) < 1:
    target = input("Enter the target URL:")
    if target[-1] != "/":
        target = target + "/"
    domain = extract_domain(url=target)


wordlist_selected = False
while not wordlist_selected:
    wordlist = input("Enter path to wordlist for directory bruteforcing:")
    try:
        with open(wordlist, "r") as f:
            directory_list = [i.strip('\n') for i in f]
            if len(directory_list) > 0:
                wordlist_selected = True
            else:
                print("Error: wordlist is empty")
    except Exception as e:
        print(f"Error opening wordlist: {e}")


bad_requests = input("Enter HTTP status codes to ignore separated by ',' or press [ENTER] to ignore default=404:")
bad_requests = bad_requests.split(',')
if bad_requests[0] == "":
    bad_requests = [403,404]
else:
    for i in range(len(bad_requests)):
        bad_requests[i] = int(bad_requests[i])
print(f'IGNORING: {bad_requests}')


output_file = input("If you would like to output the results to a file enter the path:")
if len(output_file) > 0:
    save_results = True
else:
    save_results = False
    output_file = "./results.txt"
# =========== STARTUP/SCAN SETTINGS SELECTION =========== #


# =========== REQUEST FUNCTION =========== #
def send_request(directory):
    url = target + directory
    # print(f'TESTING {url}')
    level = url.count("/") - 2
    response = requests.get(url)
    global counter
    counter += 1
    if response.status_code not in bad_requests:
        #extract(dir=directory,response=response, domain=domain, href_ext=href_extract, src_ext=src_extract)
        new_list = []
        list = re.findall(href_extract, response.text)
        list = list + re.findall(src_extract, response.text)
        print(list)
        directory = "/".join(url.split("/")[3:]) + "/"
        for i in range(len(list)):
            if list[i][0] == "h":
                if "http" not in list[i]:
                    new_list.append(list[i][6:-1])
            elif list[i][0] == "s":
                if "http" not in list[i]:
                    new_list.append(list[i][5:-1])
            elif domain in list[i]:
                new_list.append(list[i])
        if len(new_list) > 0:
            extracted_data[directory] = new_list
        print(f'NEW LIST: {new_list}')
        #print(extracted_data)
        print(f'[{response.status_code}]{url}')
        discovered_directories.append(url)
        recursion_dict[str(level)].append(directory)
        print(f'REQUESTS: {counter}')
# =========== REQUEST FUNCTION =========== #


# =========== SAVE OUTPUT TO FILE =========== #
def write_output():
    with open(output_file, "w") as f:
        f.write("#===========DISCOVERED DIRECTORIES===========#\n")
        for dir in discovered_directories:
            f.write(dir + "\n")

        f.write("#===========EXTRACTED DIRECTORIES===========#\n")
        for key in extracted_data:
            try:
                f.write(key + ":\n")
                for item in extracted_data[key]:
                    f.write(f"\t{item}\n")
            except Exception:
                pass

        f.write(f'\nTotal Requests: {counter}')
        print(f'Results saved to {output_file}')
# =========== SAVE OUTPUT TO FILE =========== #



# ============================ MAIN LOOP ============================ #
for i in recursion_dict:
    print(i)
    try:
        if i == str(1):
            target = target
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(send_request, directory_list)
        else:
            for dir in recursion_dict[str(int(i) - 1)]:
                saved = target
                target = saved + dir
                print(f'NEW TARGET: [{target}]')
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(send_request, directory_list)
                target = saved
    except Exception as e:
        print(f"Unexpected exception: {e}")
        break
# ============================ MAIN LOOP ============================ #



# ============================ SAVE OUTPUT ============================ #
if save_results:
    try:
        write_output()
    except Exception as e:
        print(f'Unable to write to specified location: {e}')
        print('Writing to ./results.txt instead')
        output_file = "./results.txt"
        write_output()
else:
    try:
        write_output()
    except Exception as e:
        print(f'Unable to write output: {e}')
# ============================ SAVE OUTPUT ============================ #

print(extracted_data)
