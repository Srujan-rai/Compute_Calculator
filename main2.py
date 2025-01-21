from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import glob

# File paths
input_file = "input_data.csv"  # Input CSV file
output_file = "output_results.csv"  # Output CSV file

# Setup download directory
download_directory = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_directory, exist_ok=True)

# Chrome options
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Mappings
os_mapping = {
    "Free: Debian, CentOS, CoreOS, Ubuntu or BYOL (Bring Your Own License)": 0,
    "Paid: Ubuntu Pro": 1,
    "Paid: Windows Server 2012 R2, Windows Server 2016, Windows Server 2019, Windows Server (2004, 20H2)": 2,
    "Paid: Red Hat Enterprise Linux": 3,
    "Paid: Red Hat Enterprise Linux 7 with Extended Life Cycle Support Add-On": 4,
    "Paid: Red Hat Enterprise Linux for SAP with HA and Update Services": 5,
    "Paid: SLES": 6,
    "Paid: SLES 12 for SAP": 7,
    "Paid: SLES 15 for SAP": 8,
    "Paid: SQL Server Standard (2012, 2014, 2016, 2017, 2019)": 9,
    "Paid: SQL Server Web (2012, 2014, 2016, 2017, 2019)": 10,
    "Paid: SQL Server Enterprise (2012, 2014, 2016, 2017, 2019)": 11,
}

machine_family_mapping = {
    "General Purpose": 0,
    "Compute-optimized": 1,
    "Memory-optimized": 2,
    "Accelerator-optimized": 3,
    "Storage-optimized": 4,
}

series_mappings = {
    "General Purpose": {
        "N1": 0, "N2": 1, "N4": 2, "E2": 3, "N2D": 4, "T2A": 5, "T2D": 6, "C3": 7, "C3D": 8, "C4": 9, "C4A": 10,
    },
    "Compute-optimized": {"C2": 0, "C2D": 1, "H3": 2},
    "Memory-optimized": {"M1": 0, "M2": 1, "M3": 2},
    "Accelerator-optimized": {"A2": 0, "A3": 1, "G2": 2},
    "Storage-optimized": {"Z3": 0},
}

machine_type_mappings = {
    "General Purpose": {
        "t2a-standard-1": 0, "t2a-standard-2": 1, "t2a-standard-4": 2, "t2a-standard-8": 3, "t2a-standard-16": 4,
        "t2a-standard-32": 5, "t2a-standard-48": 6,
    },
    "Compute-optimized": {"c2-standard-4": 0, "c2-standard-8": 1, "c2-standard-16": 2, "c2-standard-30": 3, "c2-standard-60": 4},
    "Memory-optimized": {"m1-megamem-96": 0, "m1-ultramem-40": 1, "m1-ultramem-80": 2, "m1-ultramem-160": 3},
    "Accelerator-optimized": {"a3-highgpu-1g": 0, "a3-highgpu-2g": 1, "a3-highgpu-4g": 2, "a3-highgpu-8g": 3},
    "Storage-optimized": {"z3-highmem-88": 0, "z3-highmem-176": 1},
}

def map_values(row):
    """Map input values to their corresponding indices."""
    def map_values(row):
        """Map input values to their corresponding indices."""
    os_index = os_mapping.get(row["OS with version"], None)
    if os_index is None:
        print(f"OS mapping failed for: {row['OS with version']}")
    
    machine_family_index = machine_family_mapping.get(row["Machine Family"], None)
    if machine_family_index is None:
        print(f"Machine Family mapping failed for: {row['Machine Family']}")

    series_index = series_mappings.get(row["Machine Family"], {}).get(row["Series"], None)
    if series_index is None:
        print(f"Series mapping failed for: {row['Series']} in {row['Machine Family']}")

    machine_type_index = machine_type_mappings.get(row["Machine Family"], {}).get(row["Machine Type"], None)
    if machine_type_index is None:
        print(f"Machine Type mapping failed for: {row['Machine Type']} in {row['Machine Family']}")
    
    no_of_instances = int(row["No. of Instances"])
    return os_index, machine_family_index, series_index, machine_type_index, no_of_instances

def extract_total_price(file_path):
    """Extracts the 'Total Price' value from the downloaded CSV file."""
    try:
        with open(file_path, "r") as csvfile:
            for line in csvfile:
                if "Total Price:" in line:
                    parts = line.split(",")
                    for part in parts:
                        try:
                            return float(part.strip())
                        except ValueError:
                            continue
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
    return None

def process_row(driver, actions, os_index, machine_family_index, series_index, machine_type_index, no_of_instances):
    """Processes a single row to calculate cost and retrieve URL."""

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
            for _ in range(os_index + 1):  # Navigate to the desired OS option
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(0.2)
            actions.send_keys(Keys.ENTER).perform()
        else:
            print("Invalid OS name. Skipping OS selection.")

    def select_instance():
        """Handles the instance selection."""
        for _ in range(6):  # Navigate to instance dropdown
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()

        # Increment instance count
        wait = WebDriverWait(driver, 10)
        increment_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Increment']")))
        for _ in range(no_of_instances - 1):  # Increment for (n-1) instances
            increment_button.click()
            time.sleep(0.2)

    def select_machine_family():
        """Selects the machine family."""
        for _ in range(6):  # Navigate to the machine family dropdown
            actions.send_keys(Keys.TAB).perform()
            time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()
        for _ in range(machine_family_index):  # Select the machine family
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()

    def select_series():
        """Selects the series."""
        actions.send_keys(Keys.TAB).perform()  # Navigate to the series dropdown
        for _ in range(series_index):  # Select the series
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(1)

    def machine_type():
        """Selects the machine type."""
        actions.send_keys(Keys.TAB).perform()  # Navigate to the machine type dropdown
        for _ in range(machine_type_index):  # Select the machine type
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(2)
        actions.send_keys(Keys.ENTER).perform()

    # Navigate and set options
    time.sleep(1)
    try:
        home_page()
        select_instance()
        select_operating_system()
        select_machine_family()
        select_series()
        machine_type()

        time.sleep(15)

        # Downloading estimate
        wait = WebDriverWait(driver, 10)  # Timeout of 10 seconds
        download_button = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@aria-label, 'Download estimate as .csv')]"))
        )
        download_button.click()

        # Process downloaded file
        downloaded_files = glob.glob(f"{download_directory}/*.csv")
        if not downloaded_files:
            return "Error", "Error"
        latest_file = max(downloaded_files, key=os.path.getctime)
        total_price = extract_total_price(latest_file)
        print(f"Total Price: {total_price}")

        # Get the current URL
        current_url = driver.current_url
        return total_price, current_url

    except Exception as e:
        print(f"Error processing: {e}")
        return "Error", "Error"

def main():
    # Read input CSV
    try:
        data = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if data.empty:
        print("Input file is empty.")
        return

    row = data.iloc[0]  # Process the first row
    os_index, machine_family_index, series_index, machine_type_index, no_of_instances = map_values(row)

    if None in (os_index, machine_family_index, series_index, machine_type_index):
        print(f"Error mapping values: {row}")
        return

    actions = ActionChains(driver)
    driver.get("https://cloud.google.com/products/calculator")

    print("Processing single input row...")
    cost, url = process_row(driver, actions, os_index, machine_family_index, series_index, machine_type_index, no_of_instances)

    print(f"Cost: {cost}, URL: {url}")
    driver.quit()

if __name__ == "__main__":
    main()
