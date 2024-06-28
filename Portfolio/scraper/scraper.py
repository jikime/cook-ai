from bs4 import BeautifulSoup
import requests
import re

class Scraper:
  def __init__(self, limit=10):
    self.__url = "https://www.musinsa.com/ranking/best"
    self.__params = {}

    self.__headers = {
      "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    self.__pattern = re.compile(r"[\d,]+원")
    self.__limit = limit
    
  def __build_message(self, item_box):
    # 브랜드명
    item_titles = item_box.find_all("p", class_="item_title")
    item_title = (item_titles[1] if len(item_titles) > 1 else item_titles[0]).findChild("a")
    brand = item_title.text.strip()
    
    # 상품명 및 링크
    item_link = item_box.find("p", class_="list_info").findChild("a")
    name = re.sub(r"\s{2}", "", item_link.text.strip())
    url = item_link["href"]
      
    # 가격
    item_price = item_box.find("p", class_="price")
    prices = self.__pattern.findall(item_price.text)
    
    # 사진
    img_box = item_box.find("div", class_="list_img").find("img")
    
    item = {
      "brand": brand,
      "name": name,
      "url": url,
      "original_price": prices[0],
      "sale_price": prices[1] if len(prices) > 1 else "",
      "image": img_box["data-original"]
    }
      
    return item
  
  def do(self):    
    response = requests.get(self.__url, params=self.__params, headers=self.__headers)
    soup = BeautifulSoup(response.text, "html.parser")
    item_boxes = soup.find("div", class_="list-box").find_all("li", class_="li_box")

    result = []
    count = 0
    for item_box in item_boxes:
      if count == self.__limit:
        break
      
      count += 1
      item = self.__build_message(item_box)      
      result.append(item)
      
    return result

if __name__ == "__main__":
  scraper = Scraper()
  items = scraper.do()
  print(items)