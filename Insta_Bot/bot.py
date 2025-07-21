import os
import sys
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Get secrets and inputs ---
sessionid = os.environ['IG_SESSIONID']
recipient_username = sys.argv[1]    # passed as arg
total_iterations = int(sys.argv[2]) # passed as arg

chromedriver_autoinstaller.install()
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1280,1024")
chrome_options.binary_location = "/usr/bin/google-chrome"
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

driver.get("https://www.instagram.com/")
driver.add_cookie({
    "name": "sessionid",
    "value": sessionid,
    "domain": ".instagram.com",
    "path": "/"
})
driver.refresh()
wait.until(EC.title_contains("Instagram"))  # wait page title for safety

if "Login" in driver.title or "Log in" in driver.page_source:
    print("❌ Login failed! Check your sessionid.")
    driver.quit()
    raise Exception("Not logged in to Instagram.")

driver.get("https://www.instagram.com/reels/")
wait.until(EC.presence_of_element_located((By.XPATH, '//section/main')))  # wait for reels container

def share_current_reel():
    try:
        print("🟡 Looking for Share button (ABSOLUTE XPATH) ...")
        share_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div[3]')))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", share_btn)
        share_btn.click()
        print("Clicked the Share button.")

        freq_msg_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            f'//div[@role="button"]//span[text()="{recipient_username}"]/ancestor::div[@role="button"]'
        )))
        freq_msg_btn.click()
        print(f"Clicked frequently messaged recipient: {recipient_username}")

        send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Send']")))
        send_btn.click()
        print(f"✅ Sent reel to {recipient_username}")

        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close']")))
            close_btn.click()
        except Exception:
            pass

    except Exception as e:
        print(f"❌ Error during sharing: {e}")

for i in range(total_iterations):
    print(f"\n🔁 Cycle {i + 1} of {total_iterations}")
    if i > 0:
        driver.get("https://www.instagram.com/reels/")
        wait.until(EC.presence_of_element_located((By.XPATH, '//section/main')))
    share_current_reel()

driver.quit()
print("🎉 Done sending reels!")
