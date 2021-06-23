import csv
import datetime
import os, sys
import time
import validators
from PIL import Image
import math

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import selenium.common.exceptions

from urllib.parse import urlparse

folder_path = os.getcwd()

url_path = folder_path + '\\websitelist\\top-1m.csv'
info_path = folder_path + '\\stats\\NIGHTvpnsession'

s = datetime.datetime.now()
session = "mo" + s.strftime("%m") + "_d" + s.strftime("%d") + "_h"+ s.strftime("%H") + "_mi"+ s.strftime("%M")
stats_path = info_path + session + '/stats'
good_connection_path = info_path + session + '/good_connection.csv'
error_path = info_path + session + '/errors.csv'
screenshot_path = info_path + session + '/screenshots'
os.mkdir(info_path+session)
os.mkdir(screenshot_path)

#putting the domains from the website list into two list:
# 1: check for both main page and 3 sub pages (urls)
# 2: check for only main page (add_urls)
def websitelist(url_path, n, m, skip):
    urls = []
    add_urls = []
    with open(url_path) as csv_file:
        reader = csv.reader(csv_file)
        for i, url in enumerate(reader):
            if i < skip:
                continue
            if i < n:
                    urls.append("http://" + url[1])
            elif i < m:
                add_urls.append("http://" + url[1])
            else:
                return (urls, add_urls)
    return (urls, add_urls)

#initial statistic values
good_connections = 0
errors_main = 0
    
additional_links = 0
errors_add = 0
good_addconnections = 0

good_connectionsex = 0
errors_mainex = 0

skip = 0
n = 500
m = 1500
size_of_session = 50
size_of_extra_session = 250

urls = websitelist(url_path, n, m, skip)

sub_urls = urls[0]
add_urls = urls[1]

#getting the exception type for the exception given
def getExceptionType(e):
    msg = str(e)
    if "net::ERR_NAME_NOT_RESOLVED" in msg:
        return "DNS"
    elif "timeout"in msg:
        return "TIMEOUT"
    elif "net::ERR_CONNECTION_REFUSED" in msg:
        return "REFUSED"
    elif "net::ERR_CONNECTION_RESET" in msg:
        return "RESET"
    else:
        return "UNKNOWN"

#parse method for pages with both main pages and 3 additional pages
def parse(url, driver, good_connection_writer, error_file_writer):
    try:
        global good_connections
        global errors_main
        global additional_links
        global errors_add
        global good_addconnections
        try:
            #requesting the page
            driver.get(url)
        except TimeoutException:
            pass
        except Exception as e:
            #error occured, thus writing it into statistics
            errors_main = errors_main + 1
            error_file_writer.writerow(["main",url, getExceptionType(e)])
            driver.delete_all_cookies()
            return 

        #taking screenshot of main page        
        domain = screenshot_path + '/' + urlparse(url).netloc + '.png'

        try:
            time.sleep(3)
            driver.save_screenshot(domain)
        except Exception as e:
            errors_main = errors_main + 1
            error_file_writer.writerow(["main",url, getExceptionType(e)])
            driver.delete_all_cookies()
            return 
        
        good_connections = good_connections + 1

        #extracting links from main page
        poslinks = []
        links = []
        try:
            links = driver.find_elements_by_xpath(".//a")
        except:
            good_connection_writer.writerow(["main",url,"links: " + str(0)])
            driver.delete_all_cookies()
            return 
        
        for link in links:
            try:
                poslinks.append(link.get_attribute("href"))
            except:
                continue

        good_connection_writer.writerow(["main",url,"links: " + str(len(poslinks))])

        if len(poslinks) == 0:
            driver.delete_all_cookies()
            return

        #checking whether links are valid 
        num_of_links = min(3, len(poslinks))
        
        i = 0
        j = 0
        links_to_follow= []
        while i < len(poslinks) and j < num_of_links:
            if isinstance(poslinks[i], str):
                if poslinks[i] != urlparse(url).netloc and validators.url(poslinks[i]):
                    if poslinks[i] != "www." + urlparse(url).netloc:
                        j = j + 1
                        links_to_follow.append(poslinks[i])
            i = i + 1

        additional_links = additional_links + len(links_to_follow)
        #loading all subpages, taking their screenshots and writing statistics accordingly
        j = 0
        for link in links_to_follow:
            try:
                driver.get(link)
                time.sleep(3)
            except TimeoutException:
                pass
            except Exception as e:
                errors_add = errors_add + 1
                error_file_writer.writerow(["subpage", url + str(j), getExceptionType(e)])
                continue
                
            domain = screenshot_path + "/" + urlparse(url).netloc + str(j) + ".png"
            j = j + 1

            try:
                driver.save_screenshot(domain)
            except Exception as e:
                errors_add = errors_add + 1
                error_file_writer.writerow(["subpage",url + str(j), getExceptionType(e)])
                continue
                
            good_addconnections = good_addconnections + 1

            good_connection_writer.writerow(["subpage", url + str(j)])

        #after page is finished, delete cookies
        driver.delete_all_cookies()
    except Exception as e:
        return 

    
