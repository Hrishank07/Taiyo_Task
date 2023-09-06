import datacommons_pandas as dc
import pycountry
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker


class DataCommonsScraper:
    def __init__(self, countries, stat_var):
        self.countries = self.__get_country_dcid(countries)
        self.stat_var = stat_var
        self.__ts_columns = {}

    def __build_ts_df(self, places, country):
        try:
            # Build a dataframe from the API call
            df_stats = dc.build_time_series_dataframe(places, self.stat_var)
            # adding name column (city, state, or name)
            df_stats['County/State_name'] = df_stats.index.map(dc.get_property_values(df_stats.index, 'name'))
            df_stats['County/State_name'] = df_stats['County/State_name'].str[0]
            return df_stats
        except:
            print('no data found for', country)
            return None

            
    def __get_country_dcid(self, country_names):
        country_dcids = {}
        for country_name in country_names:
            country = pycountry.countries.get(name=country_name)
            if country is None:
                print("Country name typed invalid! no code can be provided for " + country_name)
            else:
                code = country.alpha_3
                country_dcid = 'country/' + code
                country_dcids[country_name] = country_dcid
                # country_dcids.append(country_dcid)

        return country_dcids


    def scrape_data(self, place_type):
        dfs_collected = {}
        country_dcid = list(self.countries.values())
        for country in country_dcid:
            if place_type == 'state':
                states_each_country = dc.get_places_in(country_dcid, 'State')
                states = states_each_country[country]
                df_stats = self.__build_ts_df(states, country)
            elif place_type == 'county':
                counties_each_country = dc.get_places_in(country_dcid, 'County')
                counties = counties_each_country[country]
                df_stats = self.__build_ts_df(counties, country)
            elif place_type == 'city':
                cities_each_country = dc.get_places_in(country_dcid, 'City')
                cities = cities_each_country[country]
                df_stats = self.__build_ts_df(cities, country)
            else:
                print("ERROR type of place not specified!")
                return None
            dfs_collected[self.stat_var + "_" + country[8:] + '_ts'] = df_stats
        return dfs_collected


    def __standardize_years(self, df):
        standardized_years = []
        for col in df.columns[:-1]:  # except last column which is not year column
            col = pd.to_datetime(col).year
            col = str(col)
            standardized_years.append(col)
        standardized_years.append(df.columns[-1])
        df.columns = standardized_years
        return df


    def __calc_sample_frequency(self, df):
        start_year = int(df.columns[0])
        years = list(map(int, df.columns[:-1]))
        diffs = []
        for row in df.iterrows():
            prev = start_year
            later = -1
            count = 0
            diff = 0
            row = list(row[1].iloc)[:-1]
            for i, value in enumerate(row):
                later = -1
                if pd.isna(value):
                    continue
                else:
                    later = i
                    diff = diff + (years[later] - prev)
                    count += 1
                    prev = years[later]
            diff = diff + (years[later] - prev)
            count += 1
            diffs.append(diff / count)
        df['sample_frequency'] = diffs
        return df


    def __conform_to_standard(self, df, df_name):
        start_date = df.columns[0]
        end_date = df.columns[-2]
        # 1 sample frequency
        df = self.__standardize_years(df)
        df = self.__calc_sample_frequency(df)
        df['timestamps'] = '{' + '{}:{}'.format(start_date, end_date) + '}'
        df['name'] = self.stat_var + "_over_time"
        df['units'] = 'year' # statistical variables are measured year-by-year
        df['url'] = 'https://datacommons.org/tools/statvar#' + self.stat_var
        df['domain'] = df.dtypes[0] # domain is the type of the statistical variable
        country_code = df_name.split('_')[-2]
        country_name = list(self.countries.keys())[list(self.countries.values()).index('country/'+country_code)]
        df['aug_id'] = df.index
        df['original_id'] = df.index
        df = df.reset_index()
        df['country_code'] = country_code
        df['country_name'] = country_name

        return df

    
    def generate_csv_dataset(self, dfs, custom_path=None):
        for df_name in dfs.keys():
            df = dfs[df_name]
            conformed_df = self.__conform_to_standard(df, df_name)
            
            if custom_path:
                path = os.path.join(os.curdir, custom_path)
            else:
                path = os.path.join(os.curdir, 'data', 'Generated Datasets Data_Commons')
            
            if not os.path.exists(path):
                os.makedirs(path)
            
            conformed_df.to_csv(os.path.join(path, df_name + ".csv"))
            print('saved', df_name, 'in data folder')
            


    # def generate_csv_dataset(self, dfs):
    #     #save the folder in the data folder in the root directory
    #     for df_name, df in dfs.items():
    #         df = self.__conform_to_standard(df, df_name)
    #         df.to_csv('../data/' + df_name + '.csv', index=False)
    #         print('saved', df_name, 'in data folder')
    #         self.__ts_columns[df_name] = df.columns
    #     return self.__ts_columns

        
# for df_name in dfs.keys():
#             df = dfs[df_name]
#             conformed_df = self.__conform_to_standard(df, df_name)
#             path = os.curdir + 'data/Generated Datasets Data_Commons/'
#             if not os.path.exists(path):
#                 os.makedirs(path)
#                 conformed_df.to_csv('Generated Datasets/' + df_name + ".csv")
#             else:
#                 conformed_df.to_csv('Generated Datasets/' + df_name + ".csv")