import json, time, schedule, datetime
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def youtube_ads_scraper(local_chrome_driver_path, target_video, target_video_name, html_dict, number_of_fresh_times, region):

    print(f"Start scraping ads for {target_video_name}...")

    chrome_driver=webdriver.Chrome(local_chrome_driver_path)
    chrome_driver.get(target_video);  # chrome_driver.maximize_window()
    action = ActionChains(chrome_driver)

    time_list, ad_list, ad_number_list=[],[],[]
    for i in range(number_of_fresh_times):
        ad_search_time=datetime.datetime.now()
        video_pause_find=WebDriverWait(chrome_driver,30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, html_dict["video_pause"])))
        action.move_to_element(video_pause_find).click().perform()
        time.sleep(2)

        try: 
            ad_count_find=chrome_driver.find_element(By.CLASS_NAME, html_dict["ad_count"])
            ad_count_text=str(ad_count_find.text)
            ad_duration_find=chrome_driver.find_element(By.CLASS_NAME, html_dict["ad_duration"])
            ad_duration_text_min=str(ad_duration_find.text.split(":")[0])
            ad_duration_text_second=str(ad_duration_find.text.split(":")[1])
            ad_duration_text=int(ad_duration_text_min)*60 + int(ad_duration_text_second)

            if ad_count_text=="Ad ·":
                action.move_to_element(video_pause_find).click().perform()
                action.move_to_element(video_pause_find).context_click().perform()
                stats_find=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["video_stats"])
                action.move_to_element(stats_find).click().perform()

                video_id_find=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["ad_id"])
                video_id=video_id_find.text.split("/")[0]
                ad_link=[f"https://www.youtube.com/watch?v={video_id}"]
                ad_number=len(ad_link)

            if ad_count_text=="Ad 1 of 2 ·":
                action.move_to_element(video_pause_find).click().perform()
                action.move_to_element(video_pause_find).context_click().perform()
                stats_find=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["video_stats"])
                stats_find.click()

                video_id_find_1=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["ad_id"])
                video_id_1=video_id_find_1.text.split("/")[0]
                ad_link_1=f"https://www.youtube.com/watch?v={video_id_1}"

                action.move_to_element(video_pause_find).click().perform()
                time.sleep(ad_duration_text)
                time.sleep(5)

                video_id_find_2=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["ad_id"])
                video_id_2=video_id_find_2.text.split("/")[0]
                ad_link_2=f"https://www.youtube.com/watch?v={video_id_2}"

                ad_link=list(set([ad_link_1, ad_link_2]))
                ad_number=len(ad_link)

        except:
            ad_link="No ads found"
            ad_number=0
        
        printing_to_check=f"{target_video_name}: {ad_search_time}, {ad_link}"
        print(printing_to_check)
        chrome_driver.refresh()

        time_list.append(ad_search_time)
        ad_list.append(ad_link)
        ad_number_list.append(ad_number)

    video_title_list=[target_video_name for i in range(number_of_fresh_times)]
    video_link_list=[target_video for i in range(number_of_fresh_times)]

    RESULT=pd.DataFrame({
        "HKT_watching":time_list,
        "video_name":video_title_list,
        "video_link": video_link_list,
        "ad_embedded":ad_list,
        "#_ads_found": ad_number_list
    })

    chrome_driver.quit()

    return RESULT

html_dict_defined={
    "video_pause":'#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > button',
    "ad_count": 'ytp-ad-simple-ad-badge',
    "ad_duration": 'ytp-ad-duration-remaining',
    "video_stats": 'body > div.ytp-popup.ytp-contextmenu > div > div > div:nth-child(7) > div.ytp-menuitem-label',
    "ad_id": '#movie_player > div.html5-video-info-panel > div > div:nth-child(1) > span'
}

#################################################################################################################### 
# RUN 
#################################################################################################################### 
DATA=[]
for i in range(2):
    scraper_data=youtube_ads_scraper(
        local_chrome_driver_path=r"C:\Users\Noel\Desktop\Alcohol_marketing\Python\chromedriver.exe",
        target_video=top_video, target_video_name=top_video_name,
        html_dict=html_dict_defined,
        number_of_fresh_times=2,
        region="HK"
    ); DATA.append(scraper_data)
    time.sleep(5)

print("Done!")
OUTPUT=pd.concat(DATA).reset_index(drop=True)
OUTPUT