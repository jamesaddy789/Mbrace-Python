##Written by James Curtis Addy

import ftplib
import re
import os

def mbrace_ftp_connect():
    try:
        ftp = ftplib.FTP('ftp.mbrace.xyz')
        ftp.login('u305816916.datacollector','getdata')   
        return ftp
    except ftplib.all_errors as e:
        print(e)
        return None
    
def list_all():
    ftp = mbrace_ftp_connect()
    directory_list = []
    directory_list = ftp.nlst()
    ftp.quit()    
    sort_dict = {}
    for file in directory_list:   
        if file.endswith('.bin'):
            date = re.search(r"\d{4}-\d{2}-\d{2}", file)           
            if date == None : continue
            sort_dict[date.group()] = file
           
    for key in sorted(sort_dict.keys()):
        print(sort_dict[key])
        
def operate_file_download():
    download_directory = "Mbrace Data Files"
    if not os.path.exists(download_directory):
        os.mkdir(download_directory)
        print("Directory " + download_directory + " created.")
    file_to_download = input("\nCopy and paste name of file to download :")
    local_name = file_to_download.replace(':', '_')
    local_file_path = download_directory + "/" + local_name
    local_file = open(local_file_path, 'wb')
    ftp = mbrace_ftp_connect()
    if ftp != None:
        ftp.retrbinary("RETR " + file_to_download ,local_file.write)
        local_file.close()
        ftp.quit()
    print("Downloaded " + file_to_download + " to: \n" + local_file_path)

while True:
    list_all()
    operate_file_download()   
    restart = input("Enter r/R to restart:")
    if restart is not "r" and restart is not "R": break



