# -*- coding: utf-8 -*-  # 이 파일 한글 주석 있으므로 UTF-8로 저장 필요.

from selenium.webdriver.common.by import By  # HTML 요소 어떤 방식(By.ID, By.CSS_SELECTOR 등)으로 찾을지 정하는 도구.
from selenium.webdriver.common.keys import Keys  # 키보드 입력(엔터 등) 흉내낼 때 사용.
from selenium.webdriver.support.ui import WebDriverWait  # 웹페이지에서 어떤 요소 나타날 때까지 기다려주는 기능.
from selenium.webdriver.support import expected_conditions as EC  # 위에서 기다리는 조건 정해주는 도구.
import time  # 기다리기나 일시정지 때 사용하는 기본 시간 관련 모듈.
import re # 리뷰 수, 퍼센터 추출용 정규표현식
from fetch import setup_driver, scroll_to_bottom  # 따로 만들어 놓은 드라이버 실행과 스크롤 함수(import).

# Amazon 홈페이지 URL 저장해두는 변수.
HOME_URL = "https://www.amazon.com/ref=nav_logo"

# 검색어 입력 텍스트 박스 위치 알려주는 XPath.
SEARCH_INPUT_XPATH = '//*[@id="twotabsearchtextbox"]'

# 검색 버튼 XPath.
SEARCH_BUTTON_XPATH = "/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[3]/div/span/input" # ⭐id="nav-search-submit-button" 으로 써도 되는지

# 요소 화면에 나타날 때까지 최대 sec초(기본 12초) 기다리는 함수.
def _wait(driver, by, sel, sec=12): # ⭐언더바 기능 : 내부(현 파일)에서만 사용하는 비공식 도우미 함수
    return WebDriverWait(driver, sec).until( # WebDriverWait(driver, sec) : 웹 브라우저에서 최대 sec초 동안 기다릴 준비, until(...) : ...한 조건이 만족될 때까지 기다림
        EC.visibility_of_element_located((by, sel)) # 해당 위치의 요소가 눈에 보일 때까지 기다림, 만약 시간이 다 지나도 안 보이면 오류가 남
    )

# 아마존에서 가끔 뜨는 'Continue shopping' 같은 중간 페이지(Interstitial) 넘기는 함수.
# 중간에 튀어나오는 방해창을 자동으로 처리하는 역할
def _handle_interstitial(driver): # def : 함수를 만들겠다, _handle_interstitial : 함수이름,(handle : 처리하다, interstitial : 중간 광고창이나 확인창) 
    html = driver.page_source  # 현재 웹페이지 전체 HTML 내용을 html이라는 변수에 저장
    if ("Continue shopping" in html) or ("Click the button below" in html) or ("쇼핑" in html): # 페이지 안에 "Continue shopping" 이나 "Click the button below" 또는 "쇼핑"이라는 단어가 있으면 방해창으로 판단
        # 중간 페이지라면 여러 가지 버튼 후보 XPath로 확인.
        xps = [ # 방해창에 있는 버튼을 찾기 위해서 , 2가지 형태의 버튼 형태 XPATH 리스트 만듦
            "//input[@type='submit' and contains(@value,'Continue shopping')]",
            "//button[contains(.,'Continue shopping') or contains(.,'쇼핑 계속')]",
        ]
        for xp in xps: # XPAHT 리스트를 하나씩 돌면서 실제 버튼 있는지 확인
            btns = driver.find_elements(By.XPATH, xp)  # 해당 XPAHT에 해당하는 버튼 모두 찾기
            if btns: # 버튼이 하나라도 있다면
                btns[0].click()  # 버튼 클릭해서 방해창 닫고 계속 진행
                time.sleep(2)  # 버튼 클릭해서 방해창 닫고 계속 진행하는데 클릭 후 2초 기다려서 페이지 넘어가게 설정
                break # 더이상 확인할 필요 없으면 반복문 멈춤

