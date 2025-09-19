# -*- coding: utf-8 -*-  # 한글 주석 깨지지 않도록 UTF-8 인코딩 지정.

from selenium import webdriver  # 크롬 브라우저 자동으로 움직이기 위한 도구.
from selenium.webdriver.chrome.options import Options  # 크롬 실행 때 다양한 설정(옵션) 넣기 위해 사용.
from selenium.webdriver.chrome.options import Options
import time

# ✅ 크롬 브라우저 실행 때 필요한 설정들 넣고, 실행 준비 함수.
def setup_driver():
    chrome_options = Options()  # 크롬 옵션 설정 가능 빈 객체 생성.

    chrome_options.add_argument("--no-sandbox")  # 리눅스 권한 문제 방지 설정.
    chrome_options.add_argument("--disable-dev-shm-usage")  # 메모리 관련 오류 줄이기 위한 설정.
    chrome_options.add_argument("--window-size=1920,1080")  # 브라우저 크기 넓게 지정해 웹사이트 잘 보이게 함.

    # 웹사이트 "사람이 쓰는 브라우저"라고 생각하도록 속이기 위한 정보.
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"--user-agent={ua}")  # 위에서 만든 사용자 정보(User-Agent) 넣음.
    chrome_options.add_argument("--lang=ko-KR")  # 브라우저 언어 한국어 설정.

    driver = webdriver.Chrome(options=chrome_options)  # 위에서 만든 설정들로 크롬 드라이버 실행.

    # 좀 더 확실하게 브라우저에 언어와 사용자정보 알려주는 코드.
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua, "platform": "Windows"})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
        "headers": {"Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"}  # 한국어 제일 우선 언어 설정.
    })

    return driver  # 이렇게 준비된 드라이버 다른 코드에서 사용 가능하도록 되돌려줌.


# ✅ 웹페이지 자동으로 천천히 스크롤 내려가면서 숨겨진 정보 로딩 함수.
def scroll_to_bottom(driver, step_px=600, pause=0.3):
    # 현재 웹페이지 전체 높이 가져옴 (스크롤 내리기 전 기준).
    last = driver.execute_script("return document.body.scrollHeight")

    import time  # 잠깐 기다리는 기능 필요 부분에서 time 불러옴.

    while True:  # 무한 반복 시작. 나중에 조건 만족 시 종료.
        driver.execute_script(f"window.scrollBy(0,{step_px});")  # 화면 아래로 step_px만큼 스크롤.
        time.sleep(pause)  # 너무 빨리 움직이지 않도록 잠깐 쉬어줌.

        # 스크롤 후 웹페이지 전체 높이 다시 가져옴.
        cur = driver.execute_script("return document.body.scrollHeight")

        if cur == last:  # 스크롤 전과 후 높이 같다면 더 이상 내려갈 내용 없다고 판단.
            break  # 반복 멈춤.

        last = cur  # 페이지 높이 늘어났다면 새로운 높이로 업데이트.
