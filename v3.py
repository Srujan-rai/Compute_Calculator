from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
import time
import os
import pandas as pd
import re
import csv
import glob
import json


# File paths
input_file = "filtered.csv"  # Input CSV file
output_file = "output_results.csv"  # Output CSV file
index_file = "index.json"


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

# OS Options
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
    
    return indices.get(variable_name, None)
   
    
def home_page(driver,actions):
        """Navigates to the pricing section."""
        driver.implicitly_wait(5)
        add_to_estimate_button = driver.find_element(By.XPATH, "//span[text()='Add to estimate']")
        add_to_estimate_button.click()
        time.sleep(5)
        div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='8']")
        actions.move_to_element(div_element).click().perform()
        time.sleep(3)

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
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("Hours handled")


def handle_os(driver,actions,os_index):
    actions.send_keys(Keys.ENTER).perform()
    #time.sleep(5)
    for _ in range(os_index):
        actions.send_keys(Keys.ARROW_DOWN).perform()
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(6):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("OS handled")
    
def handle_machine_family(driver,actions,machine_family_index):
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.2)
    for _ in range(machine_family_index-1):
        actions.send_keys(Keys.ARROW_DOWN).perform()  #SELECTION
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.2)
    print("Machine Family handled")


def handle_series(driver,actions,series_index):
    actions.send_keys(Keys.ENTER).perform()
    
    for _ in range(series_index):
        actions.send_keys(Keys.ARROW_DOWN).perform()   #SELECTION
        time.sleep(0.2)
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.2)
    actions.send_keys(Keys.TAB).perform()
    time.sleep(0.2)
    print("Series handled")

def handle_machine_type(driver,actions,machine_type,machine_type_index):
        
    actions.send_keys(Keys.ENTER).perform()
    time.sleep(1)
    if machine_type=="custom":
        actions.send_keys(Keys.ARROW_UP).perform()
    else:
        for _ in range(machine_type_index-1):
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(1)
        actions.send_keys(Keys.ENTER).perform()
    time.sleep(0.2)
    print("Machine Type handled")
    
    

 
def handle_vcpu_and_memory(driver,actions,vCPU,ram):
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    time.sleep(2)
    actions.send_keys(vCPU).perform()
    time.sleep(2)
    actions.send_keys(Keys.ENTER).perform()
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    time.sleep(2)
    actions.send_keys(ram).perform()
    time.sleep(2)
    actions.send_keys(Keys.ENTER).perform()
    
    
def handle_extension(driver,actions):
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        
    print("Extension handled")

def no_handle_extension(driver,actions):
    
    actions.send_keys(Keys.TAB).perform()
        
    print("no Extension handled")

    
def boot_disk_type(driver,actions):
    actions.send_keys(Keys.TAB).perform()
    for _ in range(3):
        actions.send_keys(Keys.TAB).perform()
        time.sleep(0.2)
    print("Boot Disk Type handled")

def boot_disk_capacitys(driver,actions,boot_disk_capacity):
    actions.send_keys(Keys.ENTER).perform()
    actions.send_keys(Keys.BACKSPACE).perform()
    actions.send_keys(boot_disk_capacity).perform()
   


def get_price_with_js(driver):
    """
    Extracts the price value using JavaScript execution via Selenium.
    
    Args:
        driver: Selenium WebDriver instance.
    
    Returns:
        str: Extracted price value or a fallback message if not found.
    """
    try:
        # JavaScript to get the inner text of the target element
        js_script = """
        const element = document.querySelector('span.MyvX5d.D0aEmf');
        return element ? element.textContent.trim() : null;
        """
        price_text = driver.execute_script(js_script)
        
        # Validate the extracted text (basic validation for monetary value)
        if price_text and price_text.startswith("$"):
            return price_text
        elif price_text:
            return "Invalid price format"
        else:
            return "Price element not found"
    
    except JavascriptException as e:
        return f"An unexpected JavaScript error occurred: {str(e)}"




 

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
    handle_os(driver,actions,os_index)
    handle_machine_family(driver,actions,machine_family_index)
    handle_series(driver,actions,series_index)
    handle_machine_type(driver,actions,machine_type,machine_type_index)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            handle_vcpu_and_memory(driver, actions, vCPU, ram)
            if machine_type=="custom":
                handle_extension(driver,actions)
            else:
                no_handle_extension(driver,actions)
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            handle_vcpu_and_memory(driver, actions, vCPU, ram)
            no_handle_extension(driver,actions)
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    boot_disk_type(driver,actions)
    
    boot_disk_capacitys(driver,actions,boot_disk_capacity)    
    
    
    current_url = driver.current_url
    
    price=get_price_with_js(driver)
    
    print(price,current_url)
    
    driver.quit()
    
    
    
    
    
    
