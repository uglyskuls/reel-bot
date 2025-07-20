import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Get inputs ---
if len(sys.argv) < 3:
    raise Exception("❌ You must provide recipient username and number of reels as arguments.")
recipient_username = sys.argv[1]
total_iterations = int(sys.argv[2])
sessionid = os.environ.get("IG_SESSIONID")

if not sessionid:
    raise Exception("❌ Missing IG_SESSIONID in environment variables.")

# --- Set up headless Chrome ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,1024")
chrome_options.binary_location = "/usr/bin/google-chrome"

driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)
wait = WebDriverWait(driver, 10)

# --- Inject session and go to Reels ---
driver.get("https://www.instagram.com/")
driver.add_cookie({
    "name": "sessionid",
    "value": sessionid,
    "domain": ".instagram.com",
    "path": "/"
})
driver.get("https://www.instagram.com/reels/")
time.sleep(3)

def share_current_reel():
    try:
        print("🟡 Looking for Share button...")
        share_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//div[@role="button"]/*[name()="svg" and @aria-label="Share"]/..')
        ))
        driver.execute_script("arguments[0].click();", share_button)
        time.sleep(1)

        search_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
        search_input.clear()
        search_input.send_keys(recipient_username)
        time.sleep(1)

        user_click = wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[text()='{recipient_username}']")))
        user_click.click()
        time.sleep(0.5)

        send_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Send']")))
        send_button.click()
        print(f"✅ Sent reel to {recipient_username}")
        time.sleep(0.5)

        # Close dialog
        try:
            close = driver.find_element(By.XPATH, "//div[@aria-label='Close']")
            driver.execute_script("arguments[0].click();", close)
        except:
            pass

    except Exception as e:
        print(f"❌ Failed to send reel: {e}")
        try:
            close = driver.find_element(By.XPATH, "//div[@aria-label='Close']")
            driver.execute_script("arguments[0].click();", close)
        except:
            pass

# --- Main Loop ---
for i in range(total_iterations):
    print(f"\n🔁 Reload {i+1}/{total_iterations}")
    if i > 0:
        driver.get("https://www.instagram.com/reels/")
        time.sleep(2.5)
    share_current_reel()

driver.quit()
print("🎉 Done sending reels!")
