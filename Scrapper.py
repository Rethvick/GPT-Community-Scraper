from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# url = f"https://community.openai.com/tag/plugin-development"
# driver.get(url)
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
# time.sleep(30)
def scroll_to_bottom(driver):
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

def scrape_tag(tag_name):
    url = f"https://community.openai.com/tag/{tag_name}"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    title_xpath = "/html/body/section/div[1]/div[3]/div[2]/div[2]/div[2]/div/div/h1/a"
    content_xpath = "/html/body/section/div[1]/div[3]/div[2]/div[2]/div[3]"
    replies_log_filename = f"{tag_name}/{tag_name}_replies_log.txt"

    if not os.path.exists(tag_name):
        os.makedirs(tag_name)

    post_index = 1116
    while post_index < 17000:
        try:
            time.sleep(2)  # General wait to mitigate rapid request issues
            replies_xpath = f"/html/body/section/div[1]/div[3]/div[2]/div[4]/div[2]/div/div/div/table/tbody/tr[{post_index}]/td[3]/button/span"
            try:
                replies_element = WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, replies_xpath)))
                replies_count = replies_element.text
            except:
                replies_count = '0'

            post_xpath = f"/html/body/section/div[1]/div[3]/div[2]/div[4]/div[2]/div/div/div/table/tbody/tr[{post_index}]/td[1]/span"
            driver.find_element(By.XPATH, post_xpath).click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, title_xpath)))

            scroll_to_bottom(driver)

            title_element = driver.find_element(By.XPATH, title_xpath)
            content_element = driver.find_element(By.XPATH, content_xpath)
            title_text = title_element.text
            content_text = content_element.text

            filename = f"{tag_name}/{tag_name}${post_index}${replies_count}.txt"
            with open(filename, 'w') as file:
                file.write(f"Title: {title_text}\nContent: {content_text}\nReplies: {replies_count}\n\n")

            with open(replies_log_filename, 'a') as log_file:
                log_file.write(f"{tag_name}${post_index}${replies_count}\n")

            post_index += 1
            driver.back()
        except NoSuchElementException:
            # print(f"Post {post_index} not found, skipping to next.")
            # post_index += 1  # Skip the current post and move to the next
            driver.execute_script("window.scrollBy(0, 1600);")
        except Exception as e:
            print(f"Finished processing or encountered an error: {e}")
            break

tags = ["chatgpt-plugin"]

for tag in tags:
    print(f"Scraping tag: {tag}")
    scrape_tag(tag)

driver.quit()

print('Scraped data and replies counts have been saved with all content loaded.')
