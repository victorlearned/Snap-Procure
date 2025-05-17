from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

class ProcurementScraper:
    """
    A tool for scraping product data from home improvement store websites.
    """

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, output_dir: str = 'data'):
        """Initialize the scraper with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _parse_delivery_options(self, delivery_element) -> Dict[str, str]:
        """Parse delivery options from the delivery element."""
        try:
            # This is a simplified example - actual implementation will depend on the website structure
            delivery_text = delivery_element.get_text(' ', strip=True).lower()

            # Extract delivery date if available
            delivery_date = None
            if 'delivery' in delivery_text or 'arrives' in delivery_text:
                # Look for date patterns like 'by Mon, May 20' or 'on 05/20'
                import re
                date_patterns = [
                    r'(?:by|on)\s+(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}',
                    r'\d{1,2}/\d{1,2}(?:/\d{2,4})?',
                    r'(?:in\s+)?(\d+)\s*(?:-\s*\d+)?\s*(?:day|business day|week)'
                ]

                for pattern in date_patterns:
                    match = re.search(pattern, delivery_text)
                    if match:
                        delivery_date = match.group(0)
                        break

            # Estimate delivery speed
            delivery_speed = 'standard'
            if 'same day' in delivery_text or 'today' in delivery_text:
                delivery_speed = 'same_day'
            elif 'next day' in delivery_text or '1 day' in delivery_text:
                delivery_speed = 'next_day'
            elif '2 day' in delivery_text or '2-day' in delivery_text:
                delivery_speed = 'two_day'

            return {
                'delivery_text': delivery_text,
                'delivery_date': delivery_date,
                'delivery_speed': delivery_speed,
                'delivery_price': '0.00'  # This would be extracted from the page
            }
        except Exception as e:
            print(f"Error parsing delivery options: {e}")
            return {}

    def scrape_home_depot(self, product: str) -> List[Dict]:
        """
        Scrape product data from Home Depot.
        
        Args:
            product: The product to search for
            
        Returns:
            List[Dict]: List of product dictionaries with detailed information
        """
        try:
            base_url = "https://www.homedepot.com"
            search_url = f"{base_url}/s/{product.replace(' ', '%20')}"

            print(f"\n🔍 Searching Home Depot for: {product}")
            response = requests.get(search_url, headers=self.HEADERS)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            products = []

            # Find all product containers (update selector based on actual site structure)
            product_containers = soup.select('.product-pod--default, .product-pod')

            if not product_containers:
                print("⚠️ No products found on the page. The site structure might have changed.")
                return products

            print(f"Found {len(product_containers)} products on the first page")

            for item in product_containers:
                try:
                    # Extract product URL
                    link_element = item.select_one('a[data-testid="product-title"]')
                    if not link_element or 'href' not in link_element.attrs:
                        continue

                    # Ensure we have a clean, absolute URL
                    product_url = self._ensure_absolute_url(
                        link_element['href'], 
                        'https://www.homedepot.com'
                    )

                    # Extract product name
                    name = link_element.get_text(strip=True)

                    # Extract price
                    price_element = item.select_one('.price-format__main-price')
                    price = price_element.get_text(strip=True) if price_element else 'Price not available'

                    # Get delivery information
                    delivery_element = item.select_one('.delivery-options, .delivery__subtitle')
                    delivery_info = self._parse_delivery_options(delivery_element) if delivery_element else {}

                    # Construct product data
                    product_data = {
                        'store': 'Home Depot',
                        'name': name,
                        'url': product_url,
                        'price': price,
                        'timestamp': datetime.now().isoformat(),
                        **delivery_info
                    }

                    products.append(product_data)

                except Exception as e:
                    print(f"⚠️ Error parsing product: {str(e)}")
                    continue

            print(f"✅ Successfully scraped {len(products)} products from Home Depot")
            return products

        except requests.RequestException as e:
            print(f"❌ Error accessing Home Depot: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error while scraping Home Depot: {str(e)}")
            return []

    def scrape_lowes(self, product: str) -> List[Dict]:
        """
        Scrape product data from Lowe's.
        
        Args:
            product: The product to search for
            
        Returns:
            List[Dict]: List of product dictionaries with detailed information
        """
        try:
            base_url = "https://www.lowes.com"
            search_url = f"{base_url}/search?searchTerm={product.replace(' ', '%20')}"

            print(f"\n🔍 Searching Lowe's for: {product}")
            response = requests.get(search_url, headers=self.HEADERS)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            products = []

            # Find all product containers (update selector based on actual site structure)
            product_containers = soup.select('.product-item, .product-wrapper')

            if not product_containers:
                print("⚠️ No products found on the page. The site structure might have changed.")
                return products

            print(f"Found {len(product_containers)} products on the first page")

            for item in product_containers:
                try:
                    # Extract product URL
                    link_element = item.select_one('a[data-selector="product-title"]')
                    if not link_element or 'href' not in link_element.attrs:
                        continue

                    # Ensure we have a clean, absolute URL
                    product_url = self._ensure_absolute_url(
                        link_element['href'], 
                        'https://www.lowes.com'
                    )

                    # Extract product name
                    name = link_element.get_text(strip=True)

                    # Extract price
                    price_element = item.select_one('.primary')
                    price = price_element.get_text(strip=True) if price_element else 'Price not available'

                    # Get delivery information
                    delivery_element = item.select_one('.delivery-options, .delivery__subtitle')
                    delivery_info = self._parse_delivery_options(delivery_element) if delivery_element else {}

                    # Construct product data
                    product_data = {
                        'store': "Lowe's",
                        'name': name,
                        'url': product_url,
                        'price': price,
                        'timestamp': datetime.now().isoformat(),
                        **delivery_info
                    }

                    products.append(product_data)

                except Exception as e:
                    print(f"⚠️ Error parsing product: {str(e)}")
                    continue

            print(f"✅ Successfully scraped {len(products)} products from Lowe's")
            return products

        except requests.RequestException as e:
            print(f"❌ Error accessing Lowe's: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error while scraping Lowe's: {str(e)}")
            return []

    def scrape_all_stores(self, product: str) -> pd.DataFrame:
        """Scrape product data from all configured stores."""
        all_products = []

        # Scrape from each store
        all_products.extend(self.scrape_home_depot(product))
        all_products.extend(self.scrape_lowes(product))

        # Convert to DataFrame
        df = pd.DataFrame(all_products)

        # Save to CSV
        if not df.empty:
            filename = f"{self.output_dir}/procurement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"Data saved to {filename}")

        return df

# Example usage
if __name__ == "__main__":
    scraper = ProcurementScraper()
    results = scraper.scrape_all_stores("2x4x8 lumber")
    print(f"Found {len(results)} products")