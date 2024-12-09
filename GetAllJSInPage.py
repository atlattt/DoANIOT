import sys
sys.stdout.reconfigure(encoding='utf-8')  # Để in ra được chữ có dấu
import requests
from bs4 import BeautifulSoup

#url = 'https://uis.ptithcm.edu.vn/#/home'  # Thay bằng URL của trang web

def get_all_js_in_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Khởi tạo biến để lưu trữ toàn bộ nội dung các thẻ <script>
    all_scripts_content = ""

    # Lấy nội dung từ các thẻ <script> và nối vào biến
    scripts = soup.find_all('script')
    for script in scripts:
        script_content = script.string
        if script_content:  # Bỏ qua các thẻ không có nội dung giữa <script></script>
            all_scripts_content += script_content + "\n"
    return all_scripts_content
# In ra hoặc xử lý tiếp biến all_scripts_content
#print(get_all_js_in_page(url))

 