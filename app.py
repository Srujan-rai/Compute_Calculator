from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
import time
import os
import pandas as pd
import re
import csv
import glob
import json
import smtplib
from email.message import EmailMessage
import requests
from flask import Flask, request


app=Flask(__name__)




index_file = "index.json"



input_file = "sheet.csv"  # Replace with your input file path


output_file_filtered = "output.csv" 
input_filtered_file="output.csv"


output_file = "output_results.csv"

sender_email = "srujan.int@niveussolutions.com"
sender_password = "rmlh ikej rtmz ejme"
subject = "Compute Calculation Results"
body = "Please find the attached file for the results of the computation."
file_path = "output_results.xlsx"


with open('knowledge_base.json', 'r') as kb_file:
    knowledge_base = json.load(kb_file)

os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql": "Paid: SQL Server Standard",
    r"free": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sles(\s*12)?": "Paid: SLES 12 for SAP",
    r"sles(\s*15)?": "Paid: SLES 15 for SAP",
    r"ubuntu\s*pro": "Paid: Ubuntu Pro",
    r"rhel\s*7": "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support",
    r"rhel\s*sap": "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services",
    r"sles": "Paid: SLES"
}


def extract_sheet_id(sheet_url):
    pattern = r"https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, sheet_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheet URL")

def download_sheet(sheet_url):
    try:
        sheet_id = extract_sheet_id(sheet_url)
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        response = requests.get(csv_url)

        if response.status_code == 200:
            with open("sheet.csv", "wb") as f:
                f.write(response.content)
            print("Google Sheet downloaded as sheet.csv")
        else:
            print("Failed to download sheet. HTTP Status Code:", response.status_code)
    except ValueError as e:
        print(e)
    except Exception as e:
        print("An error occurred:", e)




def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path):
    try:
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.set_content(body)

        
        with open(file_path, 'rb') as file:
            file_data = file.read()
            file_name = file_path.split('/')[-1]  # Get the file name from the path
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

       
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def map_os(value, os_mapping):
    for pattern, replacement in os_mapping.items():
        if re.search(pattern, value, re.IGNORECASE):
            return replacement
    return "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL"  

def map_value(value, knowledge_base):
    for key in knowledge_base:
        if re.search(rf"\b{re.escape(value)}\b", key, re.IGNORECASE):
            return key
    return value 

def process_csv(input_file, output_file):
    df = pd.read_csv(input_file)

    if 'OS with version' in df.columns:
        df['OS with version'] = df['OS with version'].apply(
            lambda x: map_os(str(x).strip(), os_mapping) if pd.notnull(x) else "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL"
        )

    if 'Machine Family' in df.columns:
        df['Machine Family'] = df['Machine Family'].fillna("general purpose")

    if 'Series' in df.columns:
        df['Series'] = df['Series'].fillna("E2")

    if 'Machine Type' in df.columns:
        df['Machine Type'] = df['Machine Type'].fillna("custom")

    columns_to_map = ["Machine Family", "Series", "Machine Type"]

    for column in columns_to_map:
        if column in df.columns:
            df[column] = df[column].apply(lambda x: map_value(str(x).strip(), knowledge_base) if pd.notnull(x) else x)

    
    df.to_csv(output_file, index=False)
    print("input file filtered")



def load_index(file_path):
    
    with open(file_path, 'r') as file:
        return json.load(file)


indices = load_index(index_file)


os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql": "Paid: SQL Server Standard",
    r"free" :"Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
}


os_options = {
    0: "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    1: "Paid: Ubuntu Pro",
    2: "Paid: Windows Server",
    3: "Paid: Red Hat Enterprise Linux",
    4: "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support",
    5: "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services",
    6: "Paid: SLES",
    7: "Paid: SLES 12 for SAP",
    8: "Paid: SLES 15 for SAP",
    9: "Paid: SQL Server Standard",
    10: "Paid: SQL Server Web",
    11: "Paid: SQL Server Enterprise",
}



def get_os_index(os_name):
    """Get the index of the OS based on its name."""
    for regex, mapped_name in os_mapping.items():
        if pd.notna(os_name) and re.search(regex, os_name, re.IGNORECASE):
            for index, name in os_options.items():
                if name == mapped_name:
                    return index
    return None

