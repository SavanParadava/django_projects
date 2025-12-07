import os
import stat
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
import time

# 1. Setup Selenium (Headless Chrome)
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

print("Setting up ChromeDriver...")
# Download the driver
driver_path = ChromeDriverManager().install()

# --- FIX FOR ERRNO 8 ---
# If the manager points to the License file or a directory, fix the path to the binary
if "THIRD_PARTY_NOTICES" in driver_path or not driver_path.endswith("chromedriver"):
    # Look for the binary in the same directory
    base_dir = os.path.dirname(driver_path)
    possible_path = os.path.join(base_dir, "chromedriver")
    
    # If not found there, it might be in a subdir (common in newer versions)
    if not os.path.exists(possible_path):
        # Try finding it recursively or checking the 'chromedriver-linux64' subfolder
        possible_path = os.path.join(base_dir, "chromedriver-linux64", "chromedriver")
        
    driver_path = possible_path

# Ensure the driver is executable
if os.path.exists(driver_path):
    st = os.stat(driver_path)
    os.chmod(driver_path, st.st_mode | stat.S_IEXEC)
else:
    raise FileNotFoundError(f"Could not locate chromedriver binary at {driver_path}")
# -----------------------

print(f"Using driver at: {driver_path}")
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# ... Rest of your code (Step 2: Load the Page) ...

# 2. Load the Page
url = "https://codes.iccsafe.org/content/IBC2024V2.0/chapter-3-occupancy-classification-and-use"
print(f"Navigating to {url}...")
driver.get(url)

# 3. Handle Dynamic Loading (Scroll to bottom)
# The ICC site often lazy-loads content. We must scroll down to ensure everything renders.
print("Rendering page content...")
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for content to load
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 4. Extract Content
# We target the main content container. Note: Selectors can change. 
# If this fails, try finding 'main' or specific ID 'chapter-content'.
content_elements = []

try:
    # Attempt to find the main content wrapper
    # Common container classes on ICC might be 'chapter-content' or just standard tags
    # We will grab all text-heavy elements in order
    main_content = driver.find_element(By.TAG_NAME, "main") 
    
    # Get all child elements that usually contain text (headers, paragraphs, list items)
    tags = main_content.find_elements(By.CSS_SELECTOR, "h1, h2, h3, p, li, div.section")
    
    for tag in tags:
        text = tag.text.strip()
        if text:
            # Simple heuristic to determine font size/weight based on tag name
            tag_name = tag.tag_name.lower()
            content_elements.append((tag_name, text))
            
except Exception as e:
    print(f"Error finding specific content: {e}")
    # Fallback: Just get all text
    body_text = driver.find_element(By.TAG_NAME, "body").text
    content_elements.append(("p", body_text))

driver.quit()

# 5. Create PDF
print(f"Saving {len(content_elements)} elements to PDF...")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'IBC 2024 - Chapter 3', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Add fonts (using standard Arial)
# Note: FPDF doesn't support UTF-8 characters well in the default font.
# For complex symbols, you usually need to add a Unicode font (like DejaVuSans).
# This example uses 'latin-1' encoding which handles standard English text.

for tag, text in content_elements:
    try:
        # Encode/decode to handle some special characters roughly
        sanitized_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        if tag == 'h1':
            pdf.set_font("Arial", 'B', 16)
            pdf.ln(10)
            pdf.multi_cell(0, 10, sanitized_text)
            pdf.ln(5)
        elif tag == 'h2':
            pdf.set_font("Arial", 'B', 14)
            pdf.ln(8)
            pdf.multi_cell(0, 10, sanitized_text)
            pdf.ln(4)
        elif tag == 'h3':
            pdf.set_font("Arial", 'B', 12)
            pdf.ln(6)
            pdf.multi_cell(0, 10, sanitized_text)
            pdf.ln(2)
        else:
            # Paragraphs, list items, etc.
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 6, sanitized_text)
            pdf.ln(2)
            
    except Exception as e:
        print(f"Skipping a line due to encoding error: {e}")

pdf.output("IBC_Chapter_3.pdf")
print("Done! Saved as IBC_Chapter_3.pdf")