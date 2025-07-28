import requests
import json
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pyperclip
from bs4 import BeautifulSoup

# --- 헬퍼 클래스 (GeminiAPI, NaverAutoPoster) ---
class GeminiAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
    def generate_content(self, prompt, max_tokens=1500, temperature=0.7):
        url = f"{self.base_url}/{self.model}:generateContent"
        headers = {'Content-Type': 'application/json'}
        params = {'key': self.api_key}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        generation_config = {"maxOutputTokens": max_tokens, "temperature": temperature}
        payload["generationConfig"] = generation_config
        try:
            response = requests.post(url, headers=headers, params=params, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Gemini API 요청 오류: {e}")
            return None
    def extract_text(self, response):
        if not response: return "❌ API 응답 없음"
        try: return response['candidates'][0]['content']['parts'][0]['text']
        except Exception: return "❌ 텍스트 추출 실패"

class NaverAutoPoster:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, username, password):
        try:
            print("네이버 로그인 페이지로 이동 중...")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            time.sleep(2)
            
            print("아이디 입력 필드 클릭...")
            id_input = self.wait.until(EC.element_to_be_clickable((By.ID, "id")))
            id_input.click()
            
            print("아이디 입력 중...")
            pyperclip.copy(username)
            time.sleep(0.5)
            id_input.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            print("비밀번호 입력 필드 클릭...")
            pw_input = self.driver.find_element(By.ID, "pw")
            pw_input.click()
            
            print("비밀번호 입력 중...")
            pyperclip.copy(password)
            time.sleep(0.5)
            pw_input.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            print("로그인 버튼 클릭...")
            login_btn = self.driver.find_element(By.ID, "log.login")
            login_btn.click()
            
            print("로그인 처리 중...")
            time.sleep(3)
            
            current_url = self.driver.current_url
            if "naver.com" in current_url and "nidlogin" not in current_url:
                print("✅ 로그인 성공!")
                return True
            else:
                time.sleep(2)
                current_url = self.driver.current_url
                if "naver.com" in current_url and "nidlogin" not in current_url:
                    print("✅ 로그인 성공!")
                    return True
                else:
                    print("❌ 로그인 실패 또는 추가 인증 필요")
                    print(f"현재 URL: {current_url}")
                    return False
                
        except Exception as e:
            print(f"❌ 로그인 실패: {e}")
            return False

    def post(self, title, content, image_paths=None):
        try:
            print("블로그 작성 페이지로 이동 중...")
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            
            print("iframe으로 전환 중...")
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame")))
            self.driver.switch_to.frame(iframe)
            time.sleep(2)
            
            try:
                short_wait = WebDriverWait(self.driver, 2)
                cancel_button = short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-popup-button-cancel")))
                print("임시저장 팝업 취소 버튼 클릭...")
                cancel_button.click()
                time.sleep(1)
            except:
                print("임시저장 팝업 없음 - 넘어감")
            
            try:
                short_wait = WebDriverWait(self.driver, 1)
                help_close_button = short_wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-help-panel-close-button")))
                print("도움말 패널 닫기 버튼 클릭...")
                help_close_button.click()
                time.sleep(1)
            except:
                print("도움말 패널 닫기 버튼 없음 - 넘어감")

            # === 제목 입력 로직 ===
            print("제목 입력 중...")
            title_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-title-text")))
            pyperclip.copy(title)
            actions = ActionChains(self.driver)
            actions.click(title_element).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).pause(0.5).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            print(f"✅ 제목 입력 성공: {title}")

            # === 내용 입력 로직 ===
            print("내용 입력 중...")
            content_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".se-component.se-text.se-l-default")))
            content_element.click()
            time.sleep(1)
            pyperclip.copy(content)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(3)
            print("✅ 내용 입력 성공.")

            # === 이미지 첨부 로직 (안정성 강화 버전) ===
            if image_paths:
                print("이미지 첨부 시작...")
                content_body = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".se-main-container")))
                content_body.click()
                ActionChains(self.driver).send_keys(Keys.END).perform()
                time.sleep(0.5)
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                time.sleep(1)

                for image_path in image_paths:
                    try:
                        file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                        
                        initial_image_count = len(self.driver.find_elements(By.CSS_SELECTOR, ".se-component-image img, .se-image-resource img"))
                        abs_path = os.path.abspath(image_path)
                        print(f"   - 첨부 시도: {os.path.basename(image_path)}")
                        file_input.send_keys(abs_path)
                        
                        WebDriverWait(self.driver, 15).until(
                            lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".se-component-image img, .se-image-resource img")) > initial_image_count
                        )
                        
                        print(f"   - ✅ 첨부 확인: {os.path.basename(image_path)}")
                        time.sleep(2)

                    except Exception as e:
                        print(f"   - ❌ 이미지 첨부 실패: {os.path.basename(image_path)}, 오류: {e}")
                
                print("✅ 모든 이미지 첨부 완료.")

            # iframe에서 빠져나오기
            self.driver.switch_to.default_content()
            time.sleep(2)
            
            # 발행(게시) 버튼 클릭 - 여러 선택자 시도
            print("발행 버튼 클릭 중...")
            publish_button_selectors = [
                "button.publish_btn__m9KHH",  # 제공해주신 HTML의 정확한 클래스
                "button[class*='publish_btn']",
                "button[class*='publish']",
                "button:contains('발행')",
                ".publish_btn__m9KHH",
                "button .text__d09H7"  # '발행' 텍스트가 있는 버튼
            ]
            
            publish_button = None
            for selector in publish_button_selectors:
                try:
                    if selector == "button:contains('발행')":
                        # XPath로 텍스트 기반 검색
                        publish_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '발행')]")))
                    else:
                        publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"   - 발행 버튼 찾음: {selector}")
                    break
                except Exception as e:
                    print(f"   - 선택자 실패: {selector}")
                    continue
            
            if not publish_button:
                print("❌ 발행 버튼을 찾을 수 없습니다. 수동으로 확인이 필요합니다.")
                time.sleep(10)  # 수동 확인을 위한 대기
                return False
            
            # JavaScript로 클릭 시도 (일반 클릭이 안 될 경우를 대비)
            try:
                publish_button.click()
                print("   - ✅ 일반 클릭 성공")
            except Exception as e:
                print(f"   - 일반 클릭 실패, JavaScript 클릭 시도: {e}")
                self.driver.execute_script("arguments[0].click();", publish_button)
                print("   - ✅ JavaScript 클릭 성공")
            
            time.sleep(3)
            
            # 최종 발행 확인 버튼 클릭 - 여러 선택자 시도
            print("최종 발행 확인 버튼 클릭 중...")
            final_publish_selectors = [
                "button[class*='btn_apply']",
                "button[class*='confirm']",
                "button[class*='ok']",
                ".layer_popup button[class*='apply']",
                ".popup button[class*='confirm']",
                "//button[contains(text(), '발행')]",
                "//button[contains(text(), '확인')]",
                "//button[contains(text(), '게시')]"
            ]
            
            final_publish_button = None
            for selector in final_publish_selectors:
                try:
                    if selector.startswith("//"):
                        # XPath 선택자
                        final_publish_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        # CSS 선택자
                        final_publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"   - 최종 발행 버튼 찾음: {selector}")
                    break
                except Exception as e:
                    print(f"   - 최종 발행 선택자 실패: {selector}")
                    continue
            
            if final_publish_button:
                try:
                    final_publish_button.click()
                    print("   - ✅ 최종 발행 버튼 클릭 성공")
                except Exception as e:
                    print(f"   - 최종 발행 일반 클릭 실패, JavaScript 클릭 시도: {e}")
                    self.driver.execute_script("arguments[0].click();", final_publish_button)
                    print("   - ✅ 최종 발행 JavaScript 클릭 성공")
            else:
                print("⚠️ 최종 발행 확인 버튼을 찾을 수 없습니다. 첫 번째 발행 버튼만으로 완료될 수 있습니다.")
            
            WebDriverWait(self.driver, 30).until(EC.url_contains("PostView.naver"))
            print(f"✅ 포스팅 최종 완료: {title}")
            return True
            
        except Exception as e:
            screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ 포스팅 중 심각한 오류 발생! 스크린샷 저장: {screenshot_path}")
            print(f"   오류 상세 정보: {e}")
            return False

    def close(self):
        if self.driver: self.driver.quit()