# 검색어 아예 URL에 붙여서 바로 검색 결과 페이지로 이동하는 함수.
def perform_search(driver, query): # perform_search : 검색 수행, (driver : 브라우저 조종하는 리모컨 역할, query : 우리가 검색하고 싶은 단어)
    from urllib.parse import quote  # 필요한 도구를 불러오는 코드, quote : 한글이나 특수문자가 들어간 검색어를 웹주소(URL)에 안전하게 넣을 수 있도록 바꿔주는 함수
    search_url = f"https://www.amazon.com/s?k={quote(query)}"  # f-string을 사용해서 문자열을 조립하는 코드, https://www.amazon.com/s?k=검색어 형태가 아마존의 검색 주소, quote(query)로 바꾼 검색어를 {}에 끼워 넣어서 정확한 주소를 만듦
    driver.get(search_url)  # 아마존 검색 결과 페이지로 브라우저가 직접 열리는 것, (drive : 작동시키는 리모컨, .get(url)은 그 주소로 이동하라는 뜻)
    _handle_interstitial(driver)  # 방해 요소를 자동으로 눌러서 없애주는 역할, 없으면 무시하고 있으면 자동 클릭
    _wait(driver, By.CSS_SELECTOR, "div.s-main-slot", sec=12)  # 검색 결과 보일 때까지 대기, (By.CSS_SELECTOR : 요소를 CSS 선택자 방식으로 찾겠음(By.ID, By.XPATH도 있는데, 이건 HTML 구조에서 특정 태그나 클래스, 아이디 등을 지정하는 방법), "div.s-main-slot" : 아마존 검색 결과가 담겨있는 HTML 요소, 이 부분이 보일 때까지 기다리면 "상품이 다 뜬 상태"라는 뜻)
    return search_url # 뒤로 돌아올 때 필요한 함수

# 각 상품(카드) 담고 있는 HTML 블록 찾는 함수.
def _find_cards(driver): # 아마존 내의 상품 카드를 하나씩 찾는 함수
    selectors = [ # div.~~ : CSS 선택자, 3개를 사용하는 이유는 아마존의 페이지 구조가 시간, 사용, 지역에 따라 바뀌기도 하고 광고가 섞여있을수도 있어서 경우의 수를 늘려놓은 것
        "div.s-main-slot > div[data-asin][data-component-type='s-search-result']", # 아마존 상품 ID(모든 상품에 붙음), div.s-main-slot : 상품들이 쭉 나열되어있는 메인 블록, > : 그 안의 바로 아래 자식만 취급, div[data-asin] : data-asin 이라는 상품 ID 속성이 있는 div,[data-component-type='s-search-result']: 그리고 그 요소가 검색결과용 상품 블록일 때
        "div.s-main-slot div.s-result-item[data-asin]", # 상품들이 나열되는 전체 영역, div.s-main-slot : 상품 전체 영역, div.s-result-item[data-asin]: 상품 ID가 있고 s-result-item 클래스를 가진 블록, s-result-item : 아마존 웹사이트에서 상품 하나하나를 담고 있는 블록(div)에 자주 붙는 css클래스 이름
        "div[data-component-type='s-search-result'][data-asin]", # 검색 결과에 나오는 상품, data-component-type="s-search-result": 검색 결과용 상품, data-asin: 아마존 상품 고유번호가 있는 블록
    ]
    # 아마존 상품을 찾기 위해 css 선택자(selector)들을 순서대로 시도해보는 반복문
    for css in selectors: # select라는 리스트 안의 다양한 css 선택자들이 들어있는데 그 선택자들을 하나씩 꺼내면서 반복해보는 for문, css는 선택자 문자열 하나하나를 나타냄
        cards = driver.find_elements(By.CSS_SELECTOR, css)  # 셀렉터로 요소들 찾음, (driver.find_elements(...)는 화면에서 여러 개의 웹 요소를 찾는 명령어,By.CSS_SELECTOR는 CSS 선택자 방식으로 찾겠다는 뜻, css는 위에서 꺼낸 선택자 문자열, find_elements는 여러 개를 찾아서 리스트로 돌려줌, 반대로 find_element 는 하나만 찾음)
        if cards: # 만약 cards 리스트가 비어 있지 않다면(=뭔가 있다면)
            return cards # 찾은 결과를 바로 리턴하고 함수종료 => 제일 먼저 유효한 셀렉터에서 상품들을 찾으면 멈추고 결과 준다는 뜻
    return []  # 어떤 셀렉터도 유효하지 않아서 상품을 못 찾으면 빈 리스트 반환 = 아무것도 못 찾았다는 뜻

