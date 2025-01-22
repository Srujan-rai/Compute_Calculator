from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import re
import csv
import glob



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
    return machine_family_mapping.get(machine_family.lower(), 0)


def extract_total_price(file_path):
    """Extracts the 'Total Price' value from the downloaded CSV file."""
    try:
        with open(file_path, "r") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if "Total Price:" in row:
                    return float(row[row.index("Total Price:") + 1])
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None
 


def process_row(driver, actions, os_name, no_of_instances,machine_family,series,machine_type,vCPU,ram,Boot_disk_capacity,region):
    """Processes a single row to calculate cost and retrieve URL."""
    os_index = get_os_index(os_name)
    
    disk_type=1
    size=200
    region_index=5
    vcpu_value=8
    memory_value=8

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
        print("now we are navigating to  machine family")
        for _ in range(6):  # Navigate to the machine family dropdown
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        print("navigated to machine family")
        actions.send_keys(machine_family).perform()  # Select the machine family (customize index if needed)
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        print("machine family selected")

    def select_series():
        """Selects the series."""
        print("navigating to series")
        actions.send_keys(Keys.TAB).perform() 
        actions.send_keys(Keys.ENTER).perform()# Navigate to the series dropdown
          # Select the series (customize index if needed)
        actions.send_keys(series).perform()
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.2)
        print("series selected")

    def machine_type_selection():
        """Selects the machine type."""
        actions.send_keys(Keys.TAB).perform()  
        # Navigate to the machine type dropdown
        actions.send_keys(Keys.ENTER).perform()
          # Select the machine type (customize index if needed)
        actions.send_keys(machine_type).perform()
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        print("machine type selected")

    def vcpu_and_memory():
        """Sets the vCPU and memory values."""
        for _ in range(5):  # Navigate to vCPU input
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        print("reached vcpu and memory")
        
        
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(vCPU).perform()# Enter the vCPU value
        print("vcpu selected")

        print("navigating for memory ")
        for _ in range(3):  # Navigate to memory input
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
    
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(ram).perform() # Enter the memory value
        print("memory selected")
        time.sleep(2)        
        for _ in range(1): #TILL BOOT TYPE SECELCTOR WE DO THE PROGRESSION ALONG WITH EXTENDED MEMEORY ICON THAT TAKES 2 TABS
            actions.send_keys(Keys.TAB).perform()
            time.sleep(5)
            
       
    def extension_memory_escape():
        print("extension activated")
        actions.send_keys(Keys.TAB).perform()
        actions.send_keys(Keys.TAB).perform()
        
    
    
    def boot_disk_type():
        for _ in range(disk_type):
            actions.send_keys(Keys.ARROW_RIGHT).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        print("boot disk type selected")
    
    def boot_disk_size():
        for _ in range(3):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Boot_disk_capacity).perform()
        
    def sustained_user_discounts():
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
 
    def region_selection():
        for _ in range(6): #iterate towards the region
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform() #open the dropdown
        
        actions.send_keys(region).perform()
        time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
    
    def with_sud_princing():
        for _ in range(4):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
    
    
    def one_year_commitment():
        for _ in range(9):
            actions.key_down(Keys.SHIFT).send_keys(Keys.TAB).key_up(Keys.SHIFT).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        for _ in range(9):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ARROW_RIGHT).perform()
        actions.send_keys(Keys.ENTER).perform()
        
    
    def three_year_commitment():
        actions.send_keys(Keys.ARROW_RIGHT).perform()
        actions.send_keys(Keys.ENTER).perform()
        
        
        
        

    
    time.sleep(1)
    try:
        home_page()
        select_instance()
        select_operating_system()
        select_machine_family()
        select_series()
        machine_type_selection()
        valid_families_series = {
            "general purpose": ["N2", "N4", "E2", "N2D"],
            "accelerator optimized": ["G2"]
        }
        if machine_family in valid_families_series and series in valid_families_series[machine_family]:
            print("Valid family and series going ahead for vcpu and memory")
        
            vcpu_and_memory()
            
            '''if series=="N2" or series=="N2D" or series=="N4" :
                extension_memory_escape()'''
        
        
        
        boot_disk_type()
        boot_disk_size()
        sustained_user_discounts()
        region_selection()
        with_sud_princing()
        time.sleep(3)
        label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "label.gt0C8e.MyvX5d.D0aEmf"))
            )
    
    # Extract the text content
        extracted_text = label.text
        print(f"sud pricing: {extracted_text}")
        with_sud_pricing=driver.current_url
        
        one_year_commitment()
        time.sleep(3)
        label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "label.gt0C8e.MyvX5d.D0aEmf"))
            )
    
    # Extract the text content
        extracted_text = label.text
        print(f"one year pricing: {extracted_text}")
        one_year_pricing=driver.current_url
        
        three_year_commitment()
        time.sleep(3)
        label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "label.gt0C8e.MyvX5d.D0aEmf"))
            )
    
    # Extract the text content
        extracted_text = label.text
        print(f"three year pricing: {extracted_text}")
        three_year_pricing=driver.current_url
        


        
        #cost_element = driver.find_element(By.CSS_SELECTOR, "span.MyvX5d.D0aEmf")
        #cost = cost_element.text
        # Using aria-label
        # Timeout of 10 seconds

        #download_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(@aria-label, 'Download estimate as .csv')]")))
        #download_button.click()
        """downloaded_files = glob.glob(f"{download_directory}/*.csv")
        if not downloaded_files:
            return "Error", "Error"
        latest_file = max(downloaded_files, key=os.path.getctime)

        total_price = extract_total_price(latest_file)
        print(f"Total Price: {total_price}")
        os.remove(latest_file)"""

        '''time.sleep(15)
        current_url = driver.current_url
        print(current_url)'''
        
        
        label = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "label.gt0C8e.MyvX5d.D0aEmf"))
            )
    
   
        
        '''tooltip_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tt-c6968"))  # Using ID for precision
        )
        # Click the element
        tooltip_element.click()'''
        print(with_sud_pricing)
        print(one_year_pricing)
        print(three_year_pricing)

        return  with_sud_pricing or 'error fetching the report',one_year_pricing or 'error fetching the report',three_year_pricing or 'error fetching the report'
    
    
    
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
        series = row["Series"].upper() if pd.notna(row["Series"]) else "E2"
        machine_type = row["Machine Type"].upper() if pd.notna(row["Machine Type"]) else "custom"
        vCPU = row["vCPUs"] if pd.notna(row["vCPUs"]) else 2
        ram = row["RAM"] if pd.notna(row["RAM"]) else 2
        Boot_disk_capacity= row["BootDisk Capacity"] if pd.notna(row["BootDisk Capacity"]) else 10
        region= row["Datacenter Location"] if pd.notna(row["Datacenter Location"]) else "Mumbai" 
        
        print(f"Processing row {index + 1} with OS: {os_name}, Instances: {no_of_instances},machine family: {machine_family}, series {series},machine type:{machine_type}")

        try:
            with_sud_pricing,one_year_pricing,three_year_pricing= process_row(driver, actions, os_name, no_of_instances, machine_family,series,machine_type,vCPU,ram,Boot_disk_capacity,region)
            results.append({"OS with version": os_name, "No. of Instances": no_of_instances, "Machine Family": machine_family,  "with sud pricing": with_sud_pricing, "one_year_pricing":one_year_pricing, "three_year_pricing":three_year_pricing})
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