def get_sud_pricing( os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print("sud pricing")
    os_index = get_os_index(os_name)
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
    handle_os(driver,actions,os_index)
    handle_machine_family(driver,actions,machine_family)
    handle_series(driver,actions,series)
    handle_machine_type(driver,actions,machine_type)
    
    if (machine_family.lower() == "general purpose" and series in ["N1", "N2", "N4", "E2", "N2D"] and not (series == "N1" and machine_type in ["f1-micro", "g1-small"])):
            print(f"Calling handle_vcpu_and_memory Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
            handle_vcpu_and_memory(driver, actions, vCPU, ram)
            if machine_type=="custom":
                handle_extension(driver,actions)
        
    elif machine_family.lower() == "accelerator optimized" and series == "G2":
            print(f"Calling handle_vcpu_and_memory  Machine Family: {machine_family}, Series: {series}")
            handle_vcpu_and_memory(driver, actions, vCPU, ram)
            
    else:
        print(f"Skipping handle_vcpu_and_memory: Machine Family: {machine_family}, Series: {series}, Type: {machine_type}")
    
    
    
    current_url = driver.current_url

    driver.quit()
    
    
def get_one_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print("1 year pricing")
    os_index = get_os_index(os_name)
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
    handle_os(driver,actions,os_index)
    handle_machine_family(driver,actions,machine_family)
    handle_series(driver,actions,series)
    handle_machine_type(driver,actions,machine_type)
    
    
    current_url = driver.current_url
    driver.quit()


def  get_three_year_pricing(os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region):
    print("3 year pricing")
    os_index = get_os_index(os_name)
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
    handle_os(driver,actions,os_index)
    handle_machine_family(driver,actions,machine_family)
    handle_series(driver,actions,series)
    handle_machine_type(driver,actions,machine_type)
    
    
    
    current_url = driver.current_url
    driver.quit()



























#=============================================================================================#


def main():
    sheet = pd.read_csv(input_file)
    results = []

    for index, row in sheet.iterrows():
        os_name = row["OS with version"]
        if pd.isna(os_name) or os_name.strip() == "":
            os_name = os_options[0]
        if os_name.lower()=="free":
            os_name="Free: Debian, CentOS, CoreOS, Ubuntu or BY"

        no_of_instances = int(row["No. of Instances"])
        machine_family = row["Machine Family"].lower() if pd.notna(row["Machine Family"]) else "general purpose"
        series = row["Series"].upper() if pd.notna(row["Series"]) else "E2"
        machine_type = row["Machine Type"].lower() if pd.notna(row["Machine Type"]) else "custom"
        vCPU = row["vCPUs"] if pd.notna(row["vCPUs"]) else 2
        ram = row["RAM"] if pd.notna(row["RAM"]) else 2
        boot_disk_capacity = row["BootDisk Capacity"] if pd.notna(row["BootDisk Capacity"]) else 10
        region = row["Datacenter Location"] if pd.notna(row["Datacenter Location"]) else "Mumbai"
        hours_per_day = row["Hrs/Min"] if pd.notna(row["Hrs/Min"]) else 730
        
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

        for iteration in range(4):  # Four iterations for different types of pricing
            try:
                if iteration == 0:
                    print(f"Iteration {iteration + 1}: Getting on-demand price and link")
                    row_result["On-Demand URL"], row_result["On-Demand Price"] = get_on_demand_pricing(
                        os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                    )

                elif iteration == 1:
                    print(f"Iteration {iteration + 1}: Getting sustained use discount (SUD) price and link")
                    row_result["SUD URL"], row_result["SUD Price"] = get_sud_pricing(
                        os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                    )

                elif iteration == 2:
                    print(f"Iteration {iteration + 1}: Getting 1-year commitment price and link")
                    row_result["1-Year URL"], row_result["1-Year Price"] = get_one_year_pricing(
                        os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
                    )

                elif iteration == 3:
                    print(f"Iteration {iteration + 1}: Getting 3-year commitment price and link")
                    row_result["3-Year URL"], row_result["3-Year Price"] = get_three_year_pricing(
                        os_name, no_of_instances,hours_per_day, machine_family, series, machine_type, vCPU, ram, boot_disk_capacity, region
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


    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")
    
    
if __name__ == "__main__":
    main()