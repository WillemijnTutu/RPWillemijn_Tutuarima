import PIL
from PIL import Image
import imagehash
import os
import csv
import math


folder_path = os.getcwd() + "/results/15 June"
control_path = folder_path + "/control/NIGHTcontrolsessionmo06_d14_h23_mi49/screenshots"
vpn_path = folder_path + "/vpn/NIGHTvpnsessionmo06_d16_h08_mi42/screenshots"

control_files = os.listdir(control_path)
vpn_files = os.listdir(vpn_path)

#firstly for all main pages the difference in p hash value is calculated
file = open(folder_path + "/differencesmainresize.csv", "a+", newline='')
writer = csv.writer(file)
good_links = 0
stats = []
stats.append(["0-10", 0])
stats.append(["10-20", 0])
stats.append(["20-30", 0])
stats.append(["30-40", 0])
stats.append(["40-50", 0])
stats.append(["50-60", 0])
stats.append(["60-70", 0])
stats.append(["70-80", 0])
stats.append(["80-90", 0])
stats.append(["90-100", 0])
not_found = 0

subpages = 0
mainpages = 0
urls = []
#calculating the p value for both images and documenting the difference
for name in vpn_files:
    if name.endswith("0.png") or name.endswith("1.png") or name.endswith("2.png"):
        continue
    if name in control_files:
        good_links = good_links + 1
        first_image = Image.open(control_path + "/" + name)
        first_image_resize = first_image.resize((804,418))
        first_hash = imagehash.phash(first_image_resize)
        second_hash = imagehash.phash(PIL.Image.open(vpn_path + "/" + name))
        diff = abs(first_hash - second_hash)
        i = math.floor(diff/10)
        stats[i][1] = stats[i][1] + 1
        urls.append((name,diff))
    else:
        not_found = not_found + 1
        writer.writerow([name,"not found"])

urls_sorted = sorted(urls, key= lambda x: x[1])

for url in urls_sorted:
    writer.writerow([url[0], str(url[1])])


writer.writerow(["total links", good_links])
for row in stats:
    writer.writerow([row[0], str(row[1])])

writer.writerow(["not found", not_found])

file.close()




#after, the same is done for the subpages

file = open(folder_path + "/differencessubresize.csv", "a+", newline='')
writer = csv.writer(file)
good_links = 0
stats = []
stats.append(["0-10", 0])
stats.append(["10-20", 0])
stats.append(["20-30", 0])
stats.append(["30-40", 0])
stats.append(["40-50", 0])
stats.append(["50-60", 0])
stats.append(["60-70", 0])
stats.append(["70-80", 0])
stats.append(["80-90", 0])
stats.append(["90-100", 0])
not_found = 0
urls = []

subpages = 0
mainpages = 0
for name in vpn_files:
    if name.endswith("0.png") or name.endswith("1.png") or name.endswith("2.png"):
        if name in control_files:
            good_links = good_links + 1
            first_image = Image.open(control_path + "/" + name)
            first_image_resize = first_image.resize((804,418))
            first_hash = imagehash.phash(first_image_resize)
            second_hash = imagehash.phash(PIL.Image.open(vpn_path + "/" + name))
            diff = abs(first_hash - second_hash)
            i = math.floor(diff/10)
            stats[i][1] = stats[i][1] + 1
            urls.append((name,diff))
        else:
            not_found = not_found + 1
            writer.writerow([name,"not found"])

urls_sorted = sorted(urls, key= lambda x: x[1])

for url in urls_sorted:
    writer.writerow([url[0], str(url[1])])

writer.writerow(["total links", good_links])
for row in stats:
    writer.writerow([row[0], str(row[1])])
writer.writerow(["not found", not_found])

file.close()

