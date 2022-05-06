import concurrent.futures
import json

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
bPayloadTest = False
bFrontPayload = False
bFrontPayload_List = False
bBackPayload = False
bBackPayload_List = False
bCSRF_param = False
bPOST_param = False

while mode_not_selected:
    print("1. Single-level Directory Scan")
    print("2. Recursive Directory Scan")
    print("3. Payload Test")
    mode_selection = input("Select a mode:")
    if mode_selection == "1" or mode_selection == "2" or mode_selection == "3" or mode_selection == "4" or mode_selection == "5":
        mode_not_selected = False

if mode_selection == "2":
    bRecursive = True
    levels_of_recursion = int(input("Enter the levels of recursion:"))
elif mode_selection == "3":
    bPayloadTest = True


recursion_dict = {}
if bRecursive:
    for i in range(1, levels_of_recursion + 1):
        recursion_dict[str(i)] = []
else:
    recursion_dict[str(1)] = []

domain = ""
if not bPayloadTest:
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
        bad_requests = [403, 404]
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
else:
# ===================== CHOOSE PAYLOAD TYPE ===================== #
    a = True
    while a:
        bURL_param = input("Is the target for the payload test in the url?(y,n)")
        if bURL_param != "y" and bURL_param != "n":
            pass
        else:
            a = False
            break

        bPOST_param = input("Is target POST data?")
        if bPOST_param != "y" and bURL_param != "n":
            pass
        else:
            a = False
            break


# ===================== CHOOSE PAYLOAD TYPE ===================== #


# ===================== CHOOSE PAYLOAD OPTIONS ===================== #
    if bURL_param == "y":
        print("\nProceeding with url payload...\n")
        a = True
        while a:
            payload_target = input("Enter the target url with %payload% where the payload test should go:\n")
            test = payload_target.count("%")
            if test != 2:
                print("Invalid target url. Please ensure you are using the following syntax: www.hackme.com/test.php?c=%payload%")
            else:
                a = False
        bURL_param = True

    elif bPOST_param == "y":
        print("\n\nNOTE: Jackhammer only supports POST requests when testing forms\n\n")
        a = True
        while a:
            prompt = input("Does the form have a CSRF token?")
            if prompt == "y":
                bCSRF_param = True
                a = False
            elif prompt == "n":
                a = False
                break
        print('\nUSE FORMAT: {"Parameter": "%payload%", "Parameter2": "Static Value"}\nENSURE THE USE OF DOUBLE QUOTES\n')
        a = True
        while a:
            payload = input("Enter form parameters:")
            try:
                form_payload = json.loads(payload)
                a = False
            except Exception as e:
                print(f"INVALID PAYLOAD: {e}")

    a = True
    while a:
        prompt = input("Would you like to include a anything pre-payload?(y,n)")
        if prompt == "y":
            a = False
            print("\n1. Use static values")
            print("2. Iterate a list values")
            b = True
            while b:
                prompt = input("Select a pre-payload option:")
                if prompt == "1":
                    pre_payload = input("Enter pre-payload static characters:")
        elif prompt == "n":
            a = False
            pass

    a = True
    while a:
        prompt = input("Would you like to include a anything post-payload?(y,n)")
        if prompt == "y":
            a = False
            print("\n1. Use static values")
            print("2. Iterate a list values")
            b = True
            while b:
                prompt = input("Select a post-payload option:")
                if prompt == "1":
                    pre_payload = input("Enter post-payload static characters:")
        elif prompt == "n":
            a = False
            pass
# ===================== CHOOSE PAYLOAD OPTIONS ===================== #






print(r"""
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
$$   _            _    _                                         $$
$$  (_)          | |  | |                                        $$
$$   _  __ _  ___| | _| |__   __ _ _ __ ___  _ __ ___   ___ _ __ $$
$$  | |/ _` |/ __| |/ / '_ \ / _` | '_ ` _ \| '_ ` _ \ / _ \ '__|$$
$$  | | (_| | (__|   <| | | | (_| | | | | | | | | | | |  __/ |   $$
$$  | |\__,_|\___|_|\_\_| |_|\__,_|_| |_| |_|_| |_| |_|\___|_|   $$
$$ _/ |                                                          $$
$$|__/                       By 0xc013                           $$
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
""")
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
        new_list = []
        if "<form" in response.text:
            new_list.append("<<<<FORM FOUND IN THIS PAGE>>>>")
        list = re.findall(href_extract, response.text)
        list = list + re.findall(src_extract, response.text)
        directory = "/".join(url.split("/")[3:]) + "/"
        for i in range(len(list)):
            if list[i][0] == "h":
                if "http" not in list[i]:
                    if list[i][6:-1] != "/":
                        new_list.append(list[i][6:-1])
            elif list[i][0] == "s":
                if "http" not in list[i]:
                    if list[i][5:-1] != "/":
                        new_list.append(list[i][5:-1])
            elif domain in list[i]:
                new_list.append(list[i])
        if len(new_list) > 0:
            extracted_data[directory] = new_list
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

        f.write("\n\n#===========EXTRACTED PAGE ARTIFACTS===========#\n")
        for key in extracted_data:
            try:
                f.write(key + ":\n")
                for item in extracted_data[key]:
                    f.write(f"\t{item}\n")
            except Exception:
                pass

        f.write(f'\nTotal Requests: {counter}\n')
        print(f'Finished! Results saved to {output_file}')
# =========== SAVE OUTPUT TO FILE =========== #


# ============================ MAIN LOOP ============================ #
if not bPayloadTest:
    for i in recursion_dict:
        try:
            if i == str(1):
                target = target
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(send_request, directory_list)
            else:
                for dir in recursion_dict[str(int(i) - 1)]:
                    saved = target
                    target = saved + dir
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.map(send_request, directory_list)
                    target = saved
        except Exception as e:
            print(f"Unexpected exception: {e}")
            break
else:

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


