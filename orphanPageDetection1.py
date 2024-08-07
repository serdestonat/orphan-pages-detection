import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class WebCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = set([base_url])
        self.all_links = set()

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            return None

    def extract_links(self, page_content, current_url):
        soup = BeautifulSoup(page_content, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href.startswith('#'):
                continue  # Ignore anchor links
            full_url = urljoin(current_url, href)
            parsed_url = urlparse(full_url)
            if parsed_url.netloc == urlparse(self.base_url).netloc:
                links.add(full_url)
        return links

    def crawl(self):
        while self.to_visit:
            current_url = self.to_visit.pop()
            if current_url not in self.visited:
                page_content = self.fetch_page(current_url)
                if page_content:
                    links = self.extract_links(page_content, current_url)
                    self.all_links.update(links)
                    self.to_visit.update(links)
                self.visited.add(current_url)
                time.sleep(1)  # Be polite and avoid overloading the server
        return self.visited, self.all_links

    def find_orphan_pages(self):
        visited, all_links = self.crawl()
        orphan_pages = visited - all_links
        return orphan_pages

if __name__ == "__main__":
    base_url = 'https://checkorphanpage.netlify.app'  # Replace with your website URL
    crawler = WebCrawler(base_url)
    orphan_pages = crawler.find_orphan_pages()
    print(f"Orphan pages: {orphan_pages}")