def get_index(variable_name, indices):
    
    return indices.get(variable_name, 0)
   
    
def home_page(driver,actions):
        """Navigates to the pricing section."""
        driver.implicitly_wait(5)
        add_to_estimate_button = driver.find_element(By.XPATH, "//span[text()='Add to estimate']")
        add_to_estimate_button.click()
        time.sleep(5)
        div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='8']")
        actions.move_to_element(div_element).click().perform()
        time.sleep(2)

def handle_instance(driver,actions,no_of_instance):
    for _ in range(6):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(int(no_of_instance)).perform()
    for _ in range(4):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("Instance handled")


def handle_hours_per_day(driver,actions,hours_per_day):
    actions.send_keys(hours_per_day).perform()
    time.sleep(1)
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("Hours handled")



def handle_os(driver,actions,os_index,os_name):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Operating System / Software')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite(os_name)
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("machine family selected")
    
    
    
def handle_machine_family(driver,actions,machine_family_index,machine_family):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Machine Family')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite(machine_family)
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("machine family selected")


def handle_series(driver,actions,series_index,series):
    actions.send_keys(Keys.TAB).perform()
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite(series)
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    print("machine series selected")
    
    
def handle_machine_type(driver,actions,machine_type,machine_type_index):
    
    
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite(machine_type)
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("machine type selected")
    
def extended_mem_toggle_on(driver,actions):
    time.sleep(1)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Extended memory')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()
    print("extension toggle turned on")
    
    
       
 
def handle_vcpu_and_memory(driver,actions,vCPU,ram):
    print(vCPU)
    print(ram)
    time.sleep(1)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Number of vCPUs')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
        
        
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(1)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(1)
    actions.send_keys(vCPU).perform()
    time.sleep(1)
    
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Amount of memory')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.ENTER).perform()
    
    time.sleep(1)
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
        
   
    time.sleep(1)

    actions.send_keys(ram).perform()
    
    
    
    
    print("vpcu and ram selected")
    
    
  
def boot_disk_type(driver,actions):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Boot disk type')
    time.sleep(1)
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.TAB).perform()
    actions.send_keys(Keys.TAB).perform()   
    
    print("Boot Disk Type handled")

def boot_disk_capacitys(driver,actions,boot_disk_capacity):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Boot disk size (GiB)')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
   
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    actions.send_keys(Keys.BACKSPACE).perform()
    time.sleep(1)
    pyautogui.typewrite(str(boot_disk_capacity))
    time.sleep(1)
    actions.send_keys(Keys.TAB).perform()
    actions.send_keys(Keys.TAB).perform()
    print("boot disk capacity selected")
   


def select_region(driver, actions, region):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Region')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite(region)
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    actions.send_keys(Keys.ENTER).perform()
   
    
    print("Region selected")


def get_price_with_js(driver):
    
    try:
        js_script = """
        const element = document.querySelector('span.MyvX5d.D0aEmf');
        return element ? element.textContent.trim() : null;
        """
        price_text = driver.execute_script(js_script)
        
        if price_text and price_text.startswith("$"):
            return price_text
        elif price_text:
            return "Invalid price format"
        else:
            return "Price element not found"
    
    except JavascriptException as e:
        return f"An unexpected JavaScript error occurred: {str(e)}"


def move_to_region(driver,actions,moves):
    pass
    


def sud_toggle_on(driver,actions):
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Add sustained use discounts')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)
    
    actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
    time.sleep(1)
    actions.send_keys(Keys.ENTER).perform()
    print("Sud turned on")

def one_year_selection(driver,actions):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    actions.send_keys(Keys.ENTER).perform()




def three_year_selection(driver,actions):
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    
    pyautogui.typewrite('Committed use discount options')
    time.sleep(1)
    
    pyautogui.press('esc')
    time.sleep(1)   
    
    for _ in range(2):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.ARROW_RIGHT).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
  
    

