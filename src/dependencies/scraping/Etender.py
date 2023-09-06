import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

class E_tenders:

    def __init__(self, URL):
        self.URL = URL

    def get_soup(self):
        try:
            r = requests.get(self.URL)
            r.raise_for_status()  # Raise an exception for non-200 response codes
            soup = BeautifulSoup(r.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve data from the website: {str(e)}")
            return None

    def extract_data(self, soup):
        if not soup:
            return None

        head_lines = soup.find("tr", class_="list_header")
        td_elements = head_lines.find_all('td')
        pd_columns = [td.get_text(strip=True) for td in td_elements]

        # Extracting the data from the website by finding the table rows and table data
        data_rows = soup.find_all("tr", class_=["even", "odd"])
        all_rows = []

        #for loop to extract the data from the website
        for row in data_rows:
            td_row_data = row.find_all('td')
            pd_rows = [td.get_text(strip=True) for td in td_row_data]
            all_rows.append(pd_rows)

        df = pd.DataFrame(columns=pd_columns)
        for row_data in all_rows:
            df = pd.concat([df, pd.DataFrame([row_data], columns=pd_columns)], ignore_index=True)
        
        return df

    def clean_data(self, df):
        if df is None:
            return None

        # Data Cleaning and Preprocessing from the scraped data from the website for extracting tender title, reference number, organization name, location, closing date, and tender value
        df["Tender Title"] = df["Tender Title"].str.replace(r"^\d+\.\s*", "", regex=True)
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df.dropna(inplace=True)
        df.drop_duplicates(inplace=True)



        return df

    def save_to_csv(self, df, output_path):
        if df is not None:
            df['Source URL'] = self.URL
            df['Scraping Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # df.to_csv("Etenders.csv", index=False)
            #do df to csv to the specified path
            df.to_csv(output_path, index=False)
            print("Data saved successfully to data.csv")

    def scrape_tenders(self):
        soup = self.get_soup()
        df = self.extract_data(soup)
        cleaned_df = self.clean_data(df)
        self.save_to_csv(cleaned_df,output_path= "Taiyo_Task\data\etenders.csv")