def crawl_url_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.extract()
        text = soup.get_text(separator='\n', strip=True)
        return text[:2000] 
    except Exception as e:
        print(f"   - URL 텍스트 크롤링 실패: {url}, 오류: {e}")
        return ""

def download_play_store_images(url, save_dir='images'):
    print(f"   - Google Play Store URL 발견: 이미지 다운로드 시도...")
    downloaded_paths = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 커버 아트 (대표 이미지) 찾기
        cover_art_tag = soup.find('img', {'alt': 'Cover art'})
        if cover_art_tag and cover_art_tag.get('src'):
            img_url = cover_art_tag['src']
            img_data = requests.get(img_url).content
            file_path = os.path.join(save_dir, f"cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(file_path, 'wb') as handler:
                handler.write(img_data)
            downloaded_paths.append(file_path)
            print(f"     - ✅ 커버 아트 다운로드 성공: {file_path}")

        # 2. 첫 번째 스크린샷 찾기
        screenshot_tag = soup.find('img', {'alt': 'Screenshot image'})
        if screenshot_tag and screenshot_tag.get('src'):
            img_url = screenshot_tag['src']
            img_data = requests.get(img_url).content
            file_path = os.path.join(save_dir, f"screenshot1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            with open(file_path, 'wb') as handler:
                handler.write(img_data)
            downloaded_paths.append(file_path)
            print(f"     - ✅ 스크린샷 다운로드 성공: {file_path}")

    except Exception as e:
        print(f"   - ❌ 구글 플레이 스토어 이미지 다운로드 중 오류 발생: {e}")
    
    return downloaded_paths

# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
# ★★★★★★★★★ 프롬프트 수정: 본문 서식 및 가독성 강화 ★★★★★★★★★
# ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
def create_advanced_prompt(title, referral_id, crawled_contents):
    enhanced_title = title
    if referral_id and referral_id != '없음':
        enhanced_title = f"{title} (추천인 코드: {referral_id})"
    
    prompt = f"""
    당신은 저작권법을 철저히 준수하는 전문 블로그 작가입니다. 다음 정보를 바탕으로, 독자의 눈길을 사로잡고 글에 몰입하게 만드는 **'완전히 새로운'** 블로그 포스트를 작성해주세요.

    ### 최종 포스트의 주제
    "{enhanced_title}"

    ### 참고 자료 (아이디어 및 정보 수집용)
    """
    for i, content in enumerate(crawled_contents):
        if content:
            prompt += f"\n--- 참고 자료 {i+1} (내용을 절대로 복사하지 마세요) ---\n{content}\n"
            
    prompt += f"""
    ### 작성 지침 (★★매우 중요★★)
    1.  **독창성 및 저작권 준수:** '참고 자료'는 아이디어와 정보 수집용으로만 사용하세요. **내용을 절대로 그대로 복사하거나 짜깁기하면 안 됩니다.** 참고 자료의 문장, 문단 구조를 모방하지 말고, 완전히 새로운 표현과 문장으로 독창적인 글을 창작해야 합니다. **이는 저작권 위반을 방지하기 위한 가장 중요한 규칙입니다.**
    2.  **구조:** 글의 구조는 서론, 본론(2~3개의 소주제), 결론으로 명확하게 구성해주세요.
    3.  **어조:** 독자들이 이해하기 쉽고 친근한 어조로 작성해주세요.
    4.  **추천인 ID:** 글의 마지막에는 자연스럽게 아래 '추천인 ID'를 언급하며 가입이나 사용을 유도하는 문장을 추가해주세요. (만약 ID가 '없음'이 아니라면) **언급 시에는 반드시 `**`를 사용해 굵게 표시해주세요.** (예: 추천인 코드는 **{referral_id if referral_id else 'ABCD123'}** 입니다.)
    5.  **서식:** 중요한 소제목들은 `##` 또는 `###` 마크다운 형식으로 작성해주세요.
    6.  **가독성 및 강조:** 글의 핵심 키워드나 독자가 꼭 알아야 할 중요한 정보는 `**`를 사용해 **굵게** 처리해주세요. 장점이나 특징을 나열할 때는 `-` 또는 `*`를 사용해 목록으로 만들어 가독성을 높여주세요.

    ### 포함할 정보
    - 추천인 ID: "{referral_id if referral_id and referral_id != '없음' else '없음'}"

    위 지침, 특히 **독창성과 가독성 향상을 위한 서식 적용 항목을 반드시 지켜서**, 완성된 형태의 블로그 포스트를 작성해주세요.
    """
    return prompt

def main():
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        print("❌ 'API_KEY'를 .env 파일에서 찾을 수 없습니다.")
        return
        
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        NAVER_USERNAME = config['naver_id']
        NAVER_PASSWORD = config['naver_pw']
        post_info = config['post_info']
    except Exception as e:
        print(f"❌ 'data.json' 파일을 읽는 데 실패했습니다. 웹 UI에서 먼저 데이터를 저장해주세요. 오류: {e}")
        return

    image_dir = "images"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"'{image_dir}' 폴더를 생성했습니다.")

    print("🚀 1단계: 샘플 URL 내용 분석 및 이미지 다운로드 시작")
    crawled_contents = []
    all_downloaded_images = [] 
    if not post_info.get('sample_urls'):
        print("   - 경고: 분석할 샘플 URL이 없습니다. 제목만으로 글을 생성합니다.")
    else:
        for url in post_info['sample_urls']:
            print(f"   - 처리 중: {url[:70]}...")
            
            if "play.google.com/store/apps" in url:
                image_paths = download_play_store_images(url, save_dir=image_dir)
                all_downloaded_images.extend(image_paths)
            
            content = crawl_url_content(url)
            crawled_contents.append(content)

    print("\n🚀 2단계: 크롤링한 내용을 바탕으로 Gemini API 콘텐츠 생성")
    title = post_info['title']
    referral_id = post_info.get('referral_id', '')
    
    advanced_prompt = create_advanced_prompt(title, referral_id, crawled_contents)
    gemini_api = GeminiAPI(API_KEY)
    response = gemini_api.generate_content(advanced_prompt)
    final_content = gemini_api.extract_text(response)

    if "❌" in final_content:
        print(f"콘텐츠 생성에 실패했습니다: {final_content}")
        return
        
    print("✅ 응용 콘텐츠 생성 완료!")
    
    final_post_title = f"**{title}**"
    if referral_id and referral_id.strip() and referral_id != '없음':
        final_post_title = f"**{title} (추천인 코드: {referral_id})**"
    
    poster = NaverAutoPoster()
    try:
        if poster.login(NAVER_USERNAME, NAVER_PASSWORD):
            print("\n🚀 3단계: 네이버 블로그 자동 포스팅 시작")
            if not poster.post(final_post_title, final_content, image_paths=all_downloaded_images):
                print("   - 포스팅에 실패하여 프로그램을 종료합니다.")
                return
    finally:
        poster.close()
        print("\n🎉 모든 자동화 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()