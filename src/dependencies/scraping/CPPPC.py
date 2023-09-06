#CCPC

import csv
import re
from datetime import datetime
from requests import Session
from lxml import html

class CPPPCScraper:
    def __init__(self, csv_file_path):
        self.session = Session()
        self.common_file_date = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.csv_file_path = csv_file_path

    def create_csv_file(self):
        self.file = open(f'{self.csv_file_path}/CCPC_Scrap.csv', 'w', encoding='utf-8', newline='')
        self.row = csv.writer(self.file)
        self.row.writerow([
            "Rundatetime",
            "SiteAccessDate",
            "ArticleType",
            "ArticleName",
            "PostDate",
            "Editor",
            "View",
            "ArticleFrom",
            "ArticleDesc",
            "ArticleUrl",
            # "ArticleImageUrl",
        ])

    def scrape_list_page(self, url):
        tree = html.fromstring(self.session.get(url).text)

        for article in tree.xpath('//ul[@class="new-content ppp-list"]//li'):
            def get_by_xpath(path): return ''.join(article.xpath(path))

            # list page data
            rundatetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            site_access_date = get_by_xpath('//div[@id="headerDate"]/text()')
            article_name = get_by_xpath('.//a[@class="content-title"]/text()')
            article_desc = get_by_xpath('.//div[@class="content-content"]/text()')
            article_url = 'https://www.cpppc.org{}'.format(get_by_xpath('.//a[@class="content-title"]/@href'))
            # article_img = f'https://www.cpppc.org{get_by_xpath(".//img//@src")}'

            # fetching detail page data
            tree_detail = html.fromstring(self.session.get(article_url).text)
            editors_view = ''.join(tree_detail.xpath('//div[@class="common-card detail-card"]//h1/following-sibling::p[contains(.,"EDITER")]/text()'))
            article_type = tree_detail.xpath('//div[@class="component-menu-item component-menu-item-active"]/a/text()')[0]
            article_date = tree_detail.xpath('//div[@class="common-card detail-card"]//h1/following-sibling::p[1]/text()')[0]
            article_from = tree_detail.xpath('//div[@class="common-card detail-card"]//h1/following-sibling::p[contains(.,"FROM")]/text()')[-1].split('：')[-1].strip()

            article_editor = re.search(r'EDITOR：(.+?)\s', editors_view)
            article_view = re.search(r'VIEW：(\d+)', editors_view)

            self.row.writerow([
                rundatetime,
                site_access_date,
                article_type,
                article_name,
                article_date if article_date else 'N/A',
                article_editor.group(1) if article_editor else 'N/A',
                article_view.group(1) if article_view else 'N/A',
                article_from,
                article_desc,
                article_url,
                # article_img
            ])

        self.file.close() 