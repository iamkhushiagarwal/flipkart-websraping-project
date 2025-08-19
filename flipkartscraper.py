from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from selenium.webdriver.common.action_chains import ActionChains

class Flipkart:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait=WebDriverWait(self.driver, 15)
        self.phone_data=[]

    def open_page(self):
        self.driver.get("https://www.flipkart.com/") 
        self.driver.maximize_window()
        mobile_tab=self.wait.until(EC.presence_of_element_located(( By.XPATH, '//a[contains(@href, "/mobile-phones-store") and @aria-label="Mobiles & Tablets"]')))
        mobile_tab.click()
        print("opened")

    def close_popup(self):
        try:
            close_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".close.btn.btn-link"))
            )
            close_btn.click()
            print("Popup closed")
        except:
            pass 

    def goto_mobilesection(self):
        self.driver.get("https://www.flipkart.com/search?q=mobiles")
        print("Navigated to search result page")
        #waiting for search menu to appear
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "_6i1qKy")))
        time.sleep(4)

    def brand_blocks(self):
        brand_section = self.driver.find_element(By.XPATH, '//div[contains(text(), "Brand")]/ancestor::section')
        return brand_section.find_elements(By.CSS_SELECTOR, 'div.ewzVkT._3DvUAf')
    
    def phone_links(self):
        phones = self.driver.find_elements(By.XPATH, '//a[contains(@class, "CGtC98")]')
        return list(set([phone.get_attribute("href") for phone in phones if phone.get_attribute("href")]))

    def extract_phone_data(self, brand_name, phone_links, brand_page_url):
        for link in phone_links[:5]:
            
            self.driver.get(link)
            time.sleep(2)
            try:
                name = self.driver.find_element(By.TAG_NAME, "h1").text
            except:
                name = "N/A"
            try:
                price = self.driver.find_element(By.CLASS_NAME, "Nx9bqj").text
            except:
                price = "N/A"
            try:
                rating = self.driver.find_element(By.CLASS_NAME, "XQDdHH").text
            except:
                rating = "N/A"
            try:
                review_count = self.driver.find_element(By.CLASS_NAME, "Wphh3N").text
            except:
                review_count = "N/A"

            print(f"Name: {name} | Price: {price} | Rating: {rating} | Reviews: {review_count}")
            self.phone_data.append({
                "Brand": brand_name,
                "Name": name,
                "Price": price,
                "Rating": rating,
                "Reviews": review_count
            })

            self.driver.get(brand_page_url)
            time.sleep(2)

    def save_to_csv(self):
         with open("flipkart.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Brand", "Name", "Price", "Rating", "Reviews"])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(self.phone_data)
            self.phone_data = []   

    def clear_brand_filter(self):
        try:
            clear_all = self.driver.find_element(By.XPATH, '//span[text()="Clear all"]')
            self.driver.execute_script("arguments[0].click();", clear_all)
            time.sleep(4)
        except:
            print("No 'Clear all' button found.")         
    def scrape(self):
        try:
            self.open_page()
            self.close_popup()
            self.goto_mobilesection()

            brand_blocks=self.brand_blocks()
            print(brand_blocks,"==================================")
            print(len(brand_blocks))

            for i in range(len(brand_blocks)):
                brand_blocks = self.brand_blocks()
                brand=brand_blocks[i]
                brand_name=brand.get_attribute("title")

                if not brand_name:
                    continue
                print(brand_name)

                label=brand.find_element(By.TAG_NAME, "label")
                self.driver.execute_script("arguments[0].click();", label)
                time.sleep(5)
                phone_links = self.phone_links()
                brand_page_url = self.driver.current_url
                self.extract_phone_data(brand_name, phone_links, brand_page_url)
                self.save_to_csv()
                self.clear_brand_filter()
        except Exception as e:
            print("Exception occurred:", e)
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = Flipkart()
    scraper.scrape()


    