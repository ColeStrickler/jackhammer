bad_requests = input("Enter HTTP status codes to ignore separated by ',' or press [ENTER] to ignore default=404:")
bad_requests = bad_requests.split(',')
if bad_requests[0] == "":
    bad_requests = [404]
else:
    for i in range(len(bad_requests)):
        print(i)
        bad_requests[i] = int(bad_requests[i])
print(bad_requests)
