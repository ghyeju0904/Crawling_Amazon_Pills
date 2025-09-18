# -*- coding: utf-8 -*-  # 한글 주석이 깨지지 않도록 UTF-8로 저장합니다. 프로그램의 첫 줄에 위치해야 합니다.

import csv  # CSV 파일로 데이터를 저장할 때 사용합니다.
import json  # JSON 형식으로 데이터를 저장할 때 사용합니다.
import os  # 운영체제 기능 중 파일 경로 처리 기능을 사용하기 위해 불러옵니다.
from amazon import crawl_by_search  # 앞서 만든 'amazon.py' 파일에 있는 웹 크롤링 함수를 불러옵니다.

QUERY = "nutritional pills"  # 아마존 검색창에 넣을 검색어입니다. "영양제"의 영어 표현 중 하나예요.
OUT_BASE = "amazon_nutritional_pills"  # 저장할 파일 이름의 앞부분입니다. 확장자는 아래에서 붙습니다.

# 👉 이 함수는 상품 정보들을 CSV 파일로 저장하는 역할을 해요.
def save_csv(items, path):
    # CSV 파일을 새로 만들고, UTF-8-SIG 인코딩으로 열어요. (윈도우 한글 엑셀 호환됨)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        # CSV의 각 열 이름을 지정해요. 우리가 뽑아온 정보: 이미지 주소, 제목, 가격
        w = csv.DictWriter(f, fieldnames=["image_url", "title", "price"])
        w.writeheader()  # 첫 줄에 열 제목을 씁니다 (헤더)
        for row in items:  # 수집한 각 상품 정보를 하나씩 꺼내서
            w.writerow(row)  # 한 줄씩 CSV로 저장합니다.

# 👉 이 함수는 상품 정보들을 JSON 파일로 저장하는 역할을 해요.
def save_json(items, path):
    with open(path, "w", encoding="utf-8") as f:  # UTF-8 인코딩으로 파일을 열어요.
        # 'products'라는 키 아래 리스트 형태로 저장하고, 들여쓰기를 적용해서 보기 쉽게 저장합니다.
        json.dump({"products": items}, f, ensure_ascii=False, indent=2)

# 👉 이 코드는 "실행할 때만 작동"하게 설정된 부분이에요. (다른 파일에서 이 파일을 import만 하면 실행되지 않음)
if __name__ == "__main__":
    # 📌 크롤링 실행! → 'QUERY'로 최대 10페이지까지 아마존 검색 결과를 수집합니다.
    data = crawl_by_search(QUERY, max_pages=10)
    if __name__ == "__main__":
        data = crawl_by_search(QUERY, max_pages=10)
        data = [item for item in data if item["price"] != "가격 정보 없음"]



    # 저장할 파일 경로를 설정합니다. (현재 폴더 기준의 절대경로)
    csv_path = os.path.abspath(f"{OUT_BASE}.csv")
    json_path = os.path.abspath(f"{OUT_BASE}.json")

    # 크롤링한 데이터를 CSV, JSON 파일로 각각 저장합니다.
    save_csv(data, csv_path)
    save_json(data, json_path)

    # 저장이 완료되었음을 화면에 출력합니다. 몇 개 저장되었고 어디에 저장됐는지도 알려줘요.
    print(f"[DONE] {len(data)}개 저장 | CSV: {csv_path} | JSON: {json_path}")