# 현재 페이지에서 모든 상품 정보 추출하는 함수.
def extract_products_on_page(driver): # on_page -> 현재 페이지에서,  extract_products -> 모든 상품 정보 추출, driver(브라우저 조종하는 셀레니움 객체)를 받아서 실행
    scroll_to_bottom(driver)  # 페이지 아래로 스크롤해서 상품들 모두 불러오게 함. 지연 로딩된 상품들도 전부 화면에 보이게 함
    cards = _find_cards(driver) # 모든 상품 카드(블록)들을 리스트로 가져옴
    print(f"[DEBUG] cards: {len(cards)}")  # 찾은 상품 카드 수 출력 , (len() : 리스트나 문자열이 몇 개의 항목을 가지고 있는지 세주는 함수 ex. [DEBUG] cards: 20)

    results = []  # 결과 담을 빈 리스트
    for card in cards: # 모든 상품 카드(블록)에서 상품들을 하나씩 for문으로 돌리기
        try:
            title = card.find_element(By.CSS_SELECTOR, "h2 span").text.strip()  # card.find_element() : card 라는 상품 카드 안에서 특정정보(By.CSS_SELECTOR : 상품 제목이 들어있는 HTML 위치를 CSS 셀렉터로 알려줌, "h2 span" : h2 안의 span 요소 의미)를 찾는 함수, .text : HTML 안에 있는 글자만 가져오기 .strip : 앞뒤에 있는 공백(띄어쓰기, 줄바꿈 등)을 없애줌
        except:
            try:
                title = card.find_element(By.CSS_SELECTOR, "h2 a span").text.strip() # 아마존은 상품마다 HTML 구조가 약간씩 달라서 방법 하나 더 추가
            except:
                title = "상품명 없음"  # 못 찾으면 기본값, 방법2로도 못 찾으면 진짜 없는거라고 생각하고 상품명 없음으로 추출

        try: # 가격
            price_whole = card.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
            price_fraction = card.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text.strip()
            price = f"{price_whole}.{price_fraction}"  # 소수점 포함 가격
        except:
            try:
                price = card.find_element(By.CSS_SELECTOR, "span.a-offscreen").text.strip()
                price = price.replace("$", "").strip()  # $ 제거
            except:
                price = "가격 정보 없음"

        try: # 이미지
            image = card.find_element(By.CSS_SELECTOR, "img").get_attribute("src").strip()  # 이미지 주소 가져오기
        except:
            image = "이미지 없음"

        # (선택) 상세 링크도 보관해두면 디버깅 유용
        try:
            link = card.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
        except:
            link = None

        print(f"[DEBUG] {title} | {price} | {image}") # 프린트 fstring ex. [DEBUG] 비타민 | 10.00달러 | 이미지주소
        results.append({ # results : 상품들을 담는 "빈 바구니(리스트)", .append(...) : 바구니에 하나씩 넣는다 
            "title": title, # 리스트에 상품명 1, 상품명 2, 상품명 3 ...
            "price": price, # 리스트에 가격 1, 가격 2, 가격 3 ...
            "image_url": image, # 리스트에 이미지 1, 이미지 2, 이미지 3 ...
            "detail_url" : link            
        }) # 나중에 이 데이터들을 csv나 json 파일로 저장하려고 미리 정리해두는 것

    print(f"[DEBUG] 실제 추출된 상품 수: {len(results)}") 
    return results

