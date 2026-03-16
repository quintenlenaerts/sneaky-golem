import os
import sys
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlparse, unquote
from html.parser import HTMLParser


BASE_URL = "http://golem.fjfi.cvut.cz/shots/{shot_no}/"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href" and value:
                    self.links.append(value)


def get_links(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=10) as response:
        html = response.read().decode("utf-8", errors="ignore")

    parser = LinkParser()
    parser.feed(html)
    return parser.links


def download_file(url, save_path):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as response:
            content = response.read()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(content)

        print("Downloaded:", save_path)

    except Exception as e:
        print("Failed:", url, e)


def is_same_host(url, base_netloc):
    parsed = urlparse(url)
    return parsed.netloc in ("", base_netloc)


def crawl(url, local_dir, base_netloc, visited):
    if url in visited:
        return
    visited.add(url)

    try:
        links = get_links(url)
    except Exception as e:
        print("Failed to read directory:", url, e)
        return

    for link in links:
        if link in ("../", "./", "/", "#"):
            continue

        full_url = urljoin(url, link)
        parsed = urlparse(full_url)

        # skip links outside the golem host
        if not is_same_host(full_url, base_netloc):
            continue

        # skip query/hash weirdness
        if parsed.scheme not in ("http", "https"):
            continue

        rel_name = os.path.basename(parsed.path.rstrip("/"))
        rel_name = unquote(rel_name)

        if not rel_name:
            continue

        local_path = os.path.join(local_dir, rel_name)

        if full_url.endswith("/"):
            os.makedirs(local_path, exist_ok=True)
            crawl(full_url, local_path, base_netloc, visited)
        else:
            download_file(full_url, local_path)


def download_shot(shot_no):
    url = BASE_URL.format(shot_no=shot_no)
    parsed_base = urlparse(url)
    local_dir = f"shot_{shot_no}"

    os.makedirs(local_dir, exist_ok=True)
    crawl(url, local_dir, parsed_base.netloc, set())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_all.py <shot_number>")
        sys.exit(1)

    shot_no = sys.argv[1]
    download_shot(shot_no)