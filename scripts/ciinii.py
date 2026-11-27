"""Search CiiiiNiiiiiiii and retrieve selected references using HTTP Basic auth."""

import argparse
import base64
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

HOST = "ciiiiniiiiiiii.lanet.sist.chukyo-u.ac.jp"
ORIGIN = f"https://{HOST}"
ARTICLE_PATH = re.compile(r"/articles/[^/]+/?")
HTML_LIMIT = 4 * 1024 * 1024
PDF_LIMIT = 100 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def same_origin(url):
    candidate = urlsplit(url)
    return candidate.scheme == "https" and candidate.netloc == HOST


def fetch(url, limit):
    if not same_origin(url):
        raise ValueError("Use an HTTPS URL on " + HOST)
    username = os.environ.get("CIINII_USERNAME")
    password = os.environ.get("CIINII_PASSWORD")
    if not username or not password:
        raise ValueError("Set CIINII_USERNAME and CIINII_PASSWORD in the local environment.")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    request = Request(url, headers={"Authorization": "Basic " + token})
    with build_opener(NoRedirect()).open(request, timeout=25) as response:
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError("The response exceeded the size limit.")
    return content


class Page(HTMLParser):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.links = {}
        self.title = []
        self.in_title = False
        self.href = None
        self.link_text = []

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "a":
            self.href = dict(attrs).get("href")
            self.link_text = []

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)
        if self.href:
            self.link_text.append(data)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "a" and self.href:
            url = urljoin(self.url, self.href)
            label = " ".join("".join(self.link_text).split())
            if same_origin(url) and (url not in self.links or label):
                self.links[url] = label
            self.href = None

    def items(self, include):
        return [
            {"title": label, "url": url}
            for url, label in self.links.items() if include(urlsplit(url).path)
        ]


def read_page(url):
    page = Page(url)
    page.feed(fetch(url, HTML_LIMIT).decode("utf-8"))
    page.close()
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("search").add_argument("query")
    sub.add_parser("article").add_argument("url")
    pdf = sub.add_parser("pdf")
    pdf.add_argument("url")
    pdf.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "search":
            query = args.query.strip()
            if not query:
                raise ValueError("Enter a search keyword.")
            url = ORIGIN + "/search?" + urlencode({"type": "article", "q": query})
            page = read_page(url)
            data = {"search_url": url, "articles": page.items(ARTICLE_PATH.fullmatch)}
        elif args.command == "article":
            if not ARTICLE_PATH.fullmatch(urlsplit(args.url).path):
                raise ValueError("Use an article detail URL from the search results.")
            page = read_page(args.url)
            data = {
                "title": " ".join("".join(page.title).split()),
                "pdf_links": page.items(lambda path: path.lower().endswith(".pdf")),
            }
        else:
            if not urlsplit(args.url).path.lower().endswith(".pdf"):
                raise ValueError("Use a PDF link from the article detail page.")
            content = fetch(args.url, PDF_LIMIT)
            if not content.startswith(b"%PDF-"):
                raise ValueError("The response is not a PDF.")
            with open(args.destination, "xb", opener=private_file) as output:
                output.write(content)
            data = {"saved_pdf": str(args.destination)}
    except HTTPError as error:
        reason = "Check the local credentials." if error.code in (401, 403) else "Check the site in a browser."
        parser.exit(1, f"CiiiiNiiiiiiii returned HTTP {error.code}. {reason}\n")
    except (OSError, URLError, ValueError) as error:
        parser.exit(1, f"CiiiiNiiiiiiii: {error}\n")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def private_file(path, flags):
    return os.open(path, flags, 0o600)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
