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


index_mapping = {
    "General Purpose": {
        "index": 0,  # Machine family index
        "series": {
            "N1": {
                "index": 0,
                "machine_types": {
                    "Custom machine type": 0,
                    "f1-micro": 1,
                    "g1-small": 2,
                    "n1-standard-1": 3,
                    "n1-standard-2": 4,
                    "n1-standard-4": 5,
                    "n1-standard-8": 6,
                    "n1-standard-16": 7,
                    "n1-standard-32": 8,
                    "n1-standard-64": 9,
                    "n1-standard-96": 10,
                    "n1-highmem-2": 11,
                    "n1-highmem-4": 12,
                    "n1-highmem-8": 13,
                    "n1-highmem-16": 14,
                    "n1-highmem-32": 15,
                    "n1-highmem-64": 16,
                    "n1-highmem-96": 17,
                    "n1-highcpu-2": 18,
                    "n1-highcpu-4": 19,
                    "n1-highcpu-8": 20,
                    "n1-highcpu-16": 21,
                    "n1-highcpu-32": 22,
                    "n1-highcpu-64": 23,
                    "n1-highcpu-96": 24,
                },
            },
            "N2": {
                "index": 1,
                "machine_types": {
                    "Custom machine type": 0,
                    "n2-standard-2": 1,
                    "n2-standard-4": 2,
                    "n2-standard-8": 3,
                    "n2-standard-16": 4,
                    "n2-standard-32": 5,
                    "n2-standard-48": 6,
                    "n2-standard-64": 7,
                    "n2-standard-80": 8,
                    "n2-standard-96": 9,
                    "n2-standard-128": 10,
                    "n2-highmem-2": 11,
                    "n2-highmem-4": 12,
                    "n2-highmem-8": 13,
                    "n2-highmem-16": 14,
                    "n2-highmem-32": 15,
                    "n2-highmem-48": 16,
                    "n2-highmem-64": 17,
                    "n2-highmem-80": 18,
                    "n2-highmem-96": 19,
                    "n2-highmem-128": 20,
                    "n2-highcpu-2": 21,
                    "n2-highcpu-4": 22,
                    "n2-highcpu-8": 23,
                    "n2-highcpu-16": 24,
                    "n2-highcpu-32": 25,
                    "n2-highcpu-48": 26,
                    "n2-highcpu-64": 27,
                    "n2-highcpu-80": 28,
                    "n2-highcpu-96": 29,
                },
            },
            "N4": {
                "index": 2,
                "machine_types": {
                    "Custom machine type": 0,
                    "n4-standard-2": 1,
                    "n4-standard-4": 2,
                    "n4-standard-8": 3,
                    "n4-standard-16": 4,
                    "n4-standard-32": 5,
                    "n4-standard-48": 6,
                    "n4-standard-64": 7,
                    "n4-standard-80": 8,
                    "n4-highmem-2": 9,
                    "n4-highmem-4": 10,
                    "n4-highmem-8": 11,
                    "n4-highmem-16": 12,
                    "n4-highmem-32": 13,
                    "n4-highmem-48": 14,
                    "n4-highmem-64": 15,
                    "n4-highmem-80": 16,
                    "n4-highcpu-2": 17,
                    "n4-highcpu-4": 18,
                    "n4-highcpu-8": 19,
                    "n4-highcpu-16": 20,
                    "n4-highcpu-32": 21,
                    "n4-highcpu-48": 22,
                    "n4-highcpu-64": 23,
                    "n4-highcpu-80": 24,
                },
            },
            "E2": {
                "index": 3,
                "machine_types": {
                    "Custom machine type": 0,
                    "e2-micro": 1,
                    "e2-small": 2,
                    "e2-medium": 3,
                    "e2-standard-2": 4,
                    "e2-standard-4": 5,
                    "e2-standard-8": 6,
                    "e2-standard-16": 7,
                    "e2-standard-32": 8,
                    "e2-highmem-2": 9,
                    "e2-highmem-4": 10,
                    "e2-highmem-8": 11,
                    "e2-highmem-16": 12,
                    "e2-highcpu-2": 13,
                    "e2-highcpu-4": 14,
                    "e2-highcpu-8": 15,
                    "e2-highcpu-16": 16,
                    "e2-highcpu-32": 17,
                },
            },
            "N2D": {
                "index": 4,
                "machine_types": {
                    "Custom machine type": 0,
                    "n2d-standard-2": 1,
                    "n2d-standard-4": 2,
                    "n2d-standard-8": 3,
                    "n2d-standard-16": 4,
                    "n2d-standard-32": 5,
                    "n2d-standard-48": 6,
                    "n2d-standard-64": 7,
                    "n2d-standard-80": 8,
                    "n2d-standard-96": 9,
                    "n2d-standard-128": 10,
                    "n2d-standard-224": 11,
                    "n2d-highmem-2": 12,
                    "n2d-highmem-4": 13,
                    "n2d-highmem-8": 14,
                    "n2d-highmem-16": 15,
                    "n2d-highmem-32": 16,
                    "n2d-highmem-48": 17,
                    "n2d-highmem-64": 18,
                    "n2d-highmem-80": 19,
                    "n2d-highmem-96": 20,
                    "n2d-highcpu-2": 21,
                    "n2d-highcpu-4": 22,
                    "n2d-highcpu-8": 23,
                    "n2d-highcpu-16": 24,
                    "n2d-highcpu-32": 25,
                    "n2d-highcpu-48": 26,
                    "n2d-highcpu-64": 27,
                    "n2d-highcpu-80": 28,
                    "n2d-highcpu-96": 29,
                    "n2d-highcpu-128": 30,
                    "n2d-highcpu-224": 31,
                },
            },
        },
    },
    "Compute-Optimized": {
        "index": 1,
        "series": {
            "C2": {
                "index": 0,
                "machine_types": {
                    "c2-standard-4": 0,
                    "c2-standard-8": 1,
                    "c2-standard-16": 2,
                    "c2-standard-30": 3,
                    "c2-standard-60": 4,
                },
            },
            "C2D": {
                "index": 1,
                "machine_types": {
                    "c2d-standard-2": 0,
                    "c2d-standard-4": 1,
                    "c2d-standard-8": 2,
                    "c2d-standard-16": 3,
                    "c2d-standard-32": 4,
                    "c2d-standard-56": 5,
                    "c2d-standard-112": 6,
                    "c2d-highmem-2": 7,
                    "c2d-highmem-4": 8,
                    "c2d-highmem-8": 9,
                    "c2d-highmem-16": 10,
                    "c2d-highmem-32": 11,
                    "c2d-highmem-56": 12,
                    "c2d-highmem-112": 13,
                    "c2d-highcpu-2": 14,
                    "c2d-highcpu-4": 15,
                    "c2d-highcpu-8": 16,
                    "c2d-highcpu-16": 17,
                    "c2d-highcpu-32": 18,
                    "c2d-highcpu-56": 19,
                    "c2d-highcpu-112": 20,
                },
            },
            "H3": {
                "index": 2,
                "machine_types": {
                    "h3-standard-88": 0,
                },
            },
        },
    },

    # Memory-Optimized
    "Memory-Optimized": {
        "index": 2,
        "series": {
            "M1": {
                "index": 0,
                "machine_types": {
                    "m1-megamem-96": 0,
                    "m1-ultramem-40": 1,
                    "m1-ultramem-80": 2,
                    "m1-ultramem-160": 3,
                },
            },
            "M2": {
                "index": 1,
                "machine_types": {
                    "m2-megamem-416": 0,
                    "m2-ultramem-208": 1,
                    "m2-ultramem-416": 2,
                    "m2-hypermem-416": 3,
                },
            },
            "M3": {
                "index": 2,
                "machine_types": {
                    "m3-megamem-64": 0,
                    "m3-megamem-128": 1,
                    "m3-ultramem-32": 2,
                    "m3-ultramem-64": 3,
                    "m3-ultramem-128": 4,
                },
            },
        },
    },

    # Accelerator-Optimized
    "Accelerator-Optimized": {
        "index": 3,
        "series": {
            "A2": {
                "index": 0,
                "machine_types": {
                    "a2-highgpu-1g": 0,
                    "a2-highgpu-2g": 1,
                    "a2-highgpu-4g": 2,
                    "a2-highgpu-8g": 3,
                    "a2-megagpu-16g": 4,
                    "a2-ultragpu-1g": 5,
                    "a2-ultragpu-2g": 6,
                    "a2-ultragpu-4g": 7,
                    "a2-ultragpu-8g": 8,
                },
            },
            "A3": {
                "index": 1,
                "machine_types": {
                    "a3-highgpu-1g": 0,
                    "a3-highgpu-2g": 1,
                    "a3-highgpu-4g": 2,
                    "a3-highgpu-8g": 3,
                },
            },
            "G2": {
                "index": 2,
                "machine_types": {
                    "Custom machine type": 0,
                    "g2-standard-4": 1,
                    "g2-standard-8": 2,
                    "g2-standard-12": 3,
                    "g2-standard-16": 4,
                    "g2-standard-24": 5,
                    "g2-standard-32": 6,
                    "g2-standard-48": 7,
                    "g2-standard-96": 8,
                },
            },
        },
    },

    # Storage-Optimized
    "Storage-Optimized": {
        "index": 4,
        "series": {
            "Z3": {
                "index": 0,
                "machine_types": {
                    "z3-highmem-88": 0,
                    "z3-highmem-176": 1,
                },
            },
        },
    },
    
}




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
 


