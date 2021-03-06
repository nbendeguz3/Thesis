from selenium import webdriver
import os
import json
import urllib2
import sys
import time

# adding path to geckodriver to the OS environment variable
# assuming that it is stored at the same path as this script
os.environ["PATH"] += os.pathsep + os.getcwd()
download_path = "dataset/"

class GoogleImageExtractor(object):
    def __init__(self):
        self.g_search_key_list = []

        self.image_dl_per_search = int

    def set_num_image_to_dl(self, num_image):
            self.image_dl_per_search = num_image

    def get_searchlist_fr_file(self, filename):

        file = open(filename, 'r')
        self.g_search_key_list = file.read().split("\n")

    def multi_search_download(self):
        for x in xrange(self.g_search_key_list.__len__()):
            self.single_search_download(x)

    def single_search_download(self, num_list):
        searchtext = self.g_search_key_list[num_list]
        num_requested = self.image_dl_per_search

        number_of_scrolls = num_requested / 400 + 1
        # number_of_scrolls * 400 images will be opened in the browser

        if not os.path.exists(download_path + searchtext.replace(" ", "_")):
            os.makedirs(download_path + searchtext.replace(" ", "_"))

        url = "https://www.google.co.in/search?hl=en&q=" + searchtext + "&source=lnms&tbm=isch"
        driver = webdriver.Firefox()
        driver.get(url)

        headers = {}
        headers[
            'User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        extensions = {"jpg", "jpeg", "png"}
        img_count = 0
        downloaded_img_count = 0

        for _ in xrange(number_of_scrolls):
            for __ in xrange(10):
                # multiple scrolls needed to show all 400 images
                driver.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(0.2)
            # to load next 400 images
            time.sleep(0.5)
            try:
                driver.find_element_by_xpath("//input[@value='Show more results']").click()
            except Exception as e:
                print "Less images found:", e
                break

        imges = driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
        print "Total images:", len(imges), "\n"
        for img in imges:
            img_count += 1
            img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
            img_type = json.loads(img.get_attribute('innerHTML'))["ity"]
            print "Downloading image", img_count, ": ", img_url
            try:
                if img_type not in extensions:
                    img_type = "jpg"
                req = urllib2.Request(img_url, headers=headers)
                raw_img = urllib2.urlopen(req).read()
                f = open(
                    download_path + searchtext.replace(" ", "_") + "/" + str(downloaded_img_count) + "." + img_type,
                    "wb")
                f.write(raw_img)
                f.close
                downloaded_img_count += 1
            except Exception as e:
                print "Download failed:", e
            finally:
                print
            if downloaded_img_count >= num_requested:
                break

        print "Total downloaded: ", downloaded_img_count, "/", img_count
        driver.quit()


if __name__ == "__main__":
    w = GoogleImageExtractor()
    searchlist_filename = os.getcwd() + '/searchlist.txt'
    if len(sys.argv) != 1:
        w.set_num_image_to_dl(int(sys.argv[1]))
    else:
        w.set_num_image_to_dl(800)
    w.get_searchlist_fr_file(searchlist_filename)
    w.multi_search_download()
