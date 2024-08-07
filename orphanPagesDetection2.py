import requests
from bs4 import BeautifulSoup
import networkx as nx
from urllib.parse import urljoin, urlparse
import chardet

def get_links(url, base_url):
    try:
        response = requests.get(url)
        detected_encoding = chardet.detect(response.content)['encoding']
        response.encoding = detected_encoding if detected_encoding else 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(base_url, a_tag['href'])
            # Ignore links to fragments and mailto links
            if '#' in link or 'mailto:' in link:
                continue
            # Ensure we only crawl links within the same domain
            if urlparse(link).netloc == urlparse(base_url).netloc:
                links.add(link)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()

def crawl_website(start_url, max_depth=3):
    G = nx.DiGraph()
    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(start_url))
    to_crawl = [(start_url, 0)]
    crawled = set()

    while to_crawl:
        url, depth = to_crawl.pop()
        if url in crawled or depth > max_depth:
            continue
        crawled.add(url)
        print(f"Crawling: {url} at depth {depth}")
        links = get_links(url, base_url)
        for link in links:
            if link not in crawled:
                G.add_edge(url, link)
                to_crawl.append((link, depth + 1))
        print(f"Links found on {url}: {links}")

    return G

def find_orphan_pages(graph):
    all_pages = set(graph.nodes())
    non_orphan_pages = set(target for _, target in graph.edges())
    orphan_pages = all_pages - non_orphan_pages
    return orphan_pages

start_url = 'https://checkorphanpage.netlify.app/' # Replace with your website URL
graph = crawl_website(start_url)
orphan_pages = find_orphan_pages(graph)

print("Graph Nodes (Pages):")
print(list(graph.nodes))
print("\nGraph Edges (Links):")
print(list(graph.edges))

print("\nOrphan Pages:")
for page in orphan_pages:
    print(page)
 