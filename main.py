import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from notion_client import Client

# Setup logging
logging.basicConfig(filename='notion_automation.log', level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Read Notion API key and page ID from environment variables
notion_api_key = os.environ.get('NOTION_API_KEY_My_Selenium_Notion_Integration')
notion_page_id = os.environ.get('NOTION_PAGE_ID_My_Selenium_Notion_Integration')

# Hardcoded path for testing
chromedriver_path = "D:\\D-H4wk Downloads and Installations\\Software Installations\\Chrome Web Driver\\Webdriver 125\\chromedriver-win64\\chromedriver.exe"

# Debug prints to check if environment variables are being retrieved correctly
logger.info(f"Notion API Key: {notion_api_key}")
logger.info(f"Notion Page ID: {notion_page_id}")
logger.info(f"ChromeDriver Path: {chromedriver_path}")

if not notion_api_key or not notion_page_id or not chromedriver_path:
    logger.error("Environment variables NOTION_API_KEY, NOTION_PAGE_ID, and CHROMEDRIVER_PATH must be set")
    raise ValueError("Environment variables NOTION_API_KEY, NOTION_PAGE_ID, and CHROMEDRIVER_PATH must be set")

# Initialize Notion client
notion = Client(auth=notion_api_key)


def backup_notion_data():
    # Backup current Notion page content
    try:
        page_content = notion.blocks.children.list(block_id=notion_page_id)
        with open('backup_page_content.json', 'w') as f:
            json.dump(page_content, f, indent=4)
        logger.info("Notion page content backed up successfully to backup_page_content.json.")
    except Exception as e:
        logger.error(f"Failed to backup Notion page content: {e}")


def test_integration_access():
    try:
        # Fetch the page
        page = notion.pages.retrieve(page_id=notion_page_id)
        logger.info(f"Integration access confirmed. \nPage data: {page}")

        # Check if the page has a title
        if 'properties' in page and 'title' in page['properties']:
            title_property = page['properties']['title']
            if title_property['type'] == 'title' and title_property['title']:
                logger.info(f"Page title: {title_property['title'][0]['text']['content']}")
            else:
                logger.warning("Page has no title or title format is unexpected")
        else:
            logger.warning("Page properties do not include a title")
    except Exception as e:
        logger.error(f"Failed to access page: {e}")


test_integration_access()

# Selenium setup
options = Options()
options.add_experimental_option("detach", True)
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Use the hardcoded path to the manually downloaded ChromeDriver
try:
    logger.info(f"Attempting to initialize ChromeDriver with path: {chromedriver_path}")
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)
    logger.info("ChromeDriver initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize ChromeDriver: {e}")
    raise


def scrape_first_favorite():
    driver.get(
        "https://www.notion.so/sidex/1x-xxxx-FAVES-Home-Favorites-saved-1st-100-Cats-2nd-240425-0a27fe7350eb497eb190ed1efeffb74f?pvs=4")
    logger.info("Navigated to Notion page for scraping favorites.")

    # Wait for the favorites to load
    driver.implicitly_wait(10)

    # Scroll to the first favorite
    first_favorite_xpath = "(//div[contains(@class, 'sidebar')]//div[contains(@class, 'favorite')])[1]"
    try:
        first_favorite_element = driver.find_element(By.XPATH, first_favorite_xpath)
        first_favorite_element.click()
        time.sleep(1.5)
        link_element = driver.find_element(By.XPATH, "//button[contains(@class, 'more-button')]")
        link_element.click()
        link = driver.find_element(By.XPATH, "//button[text()='Copy Link']").get_attribute('href')
        logger.info(f"Scraped first favorite link: {link}")
        return [link]
    except Exception as e:
        logger.error(f"Failed to scrape the first favorite: {e}")
        return []


def update_notion(favorites):
    # Fetch the existing page content
    try:
        # Update the Notion page
        children = []
        for favorite in favorites:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": favorite
                            }
                        }
                    ]
                }
            })

        notion.blocks.children.append(block_id=notion_page_id, children=children)
        logger.info("Notion page updated successfully.")

        # Update the Notion database
        database_id = 'YOUR_DATABASE_ID'  # Replace with your actual database ID
        for favorite in favorites:
            notion.pages.create(parent={"database_id": database_id}, properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": favorite
                            }
                        }
                    ]
                }
            })
        logger.info("Notion database updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update Notion page or database: {e}")


# Main function
def main():
    backup_notion_data()
    favorites = scrape_first_favorite()
    update_notion(favorites)
    driver.quit()


if __name__ == "__main__":
    main()
