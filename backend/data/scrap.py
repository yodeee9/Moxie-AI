import pdfkit
import requests

def save_webpage_as_pdf(url, output_file):
    # WebページのHTMLを取得
    response = requests.get(url)
    if response.status_code == 200:
        # HTMLをPDFに変換して保存
        pdfkit.from_string(response.text, output_file)
        print(f"Saved {url} as {output_file}")
    else:
        print(f"Failed to retrieve {url}")

def save_multiple_pages_as_pdfs(urls, output_folder):
    for i, url in enumerate(urls):
        output_file = f"{output_folder}/page_{i+1}.pdf"
        save_webpage_as_pdf(url, output_file)

# 使用例
urls = [
    'https://www.chase.com/personal/credit-cards/card-resource-center/passwordpin',
    'https://www.chase.com/personal/credit-cards/card-resource-center/cardreplace',
    'https://www.chase.com/personal/credit-cards/card-resource-center/cc-payments',
    'https://www.chase.com/personal/credit-cards/card-resource-center/acct-servicing',
    'https://www.chase.com/personal/credit-cards/card-resource-center/profile-settings',
    'https://www.chase.com/personal/credit-cards/card-resource-center/statements',
    'https://www.chase.com/personal/credit-cards/card-resource-center/credit-reports',
    'https://www.chase.com/personal/credit-cards/card-resource-center/accountalerts',
    'https://www.chase.com/personal/credit-cards/card-resource-center/contactless-cards',
    'https://www.chase.com/personal/credit-cards/card-resource-center/stored-cards',
    'https://www.chase.com/personal/credit-cards/card-resource-center/digital-wallets',
    'https://www.chase.com/personal/credit-cards/card-resource-center/fraud-security',
    'https://www.chase.com/personal/credit-cards/card-resource-center/understanding-cc-accounts',
]

output_folder = 'output_pdfs'
save_multiple_pages_as_pdfs(urls, output_folder)
