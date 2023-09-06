
# Importing scraping and data processing modules
# from dependencies.scraping.<file_name> import <class_name>
# from dependencies.scraping.<file_name> import <class_name>
# from dependencies.cleaning.<file_name> import <class_name>
# from dependencies.geocoding.<file_name> import <class_name>
# from dependencies.standardization.<file_name> import <class_name>

# Importing
from dependencies.scraping.Data_Commons_Scrapper import DataCommonsScraper
from dependencies.scraping.ChinaBidding import ChinaBiddingScraper
from dependencies.scraping.Etender import E_tenders
from dependencies.scraping.CPPPC import CPPPCScraper
from selenium import webdriver
from selenium.webdriver.common.by import By


def main_menu():
    print("Select a scraper:")
    print("1. Chinnabidding")
    print("2. CPPPC")
    print("3. Etenders")
    print("4. Data Commons")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        csv_file_path = 'Taiyo_Task\data\Chinabidding_Scrap.csv'
        # Create an instance of the ChinaBiddingScraper class
        scraper = ChinaBiddingScraper(csv_file_path)
        # Specify the URL to scrape
        url = 'https://www.chinabidding.com/en'  # Replace with the actual URL
        # Call the scrape_bidding_info method
        scraper.scrape_bidding_info(url)

    elif choice == "2":
        csv_file_location = "Taiyo_Task\data"
        scraper = CPPPCScraper(csv_file_location)
        scraper.create_csv_file()
        url = 'https://www.cpppc.org/en/PPPyd.jhtml'
        scraper.scrape_list_page(url)

    elif choice == "3":
        output_path = "Taiyo_Task\data\etenders.csv"
        scraper = E_tenders("https://etenders.gov.in/eprocure/app")
        scraper.scrape_tenders()


    elif choice == "4":
        print("You have selected Data Commons Scraper.")
        countries = ['American Samoa', 'Canada', 'France', 'United Kingdom','India']
        stat_var = input("Enter stat_var (default is 'Count_Person', press Enter to use default): ")
        if stat_var == "":
            stat_var = "Count_Person"
        scraper = DataCommonsScraper(countries, stat_var)
        dfs = scraper.scrape_data('city')
        scraper.generate_csv_dataset(dfs, custom_path='Taiyo_Task\data\Generated Datasets Data_Commons')
        print(dfs)

        

    elif choice == "5":
        exit()

    else:
        print("Invalid choice. Please select a valid option.")
        main_menu()

if __name__ == "__main__":
    while True:
        main_menu()


