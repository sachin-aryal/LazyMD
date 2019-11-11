# coding=utf-8
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from tkinter import END

START_URL = "http://www.charmm-gui.org/?doc=input/solution"
WORKING_DIRECTORY = os.path.abspath(".")
MAX_WAIT_PERIOD = 600

PROTEIN_PSF = "Protein_PSF.tcl"
COMBINE_SCRIPT = "1_combine.tcl"
COMBINED = "combined.pdb"
LIGAND_MOL2 = "Ligand.mol2"
OUTPUT_DIRECTORY = os.path.join(WORKING_DIRECTORY, "output")
# "/".join(sys.argv[0].split("/")[:-1])

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)


def execute_commands(folder, output_box):
    """
    Execute the two commands in a serial manner.
    """
    os.chdir(folder)
    try:
        protein_psf_script = os.path.join(folder, PROTEIN_PSF)
        combine_script = os.path.join(folder, COMBINE_SCRIPT)
        proc = subprocess.Popen(["vmd", "-dispdev", "text", "-e", protein_psf_script])
        proc.communicate()
        proc = subprocess.Popen(["vmd", "-dispdev", "text", "-e", combine_script])
        proc.communicate()
        output_box.insert(END, PROTEIN_PSF + " and " + COMBINE_SCRIPT + " executed.")
    except Exception as ex:
        output_box.insert(END, "Error Occured: " + str(ex))
    os.chdir(WORKING_DIRECTORY)


def download_wait(path_to_downloads):
    """
    :param path_to_downloads: 
    See if any file name endswith .crdownload to check download is progress.
     If .crdownload found, sleep for 5 seconds and check again.
    """
    dl_wait = True
    while dl_wait:
        time.sleep(5)
        dl_wait = False
        for fname in os.listdir(path_to_downloads):
            if fname.endswith('.crdownload'):
                dl_wait = True


def upload_data(folder, output_box):
    browser = None
    try:
        """
        Perform the automation work with chromedriver.
        """
        COMBINED_FILE = os.path.join(folder, COMBINED)
        LIGAND_MOL2_FILE = os.path.join(folder, LIGAND_MOL2)

        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory": OUTPUT_DIRECTORY}
        options.add_experimental_option("prefs", prefs)
        # options.add_argument("headless")
        # options.add_argument("window-size=1920,1080")
        browser = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
        browser.minimize_window()
        # Open the initial url in the browser.
        browser.get(url=START_URL)
        """
        Choose file and upload “combined.pdb” and then choose “PDB” for the format and go to next page.
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(
            EC.element_to_be_clickable((By.XPATH, ".//input[@type='radio' and "
                                                  "@value='PDB']")))
        browser.find_element_by_xpath(".//input[@type='radio' and @value='PDB']").click()
        browser.find_element_by_name("file").send_keys(COMBINED_FILE)
        browser.find_element_by_xpath("//*[@id='nav_title']").click()
        output_box.insert(END, "Step 1 Completed Successfully.")
        print("Step 1 Completed Successfully.")
        """
        Check “hetero” because it is not selected initially.
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(
            EC.element_to_be_clickable((By.NAME, "chains[HETA][checked]")))
        browser.find_element_by_name('chains[HETA][checked]').click()
        browser.find_element_by_id("nextBtn").click()
        output_box.insert(END, "Step 2 Completed Successfully.")
        print("Step 2 Completed Successfully.")
        """
        Select the “the mol2 file uploaded…” and upload “ligand.mol2”, then choose “preserve hydrogen coordinates”.
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="rename[LIG]_cgenff"]/input[4]')))
        browser.find_element_by_xpath('//*[@id="rename[LIG]_cgenff"]/input[4]').click()
        browser.find_element_by_name("mol2_cgenff[LIG]").send_keys(LIGAND_MOL2_FILE)
        browser.find_element_by_id("hbuild_checked").click()
        browser.find_element_by_id("nextBtn").click()
        output_box.insert(END, "Step 3 Completed Successfully.")
        print("Step 3 Completed Successfully.")
        """
        uncheck change waterbox type to “octahedral” and uncheck “”include ions”
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(
            EC.element_to_be_clickable((By.ID, "ion_checked")))
        browser.find_element_by_xpath("//select[@name='solvtype']/option[text()='Octahedral']").click()
        include_ions = browser.find_element_by_id("ion_checked")
        if include_ions.get_attribute('checked'):
            include_ions.click()
        browser.find_element_by_id("nextBtn").click()
        output_box.insert(END, "Step 4 Completed Successfully.")
        print("Step 4 Completed Successfully.")
        """
        click to go to next page.
        """
        try:
            WebDriverWait(browser, MAX_WAIT_PERIOD).until_not(EC.visibility_of_element_located((By.ID, "overlay")))
        except Exception:
            pass
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(EC.element_to_be_clickable((By.ID, "nextBtn")))
        next_btn = browser.find_element_by_id("nextBtn")
        next_btn.click()
        output_box.insert(END, "Step 5 Completed Successfully.")
        print("Step 5 Completed Successfully.")
        """
        choose “NAMD” and change temperature to “310 K”
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fsolution'
                                                                                            '"]/table[3]/tbody/tr['
                                                                                            '3]/td/input')))
        namd = browser.find_element_by_name("namd_checked")
        if not namd.get_attribute('checked'):
            namd.click()
        temperature = browser.find_element_by_xpath('//*[@id="fsolution"]/table[3]/tbody/tr[3]/td/input')
        temperature.clear()
        temperature.send_keys("310")
        browser.find_element_by_id("nextBtn").click()
        output_box.insert(END, "Step 6 Completed Successfully.")
        print("Step 6 Completed Successfully.")
        """
         Download the .tgz file and save it in the working directory.
        """
        WebDriverWait(browser, MAX_WAIT_PERIOD).until_not(EC.visibility_of_element_located((By.ID, "overlay")))
        WebDriverWait(browser, MAX_WAIT_PERIOD).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="input"]/a')))
        browser.find_element_by_xpath('//*[@id="input"]/a').click()
        output_box.insert(END, "Download in Progress.")
        print("Download in Progress.")
        """
        Wait till download is completed.
        """
        download_wait(OUTPUT_DIRECTORY)
        output_box.insert(END, "Download Completed..")
        print("Download Completed..")
        browser.quit()
    except Exception as ex:
        if browser:
            browser.quit()
        raise Exception


def run_automation(folder, output_box):
    retry = 0
    while retry < 5:
        try:
            output_box.insert(END, "Process started.")
            execute_commands(folder, output_box)
            upload_data(folder, output_box)
            output_box.insert(END, "Process Completed.")
            break
        except Exception as ex:
            import traceback
            traceback.print_exc()
            output_box.insert(END, "Error Occured: " + str(ex))
            output_box.insert(END, "Retry Attempt: "+str(retry))
        retry += 1
