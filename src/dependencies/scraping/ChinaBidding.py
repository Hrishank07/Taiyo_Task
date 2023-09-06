# import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

class ChinaBiddingScraper:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.driver = webdriver.Chrome()  # You need to initialize the drivers here
        self.inner_driver = webdriver.Chrome()

    def scrape_bidding_info(self, url):
        ptrn = "https://[\w./-]+"
        self.driver.get(url)
        time.sleep(5)

        # Click on the element using XPATH
        xpath = '//*[@id="bidding"]/div[2]/div[2]/ul/li[2]/a'
        self.driver.find_element(By.XPATH, xpath).click()
        time.sleep(2)

        # Define the XPATH for the button to load more items
        xpath_button = '//*[@id="bidding"]/div[2]/div[3]/div[1]/div[2]'

        while True:
            try:
                button = self.driver.find_element(By.XPATH, xpath_button)
                button.click()
                time.sleep(5)
            except:
                break

        # Define the XPATH for the tender items
        X_path_tenders = '//*[@id="bidding"]/div[2]/div[3]/div[1]/ul/li'
        elements = self.driver.find_elements(By.XPATH, X_path_tenders)
        print(f"Total elements found: {len(elements)}")

        # Create a list to store the extracted data
        data_to_save = []

        for ele in elements:
            abc = ele.get_attribute("innerHTML")
            aa = re.findall(ptrn, abc)
            if len(aa) > 0:
                self.inner_driver.get(aa[0])
                dd = '//*[@id="bidding"]/div[3]/div/div[4]'

                try:
                    # Extract the main text
                    main_element = self.inner_driver.find_element(By.XPATH, dd)
                    main_text = main_element.get_attribute("innerHTML")
                    # print(main_text)

                    # Define the regex patterns
                    ptrn_loan_number = r"Loan Number :[\w.-]+"
                    ptrn_bidding_no = r"Bidding No :[\w.-]+"
                    ptrn_bidding_agency = r"Bidding Agency :[\w\s.,]+"
                    ptrn_purchasers = r"Purchasers :[\w\s&;.,]+"
                    ptrn_bidding_type = r"Bidding Type :[\w\s]+"
                    ptrn_deadline_for_submitting = r"Deadline for Submitting Bids :[\w-]+"

                    # Extract the data using regex, don't include the title of the data
                    loan_no = re.search(ptrn_loan_number, main_text).group()
                    bidding_no = re.search(ptrn_bidding_no, main_text).group()
                    bidding_agency = re.search(ptrn_bidding_agency, main_text).group()
                    purchasers = re.search(ptrn_purchasers, main_text).group()
                    bidding_type = re.search(ptrn_bidding_type, main_text).group()
                    deadline = re.search(ptrn_deadline_for_submitting, main_text).group()
                    print(loan_no, bidding_no, bidding_agency, purchasers, bidding_type, deadline, sep="\n")
                    print()

                    # Append the extracted data to the list and only save the data to the list from the variables after the : sign
                    # data_to_save.append([loan_no, bidding_no, bidding_agency, purchasers, bidding_type, deadline])
                    data_to_save.append([loan_no[13:], bidding_no[12:], bidding_agency[16:], purchasers[12:], bidding_type[14:], deadline[30:]])

                except:
                    pass

        # Write the data to a CSV file
        with open(self.csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # Write the header row
            writer.writerow(["Loan Number", "Bidding No", "Bidding Agency", "Purchasers", "Bidding Type", "Deadline"])

            # Write the data rows
            writer.writerows(data_to_save)