#method for pages where only the main page is requested
def parseadd(url, driver, good_connection_writer, error_file_writer):
    try:
        
        global good_connectionsex
        global errors_mainex

        try:
            #requesting page
            driver.get(url)
        except TimeoutException:
            pass
        except Exception as e:
            errors_mainex = errors_mainex + 1
            error_file_writer.writerow(["extra", url, getExceptionType(e)])
            driver.delete_all_cookies()
            return

        #taking screenshot of main page        
        domain = screenshot_path + '/' + urlparse(url).netloc + '.png'

        try:
            driver.save_screenshot(domain)
        except Exception as e:
            errors_mainex = errors_mainex + 1
            error_file_writer.writerow(["extra", url, getExceptionType(e)])
            driver.delete_all_cookies()
            return
            
        good_connectionsex = good_connectionsex + 1

        good_connection_writer.writerow(["extra", url])


        driver.delete_all_cookies()
    except Exception as e:
        return

#method to write the statistics
def write(session_number, n):
    global good_connections
    global errors_main
    global additional_links
    global errors_add
    global good_addconnections
    global good_connectionsex
    global errors_mainex
    global s

    end_time = datetime.datetime.now()
    difference = end_time - s
    d = divmod(difference.total_seconds(), 60)

    with open(stats_path + str(session_number) + ".csv", 'a+', newline='') as file:
        writer = csv.writer(file, delimiter = ',')
        writer.writerow(["Session number", session_number])
        writer.writerow(["Total original pages", n])
        writer.writerow(["Good connections", good_connections])
        writer.writerow(["Errors on main page", errors_main])

        writer.writerow(["Total sub pages", additional_links])
        writer.writerow(["Good subpage connections", good_addconnections])
        writer.writerow(["Errors on sub page", errors_add])

        writer.writerow(["Total extra pages", m - n])
        writer.writerow(["Good extra pages", good_connectionsex])
        writer.writerow(["Error on extra page", errors_mainex])
        writer.writerow(["Time spend:", "minutes:" + str(d[0]), "seconds: " + str(d[1])]) 
                
        file.close()


#settings for the chrome webdriver
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.prompt_for_download": False,
    "download_restrictions":3,
}
chrome_options.add_experimental_option(
    "prefs", prefs
)
chrome_options.add_extension(folder_path + '\\extensions\\cookies.crx')
chrome_options.add_extension(folder_path + '\\extensions\\adblocker.crx')
chrome_options.add_argument('--window-size=900,550')


#the crawling session is partitioned into sessions for the purpose of having intermediate results and being able to reduce impact if problems occur
num_of_sessions = math.floor((n - skip) / size_of_session)
num_of_extra_sessions = math.floor((m-n)/size_of_extra_session)

print("num of sessions" + str(num_of_sessions))
print("num of extra sessions" + str(num_of_extra_sessions))

#going through the list of pages and running the crawler on them
if num_of_sessions > 0 :
    for i in range(0, num_of_sessions):
        good_connection_file = open(good_connection_path, 'a+', newline='')
        good_connection_writer = csv.writer(good_connection_file)
        error_file = open(error_path, 'a+', newline='')
        error_file_writer = csv.writer(error_file)
        retry = 0
        stopped = True
        while stopped:
            try:
                driver = webdriver.Chrome(options = chrome_options)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)
                driver.implicitly_wait(30)
                time.sleep(3)
                for j in range(0, size_of_session):
                    if (i*size_of_session + j) < len(sub_urls):
                        parse(sub_urls[i*size_of_session + j], driver, good_connection_writer, error_file_writer)
                driver.quit()
                write(i, n)
            except:
                driver.quit()
                if retry > 2:
                    stopped = False
                retry = retry + 1
                continue
            break
        good_connection_file.close()
        error_file.close()

if num_of_extra_sessions > 0 :
    for i in range(0, num_of_extra_sessions):
        good_connection_file = open(good_connection_path, 'a+', newline='')
        good_connection_writer = csv.writer(good_connection_file)
        error_file = open(error_path, 'a+', newline='')
        error_file_writer = csv.writer(error_file)
        retry = 0
        stopped = True
        while stopped:
            try:
                driver = webdriver.Chrome(options = chrome_options)
                driver.set_page_load_timeout(30)
                driver.set_script_timeout(30)
                time.sleep(3)
                for j in range(0, size_of_extra_session):
                    if (i * size_of_extra_session + j) < len(add_urls): 
                        parseadd(add_urls[i*size_of_extra_session + j], driver, good_connection_writer, error_file_writer)

                driver.quit()
                write(num_of_sessions + i, n)
            except:
                driver.quit()
                if retry > 2:
                    stopped = False
                retry = retry + 1
                continue
            break
        good_connection_file.close()
        error_file.close()
        

        






