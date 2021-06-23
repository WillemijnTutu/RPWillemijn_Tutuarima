import os
import csv
folder_path = os.getcwd() + "/results/15 June"
control_path = folder_path + "/control/NIGHTcontrolsessionmo06_d14_h23_mi49/errors.csv"
vpn_path = folder_path + "/vpn/NIGHTvpnsessionmo06_d16_h08_mi42/errors.csv"


#the code compares both lists of errors and documents whether for a domain,
#they are the same or different

file = open(folder_path + "/errordiff.csv", "a+", newline='')
writer = csv.writer(file)

diff = 0
same = 0
not_found = 0

diffsub = 0
samesub = 0
not_foundsub = 0

control_urls=[]

with open(control_path) as csv_file:
    control_file_reader = csv.reader(csv_file)
    for row in enumerate(control_file_reader):
        row = row[1]
        if row[0] == "stop":
            break
        if row[0] == "subpage":
            control_urls.append((row[1], row[2]))
        else:
            control_urls.append((row[1], row[2]))

with open(vpn_path) as csv_file:
    vpn_file_reader = csv.reader(csv_file)
    for row in vpn_file_reader:
        found = False
        if row[0] == "stop":
            break
        for control_row in control_urls:
            if row[0] == "subpage":
                if control_row[0] == row[1]:
                    if control_row[1] == row[2]:
                        samesub = samesub + 1
                        writer.writerow(["subpage", row[1], "same"])
                        found = True
                    else:
                        diffsub = diffsub + 1
                        found = True
                        writer.writerow(["subpage", row[1], "different"])
                else:
                    continue
            else:
                if control_row[0] == row[1]:
                    if control_row[1] == row[2]:
                        same = same + 1
                        found = True
                        writer.writerow(["main", row[1], "same"])
                    else:
                        diff = diff + 1
                        found = True
                        writer.writerow(["main", row[1], "different"])    
                else:
                    continue
        if found == False:
            if row[0] == "subpage":
                not_foundsub = not_foundsub + 1
                writer.writerow(["subpage", row[1], "not found"])
            else:
                not_found = not_found + 1
                writer.writerow(["main", row[1], "not found"])

writer.writerow(["main same", same])
writer.writerow(["main diff", diff])
writer.writerow(["main not found", not_found])
writer.writerow(["sub same", samesub])
writer.writerow(["sub diff", diffsub])
writer.writerow(["sub not found", not_foundsub])

file.close()