# 상세 페이지: 좌측 썸네일 이미지 전부 추출
def extract_detail_images(driver):
    thumbs = driver.find_elements(By.CSS_SELECTOR, "#altImages img")
    urls = []
    for t in thumbs:
        src = (t.get_attribute("src") or "").strip()
        if src:
            urls.append(src)
    print(f"[INFO] 상세 썸네일 {len(urls)}개 수집")
    return urls

# 상세 페이지: 평점 정보 (평균, 총리뷰수, 별점 분포)
def extract_ratings(driver):
    avg = None
    total = None
    hist = {}

    # 평균 별점
    try:
        alt = driver.find_element(By.CSS_SELECTOR, "#acrPopover .a-icon-alt").text.strip()
        avg = float(alt.split(" ")[0])  # "4.2 out of 5 stars" → 4.2
    except:
        pass

    # 총 리뷰 수
    try:
        total_txt = driver.find_element(By.CSS_SELECTOR, "#acrCustomerReviewText").text.strip()
        digits = re.findall(r"\d+", total_txt.replace(",", ""))
        if digits:
            total = int("".join(digits))
    except:
        pass

    # 별점 분포 (팝오버)
    try:
        pop = driver.find_element(By.CSS_SELECTOR, "#acrPopover")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pop)
        time.sleep(0.3)
        pop.click()

        vis = WebDriverWait(driver, 8).until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "div.a-popover[aria-hidden='false']"
            ))
        )
        rows = vis.find_elements(By.CSS_SELECTOR, "tr")
        for r in rows:
            try:
                star_txt = r.find_element(By.CSS_SELECTOR, "th").text
                star_num = int(re.findall(r"\d", star_txt)[0])
                perc_txt = r.find_element(By.CSS_SELECTOR, "td.a-text-right a").text
                perc = int(re.findall(r"\d+", perc_txt)[0])
                hist[star_num] = perc
            except:
                continue
    except:
        pass

    return {"avg": avg, "total": total, "histogram_percent": hist}

# 다음 페이지로 이동하는 함수.
def _click_next(driver):
    scroll_to_bottom(driver)  # 현재 페이지 끝까지 스크롤.
    try:
        nxt = WebDriverWait(driver, 12).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next"))
        )

        if nxt.get_attribute("aria-disabled") == "true":
            print("[INFO] 다음 페이지 없음 (버튼 비활성)")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nxt)  # 버튼 위치로 이동
        time.sleep(0.5)
        nxt.click()  # 다음 버튼 클릭

        print("[WAIT] 다음 페이지 콘텐츠 로딩을 위해 15초 대기 중...")
        time.sleep(15)  # 콘텐츠 로드 대기

        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
        )  # 로딩 확인
        return True
    except Exception as e:
        print("[SKIP] 다음 페이지 이동 실패:", e)
        return False

# 검색어로 여러 페이지 순회하면서 전체 상품 수집하는 함수.
def crawl_by_search(query, max_pages=10):
    driver = setup_driver()  # 웹드라이버 실행 (크롬 브라우저 띄우기)
    try:
        search_url = perform_search(driver, query)  # 검색 실행
        all_items = []  # 전체 결과 저장 리스트
        page = 1  # 현재 페이지 번호
        while True:
            print(f"[INFO] {page}페이지 수집 중")
            items = extract_products_on_page(driver)

            # 각 상품 상세 진입
            for item in items:
                if not item.get("detail_url"):
                    continue
                try:
                    driver.get(item["detail_url"])
                    time.sleep(1.5)

                    detail_imgs = extract_detail_images(driver)
                    rating_info = extract_ratings(driver)

                    item["detail_images"] = detail_imgs
                    item["rating"] = rating_info
                    print(f"[INFO] 상세 수집 완료: {item['title']}")
                except Exception as e:
                    print(f"[ERROR] 상세 수집 실패: {e}")
                finally:
                    # 다시 검색 결과로 돌아오기
                    driver.get(search_url)
                    _wait(driver, By.CSS_SELECTOR, "div.s-main-slot", sec=12)

            all_items.extend(items)

            if page >= max_pages:
                break
            moved = _click_next(driver)
            if not moved:
                break
            page += 1
    finally:
        driver.quit()
    return all_items