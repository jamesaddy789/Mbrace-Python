##Written by James Curtis Addy

import ftplib

directory_list = []
try:
    ftp = ftplib.FTP('ftp.mbrace.xyz')
    ftp.login('u305816916.datacollector','getdata')   
    directory_list = ftp.nlst()
    ftp.close()   
except ftplib.all_errors as e:
    print(e)

bin_list = []
for file in directory_list:
    
    if file.endswith('.bin'):
        bin_list.append(file)

def list_from_date(date):
    found = False
    for file in bin_list:
        if file.endswith(date + ".bin"):
            found = True
            print(file)
    if not found:
        print("There is no file with that date.")
            
def list_all():
    sort_dict = {}
    for file in bin_list:
        f = file.split(".")
        d = f[0].split("_")    
        if len(d) < 2: continue
        date = d[1]
        split_date = date.split("-")
        if len(split_date) < 3: continue   
        sort_dict[date] = file

    for key in sorted(sort_dict.keys()):
        print(sort_dict[key])

def operate_file_search():
    print("\nEnter 1 to enter a specific date to search")
    print("Enter anything else to list all files sorted by date")
    list_type = input("Enter choice:")
    print("\n")
    if list_type == '1':
        date_to_search = input("Enter the date to search as YYYY-MM-DD:")
        list_from_date(date_to_search)
    else:
        list_all()
                        
while True:
    operate_file_search()
    print("\nEnter c/C to continue or anything else to exit.")
    keep_going = input("Enter choice:")
    if keep_going is not "c" and keep_going is not "C": break

        