#=============================================================================================#
def get_on_demand_pricing( os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print(os_name,no_of_instances,hours_per_day,machine_family,series,machine_type,vCPU,ram,boot_disk_capacity,region)
    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("ondemand pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(1)
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(1)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(1)
    handle_series(driver,actions,series_index,series)
    #time.sleep(1)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(1)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(1)
    boot_disk_type(driver,actions)
    #time.sleep(1)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(1)

    

    select_region(driver,actions,region)
    
        
        
    
    time.sleep(5)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    driver.quit()
    
    return current_url, price
    
    
    
    
    
    
def get_sud_pricing( os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print(os_name,no_of_instances,hours_per_day,machine_family,series,machine_type,vCPU,ram,boot_disk_capacity,region)
    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("sud pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances)
    #time.sleep(1)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(1)
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(1)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(1)
    handle_series(driver,actions,series_index,series)
    #time.sleep(1)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(1)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(1)
    boot_disk_type(driver,actions)
    #time.sleep(1)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(2)

    sud_toggle_on(driver,actions)
    
    #time.sleep(2)
    select_region(driver,actions,region)
    
        
        
    
    time.sleep(5)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    driver.quit()
    
    return current_url, price   
    
    
def get_one_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print(os_name,no_of_instances,hours_per_day,machine_family,series,machine_type,vCPU,ram,boot_disk_capacity,region)
    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("one year pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances)
    #time.sleep(1)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(1)
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(1)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(1)
    handle_series(driver,actions,series_index,series)
    #time.sleep(1)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(1)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(1)
    boot_disk_type(driver,actions)
    #time.sleep(1)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(1)

    

    select_region(driver,actions,region)
    
    #time.sleep(1)
    
    one_year_selection(driver,actions)  
        
    
    time.sleep(5)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    driver.quit()
    
    return current_url, price

def  get_three_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print(os_name,no_of_instances,hours_per_day,machine_family,series,machine_type,vCPU,ram,boot_disk_capacity,region)
    os_index = get_os_index(os_name)
    machine_family_index = get_index(machine_family, indices)
    series_index = get_index(series, indices)
    machine_type_index = get_index(machine_type, indices)
    
    print(f"os index : {os_index},machine family : {machine_family_index},series index :{series_index},machine type index : {machine_type_index}")
    print(vCPU,ram)
    print("ondemand pricing")
    download_directory = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_directory, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")
    driver.implicitly_wait(10)
    
    home_page(driver,actions)
    handle_instance(driver,actions,no_of_instances)
    #time.sleep(1)
    handle_hours_per_day(driver,actions,hours_per_day)
    #time.sleep(1)
    handle_os(driver,actions,os_index,os_name)
    #time.sleep(1)
    handle_machine_family(driver,actions,machine_family_index,machine_family)
    #time.sleep(1)
    handle_series(driver,actions,series_index,series)
    #time.sleep(1)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    #time.sleep(1)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            if machine_type=='custom':
                extended_mem_toggle_on(driver,actions)
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
            else:
                handle_vcpu_and_memory(driver, actions, vCPU, ram)
           
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    #time.sleep(1)
    boot_disk_type(driver,actions)
    #time.sleep(1)
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    #time.sleep(1)
    
    select_region(driver,actions,region)
    
    #time.sleep(1)
    
    three_year_selection(driver,actions)
    
    time.sleep(5)
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    driver.quit()
    
    return current_url, price


#=============================================================================================#


def main(sheet_url,recipient_email):
    download_sheet(sheet_url)

    process_csv(input_file, output_file_filtered)
    sheet = pd.read_csv(input_filtered_file)
    results = []

    for index, row in sheet.iterrows():
        os_name = row["OS with version"]
        no_of_instances = float(row["No. of Instances"])
        machine_family = row["Machine Family"].lower() if pd.notna(row["Machine Family"]) else "general purpose"
        series = row["Series"].upper() if pd.notna(row["Series"]) else "E2"
        machine_type = row["Machine Type"].lower() if pd.notna(row["Machine Type"]) else "custom"
        vCPU = row["vCPUs"] if pd.notna(row["vCPUs"]) else 0.25
        ram = row["RAM"] if pd.notna(row["RAM"]) else 1
        boot_disk_capacity = row["BootDisk Capacity"] if pd.notna(row["BootDisk Capacity"]) else 0
        region = row["Datacenter Location"] if pd.notna(row["Datacenter Location"]) else "Mumbai"
        hours_per_day = row["Hrs/Min"] if pd.notna(row["Hrs/Min"]) else 730
        print(hours_per_day)
        
        '''if hours_per_day <730:
            same_costing=True'''
        
        print(f"Processing row {index + 1} with OS: {os_name}, Instances: {no_of_instances}, machine family: {machine_family}, series: {series}, machine type: {machine_type}")

        row_result = {
            "Row Index": index + 1,
            "OS with version": os_name,
            "No. of Instances": no_of_instances,
            "Machine Family": machine_family,
            "On-Demand URL": None,
            "On-Demand Price": None,
            "SUD URL": None,
            "SUD Price": None,
            "1-Year URL": None,
            "1-Year Price": None,
            "3-Year URL": None,
            "3-Year Price": None
        }

        for iteration in range(4):  
            try:
                if machine_type == "e2-micro" :
                    if iteration == 0:  
                        print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                        row_result["On-Demand URL"], row_result["On-Demand Price"] = get_on_demand_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )

                        row_result["SUD URL"], row_result["SUD Price"] = row_result["On-Demand URL"], row_result["On-Demand Price"]
                        row_result["1-Year URL"], row_result["1-Year Price"] = row_result["On-Demand URL"], row_result["On-Demand Price"]
                        row_result["3-Year URL"], row_result["3-Year Price"] = row_result["On-Demand URL"], row_result["On-Demand Price"]
                        break 
                
                
                elif hours_per_day < 730:
                    if iteration==0:
                        print(f"Iteration {iteration + 1}: Getting on-demand price and link (e2-micro)")
                        row_result["On-Demand URL"], row_result["On-Demand Price"] = get_on_demand_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )

                    if iteration==1:
                        print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                        row_result["SUD URL"], row_result["SUD Price"] = get_sud_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )
                        
                        row_result["1-Year URL"], row_result["1-Year Price"] = row_result["SUD URL"], row_result["SUD Price"]
                        row_result["3-Year URL"], row_result["3-Year Price"] = row_result["SUD URL"], row_result["SUD Price"]
                        break
                    
                
                
                else:
                    if iteration == 0:
                        print(f"Iteration {iteration + 1}: Getting on-demand price and link")
                        row_result["On-Demand URL"], row_result["On-Demand Price"] = get_on_demand_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )
                    elif iteration == 1:
                        print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                        row_result["SUD URL"], row_result["SUD Price"] = get_sud_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )
                    elif iteration == 2:
                        print(f"Iteration {iteration + 1}: Getting 1-year commitment price and link")
                        row_result["1-Year URL"], row_result["1-Year Price"] = get_one_year_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )
                    elif iteration == 3:
                        print(f"Iteration {iteration + 1}: Getting 3-year commitment price and link")
                        row_result["3-Year URL"], row_result["3-Year Price"] = get_three_year_pricing(
                            os_name, no_of_instances, hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                        )
            except Exception as e:
                print(f"Error processing row {index + 1}, iteration {iteration + 1}: {e}")
                if iteration == 0:
                    row_result["On-Demand URL"] = "Error"
                    row_result["On-Demand Price"] = "Error"
                elif iteration == 1:
                    row_result["SUD URL"] = "Error"
                    row_result["SUD Price"] = "Error"
                elif iteration == 2:
                    row_result["1-Year URL"] = "Error"
                    row_result["1-Year Price"] = "Error"
                elif iteration == 3:
                    row_result["3-Year URL"] = "Error"
                    row_result["3-Year Price"] = "Error"
            finally:
                time.sleep(5)

        results.append(row_result)


    output_file = "output_results.xlsx"  # Excel file extension

    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")
    print("sending mail!!")
    send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, file_path)


@app.route('/calculate',methods=["POST"])
def run_automation():
    sheet = request.form.get('sheet')
    email = request.form.get('email')
    
    main(sheet,email)
    
    

        
    
if __name__ == "__main__":
    
    app.run(debug=True,use_reloader=False,host='0.0.0.0')
