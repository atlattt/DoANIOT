import sys
sys.stdout.reconfigure(encoding='utf-8')  # Để in ra được chữ có dấu
import requests
from bs4 import BeautifulSoup
import result
#url = 'https://mykasihterkini.confirm-ic.my.id/'  # Trang web malicious
#url='https://uis.ptithcm.edu.vn/#/home'  # Trang web benign

import requests
from bs4 import BeautifulSoup

def get_all_js_in_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Lấy tất cả các thẻ <script> có thuộc tính src
    scripts = soup.find_all('script', src=True)
    for script in scripts:
        script_url = script['src']
        # Lấy file JavaScript từ URL
        if not script_url.startswith('http'):  # Đảm bảo URL đầy đủ
            script_url = url + script_url
            print(script_url)
        try:
            js_content = requests.get(script_url).text
            feature_counts = result.analyze_javascript_code(js_content)
            X = result.change_data(feature_counts)
            my_prediction = result.predict_with_DENSE_CNN(X)
            # Phân tích mã JavaScript
            if my_prediction == 'Malicious':
                print(f"Mã độc hại phát hiện trong file: {script_url}")
                return "Malicious"
        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi tải {script_url}: {e}")
    
    # Lấy nội dung JavaScript inline (không có thuộc tính src)
    inline_scripts = soup.find_all('script', src=False)
    for script in inline_scripts:
        script_content = script.string
        if script_content:  # Kiểm tra nếu có mã JavaScript trong thẻ
            feature_counts = result.analyze_javascript_code(script_content)
            X = result.change_data(feature_counts)
            my_prediction = result.predict_with_DENSE_CNN(X)
            # Phân tích mã JavaScript
            if my_prediction == 'Malicious':
                print(f"Mã độc hại phát hiện trong inline JavaScript.")
                return  "Malicious"
    
    # Nếu không phát hiện mã độc hại trong các file hoặc inline JS
    print("Không phát hiện mã độc hại trong các file JavaScript hoặc inline JavaScript.")
    return "Benign"

#print(get_all_js_in_page(url))

#print(get_all_js_in_page(url))