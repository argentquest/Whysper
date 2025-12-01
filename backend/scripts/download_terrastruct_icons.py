#!/usr/bin/env python3
"""
Terrastruct Icon Downloader

This script scrapes and downloads icons from https://icons.terrastruct.com/
to a local directory for offline use in D2 diagrams.

Usage:
    python download_terrastruct_icons.py

Output:
    Icons will be saved to: backend/static/terrastruct_icons/
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TerrastructIconScraper:
    """Scraper for downloading icons from terrastruct.com"""

    def __init__(self, output_dir: str = "backend/static/terrastruct_icons"):
        self.base_url = "https://icons.terrastruct.com"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded = 0
        self.failed = 0

    def get_page(self, url: str) -> str:
        """Fetch a page and return its HTML content"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.info(f"Failed to fetch {url}: {e}")
            return ""

    def extract_icon_urls(self, html: str) -> list:
        """Extract icon URLs from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        icon_urls = []

        # Find all links that end with .svg
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.svg'):
                full_url = urljoin(self.base_url, href)
                icon_urls.append(full_url)

        # Also check for img tags with svg sources
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.endswith('.svg'):
                full_url = urljoin(self.base_url, src)
                icon_urls.append(full_url)

        return list(set(icon_urls))  # Remove duplicates

    def extract_category_links(self, html: str) -> list:
        """Extract category/folder links from the main page"""
        soup = BeautifulSoup(html, 'html.parser')
        category_urls = []

        # Look for links that might be categories
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Categories typically have paths like /aws/, /gcp/, /azure/, etc.
            if href.startswith('/') and href.endswith('/') and len(href) > 2:
                full_url = urljoin(self.base_url, href)
                category_urls.append(full_url)

        return list(set(category_urls))

    def download_icon(self, url: str) -> bool:
        """Download a single icon"""
        try:
            # Parse URL to get the path
            parsed = urlparse(url)
            rel_path = parsed.path.lstrip('/')

            # Create local file path
            local_file = self.output_dir / rel_path
            local_file.parent.mkdir(parents=True, exist_ok=True)

            # Skip if already downloaded
            if local_file.exists():
                logger.debug(f"Skipping (exists): {rel_path}")
                return True

            # Download the icon
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            # Save to file
            local_file.write_bytes(response.content)
            logger.info(f"✓ Downloaded: {rel_path}")
            self.downloaded += 1

            # Be polite - don't hammer the server
            time.sleep(0.5)
            return True

        except Exception as e:
            logger.info(f"✗ Failed to download {url}: {e}")
            self.failed += 1
            return False

    def scrape(self):
        """Main scraping logic"""
        logger.info("Starting Terrastruct icon scraper...")
        logger.info(f"Output directory: {self.output_dir}")

        # Get main page
        html = self.get_page(self.base_url)
        if not html:
            logger.info("Failed to fetch main page. Exiting.")
            return

        # Extract category links
        categories = self.extract_category_links(html)
        logger.info(f"Found {len(categories)} categories")

        # Also check main page for icons
        icon_urls = self.extract_icon_urls(html)
        logger.info(f"Found {len(icon_urls)} icons on main page")

        # Visit each category
        for category_url in categories:
            logger.info(f"Exploring category: {category_url}")
            category_html = self.get_page(category_url)
            if category_html:
                category_icons = self.extract_icon_urls(category_html)
                icon_urls.extend(category_icons)
                logger.info(f"Found {len(category_icons)} icons in category")
                time.sleep(1)  # Be polite between categories

        # Remove duplicates
        icon_urls = list(set(icon_urls))
        logger.info(f"\nTotal unique icons found: {len(icon_urls)}")

        # Download all icons
        logger.info("\nStarting downloads...")
        for i, icon_url in enumerate(icon_urls, 1):
            logger.info(f"[{i}/{len(icon_urls)}] Downloading...")
            self.download_icon(icon_url)

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info(f"Download complete!")
        logger.info(f"Successfully downloaded: {self.downloaded}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)


def main():
    """Main entry point"""
    scraper = TerrastructIconScraper()
    scraper.scrape()


if __name__ == "__main__":
    main()
