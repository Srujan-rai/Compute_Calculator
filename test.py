import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def task_on_screen(display, task_id):
    # Set the DISPLAY environment variable for this process
    os.environ["DISPLAY"] = display
    print(f"Task {task_id} running on {display}")

    # Start Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    # Open a website
    driver.get("https://www.google.com")
    print(f"Task {task_id}: Google loaded on {display}")

    # Perform PyAutoGUI actions (key presses and mouse movements)
    pyautogui.typewrite(f"Hello from Task {task_id} on {display}")
    pyautogui.press("enter")

    # Wait to simulate longer processing
    time.sleep(5)

    # Close the browser
    driver.quit()
    print(f"Task {task_id} completed on {display}")
