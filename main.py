import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from selenium.webdriver.support import expected_conditions as EC


# File paths
input_file = "sheet.csv"  # Input CSV file
output_file = "output_results.csv"  # Output CSV file

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


# OS Mapping
os_mapping = {
    r"win(dows)?": "Paid: Windows Server",
    r"rhel": "Paid: Red Hat Enterprise Linux",
    r"ubuntu": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"debian": "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL",
    r"sql": "Paid: SQL Server Standard",
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

def get_machine_family_index(machine_family):
    """Get the index of the machine family based on its name."""
    machine_family_mapping = {
        "general purpose": 0,
        "compute optimized": 1,
        "memory optimized": 2,
        "accelerator optimized": 3,
        "storage optimized": 4,
    }
    # Default to "general purpose" if the machine family is empty or invalid
    return machine_family_mapping.get(machine_family.lower(), 0)

def process_row(driver, actions, os_name, no_of_instances,machine_family):
    """Processes a single row to calculate cost and retrieve URL."""
    os_index = get_os_index(os_name)
    machine_family_index = get_machine_family_index(machine_family) 

    def home_page():
        """Navigates to the pricing section."""
        driver.implicitly_wait(5)
        add_to_estimate_button = driver.find_element(By.XPATH, "//span[text()='Add to estimate']")
        add_to_estimate_button.click()
        time.sleep(5)
        div_element = driver.find_element(By.XPATH, "//div[@class='d5NbRd-EScbFb-JIbuQc PtwYlf' and @data-service-form='8']")
        actions.move_to_element(div_element).click().perform()
        time.sleep(3)

    def select_operating_system():
        """Selects the operating system based on the index."""
        if os_index is not None:
            for _ in range(6):  # Navigate to the OS dropdown
                actions.send_keys(Keys.TAB).perform()
                time.sleep(0.2)
            actions.send_keys(Keys.ENTER).perform()
            for _ in range(os_index+1):  # Navigate to the desired OS option
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.2)
            actions.send_keys(Keys.ENTER).perform()
        else:
            print("Invalid OS name. Skipping OS selection.")

    def select_instance():
        """Handles the instance selection."""
        print(no_of_instances)
        for _ in range(6):  # Navigate to instance dropdown
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()

        # Increment instance count
        wait = WebDriverWait(driver, 10)
        increment_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Increment']")))
        for _ in range(no_of_instances-1):  # Increment for (n-1) instances
            increment_button.click()
            time.sleep(0.2)

    def select_machine_family():
        """Selects the machine family."""
        for _ in range(6):  # Navigate to the machine family dropdown
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        for _ in range(machine_family_index):  # Select the machine family (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()

    def select_series():
        """Selects the series."""
        actions.send_keys(Keys.TAB).perform()  # Navigate to the series dropdown
        for _ in range(1):  # Select the series (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(1)

    def machine_type():
        """Selects the machine type."""
        actions.send_keys(Keys.TAB).perform()  # Navigate to the machine type dropdown
        actions.send_keys(Keys.TAB).perform()
        for _ in range(1):  # Select the machine type (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()

    def vcpu_and_memory():
        """Sets the vCPU and memory values."""
        for _ in range(3):  # Navigate to vCPU input
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(8).perform()  # Enter the vCPU value

        for _ in range(3):  # Navigate to memory input
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(8).perform()  # Enter the memory value

    # Navigate and set options
    time.sleep(1)
    try:
        home_page()
        select_instance()
        select_operating_system()
        select_machine_family()
        select_series()
        machine_type()
        #vcpu_and_memory()

        time.sleep(15)
        #cost_element = driver.find_element(By.CSS_SELECTOR, "span.MyvX5d.D0aEmf")
        #cost = cost_element.text
        # Using aria-label
        cost=1234
        wait = WebDriverWait(driver, 10)  # Timeout of 10 seconds

        download_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(@aria-label, 'Download estimate as .csv')]")))
        download_button.click()

        current_url = driver.current_url
        return cost, current_url
    except Exception as e:
        print(f"Error processing: {e}")
        return "Error", "Error"
    

def main():
    sheet = pd.read_csv(input_file)
    results = []

    
    driver.get("https://cloud.google.com/products/calculator")
    actions = ActionChains(driver)

    for index, row in sheet.iterrows():
        os_name = row["OS with version"]
        if pd.isna(os_name) or os_name.strip() == "":
            os_name = os_options[0]
        no_of_instances = int(row["No. of Instances"])
        machine_family = row["Machine Family"] if pd.notna(row["Machine Family"]) else "general purpose"
        print(f"Processing row {index + 1} with OS: {os_name}, Instances: {no_of_instances},machine family: {machine_family}")

        try:
            cost, url = process_row(driver, actions, os_name, no_of_instances, machine_family)
            results.append({"OS with version": os_name, "No. of Instances": no_of_instances, "Machine Family": machine_family, "Estimated Cost": cost, "URL": url})
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")
            results.append({"OS with version": os_name, "No. of Instances": no_of_instances, "Machine Family": machine_family, "Estimated Cost": "Error", "URL": "Error"})
        finally:
            time.sleep(5)

    driver.quit()

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()