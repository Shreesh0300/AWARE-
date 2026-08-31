import urllib.request
import re
import sys

def show_progress(block_num, block_size, total_size):
    # Quick math to show a progress percentage in the terminal
    downloaded = block_num * block_size
    if total_size > 0:
        percent = downloaded * 100 / total_size
        # Overwrite the same line so it doesn't flood the terminal
        sys.stdout.write(f"\r📥 Downloading: {percent:.1f}%")
        sys.stdout.flush()

url = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/deprecated/oa_bulk/oa_comm/txt/"
print("🔍 Scanning NCBI servers...")

try:
    # 1. Scrape the FTP directory HTML
    html = urllib.request.urlopen(url).read().decode('utf-8')
    
    # 2. Use Regex to find the first massive .tar.gz baseline file
    match = re.search(r'href="(oa_comm_txt\.[^"]+\.baseline\.[^"]+\.tar\.gz)"', html)
    
    if match:
        filename = match.group(1)
        download_url = url + filename
        print(f"🎯 Target Acquired: {filename}")
        print("⏳ Initiating download (This is a huge file, grab a coffee!)...")
        
        # 3. Download the file and trigger the progress tracker
        urllib.request.urlretrieve(download_url, filename, show_progress)
        print("\n✅ Download complete! Ready for extraction.")
    else:
        print("❌ Could not find the baseline file. NCBI might have moved it.")
except Exception as e:
    print(f"\n🚨 Connection Error: {e}")