def process_row(driver, actions, os_name, no_of_instances,machine_family,series):
    """Processes a single row to calculate cost and retrieve URL."""
    os_index = get_os_index(os_name)
    machine_family_index = 0#0get_machine_family_index(machine_family) 
    series_index=1
    machine_type_index=1
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
        for _ in range(machine_family_index):  # Select the machine family (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        print("machine family selected")

    def select_series():
        """Selects the series."""
        print("navigating to series")
        actions.send_keys(Keys.TAB).perform() 
        actions.send_keys(Keys.ENTER).perform()# Navigate to the series dropdown
        for _ in range(series_index):  # Select the series (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(0.2)
        print("series selected")

    def machine_type():
        """Selects the machine type."""
        actions.send_keys(Keys.TAB).perform()  
        # Navigate to the machine type dropdown
        actions.send_keys(Keys.ENTER).perform()
        for _ in range(machine_type_index):  # Select the machine type (customize index if needed)
            actions.send_keys(Keys.ARROW_DOWN).perform()
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
        actions.send_keys(vcpu_value).perform()# Enter the vCPU value
        print("vcpu selected")

        print("navigating for memory ")
        for _ in range(3):  # Navigate to memory input
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
    
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(memory_value).perform() # Enter the memory value
        print("memory selected")
        
        for _ in range(4): #TILL BOOT TYPE SECELCTOR WE DO THE PROGRESSION ALONG WITH EXTENDED MEMEORY ICON THAT TAKES 2 TABS
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
            
       
        
    
    
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
        actions.send_keys(size).perform()
        
    def sustained_user_discounts():
        for _ in range(2):
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform()
 
    def region():
        for _ in range(6): #iterate towards the region
            actions.send_keys(Keys.TAB).perform()
            time.sleep(0.2)
        actions.send_keys(Keys.ENTER).perform() #open the dropdown
        for _ in range(region_index):
            actions.send_keys(Keys.ARROW_DOWN).perform()
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
        machine_type()
        valid_families_series = {
            "general purpose": ["N2", "N4", "E2", "N2D"],
            "accelerator optimized": ["G2"]
        }
        if machine_family in valid_families_series and series in valid_families_series[machine_family]:
            print("Valid family and series going ahead for vcpu and memory")
        
            vcpu_and_memory()
                    
        boot_disk_type()
        boot_disk_size()
        sustained_user_discounts()
        region()
        with_sud_princing()
        time.sleep(3)
        with_sud_pricing=driver.current_url
        
        one_year_commitment()
        time.sleep(3)
        one_year_pricing=driver.current_url
        
        three_year_commitment()
        time.sleep(3)
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
    
    # Extract the text content
        extracted_text = label.text
        print(f"Extracted Text: {extracted_text}")
        
        tooltip_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "tt-c6968"))  # Using ID for precision
    )
    # Click the element
        tooltip_element.click()
        print(with_sud_pricing)
        print(one_year_pricing)
        print(three_year_pricing)

        return  with_sud_pricing,one_year_pricing,three_year_pricing
    
    
    
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
        series = row["Series"].upper() if pd.notna(row["Series"]) else "default"
        print(f"Processing row {index + 1} with OS: {os_name}, Instances: {no_of_instances},machine family: {machine_family}, series {series}")

        try:
            with_sud_pricing,one_year_pricing,three_year_pricing= process_row(driver, actions, os_name, no_of_instances, machine_family,series)
            results.append({"OS with version": os_name, "No. of Instances": no_of_instances, "Machine Family": machine_family,  "URL": with_sud_pricing+' '+one_year_pricing+' '+three_year_pricing})
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