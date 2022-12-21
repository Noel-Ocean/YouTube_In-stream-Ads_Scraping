import os 
import json, time, schedule, datetime
import pandas as pd
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

def youtube_ads_scraper_no_login(local_chrome_driver_path, target_video_link, target_video_name, html_dict, number_of_times):

    chrome_driver=webdriver.Chrome(local_chrome_driver_path)
    chrome_driver.get(target_video_link) #; chrome_driver.minimize_window()
    action = ActionChains(chrome_driver)

    print(f"Start scraping ads for {target_video_name}...")
    ad_list=[]
    
    for i in range(number_of_times):

        try: 
            video_pause_find=WebDriverWait(chrome_driver,15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, html_dict["video_pause"])))
            action.move_to_element(video_pause_find).click().perform()

            time.sleep(3)

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
                ad_link_1=f"https://www.youtube.com/watch?v={video_id}".strip()
                ad_link_2=None
                time.sleep(2)

            if ad_count_text=="Ad 1 of 2 ·":
                action.move_to_element(video_pause_find).click().perform()
                action.move_to_element(video_pause_find).context_click().perform()
                stats_find=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["video_stats"])
                stats_find.click()
                video_id_find_1=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["ad_id"])
                video_id_1=video_id_find_1.text.split("/")[0]
                ad_link_1=f"https://www.youtube.com/watch?v={video_id_1}".strip()

                action.move_to_element(video_pause_find).click().perform()
                time.sleep(ad_duration_text+3)

                video_id_find_2=chrome_driver.find_element(By.CSS_SELECTOR, html_dict["ad_id"])
                video_id_2=video_id_find_2.text.split("/")[0]
                ad_link_2=f"https://www.youtube.com/watch?v={video_id_2}".strip()

        except:
            action.move_to_element(video_pause_find).click().perform()
            time.sleep(5)
            ad_link_1, ad_link_2=None, None
        
        search_time=datetime.datetime.now()
        printing_to_check=f"n={i}, {target_video_name}: {search_time.strftime('%H:%M:%S')}, {[ad_link_1, ad_link_2]}"
        print(printing_to_check)

        chrome_driver.refresh()
        ad_list.append([ad_link_1, ad_link_2])
    
    chrome_driver.quit()

    ad_list_unpacked=[item for sublist in ad_list for item in sublist]

    RESULT_DICT={
        "video_name": target_video_name,
        "video_link": target_video_link,
        "watching_date":search_time.strftime("%Y/%B/%d"),
        "watching_hour":search_time.strftime("%H"),
        "ad_embedded": ad_list_unpacked}
            
    RESULT_df=pd.DataFrame(RESULT_DICT)

    return RESULT_df

#################################################################################################################### 
# variables and arguments
#################################################################################################################### 
search_terms_excel="/Users/noel/Documents/GitHub/youtube_ads/DataCollection_SearchTerms.xlsx"
search_terms=pd.read_excel(search_terms_excel)[:2]
video_list=list(search_terms["most_viewed_202209"])
link_list=list(search_terms["link"])

html_dict_defined={
    "video_pause":'#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > button',
    "ad_count": 'ytp-ad-simple-ad-badge',
    "ad_duration": 'ytp-ad-duration-remaining',
    "video_stats": 'body > div.ytp-popup.ytp-contextmenu > div > div > div:nth-child(7) > div.ytp-menuitem-label',
    "ad_id": '#movie_player > div.html5-video-info-panel > div > div:nth-child(1) > span', 
}; region="hk"

#################################################################################################################### 
# RUN 
#################################################################################################################### 
today=datetime.datetime.today()
start_time=datetime.datetime.now()

df=[]
for name,link in zip(video_list, link_list):
    scraper_data=youtube_ads_scraper_no_login(
        local_chrome_driver_path="/Users/noel/Documents/GitHub/youtube_ads/chromedriver_mac",
        target_video_name=name, target_video_link=link, 
        html_dict=html_dict_defined,
        number_of_times=2
    ); df.append(scraper_data)
    time.sleep(5)

end_time=datetime.datetime.now()
print(f"Done! Time spent: {end_time-start_time}")

#################################################################################################################### 
# Reshape to save 
####################################################################################################################
output=pd.concat(df)
output_save_path="/Users/noel/Documents/GitHub/youtube_ads/data"; os.chdir(output_save_path)
output_filename=f"{region}_{today.date()}_{today.hour}{today.minute}.csv"
print(output_filename)
output.to_csv(output_filename)
