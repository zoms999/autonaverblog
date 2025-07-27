import requests
import json
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pyperclip

# ==============================================================================
# PART 1: CONTENT CREATION CLASSES
# ==============================================================================

class GeminiAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"
        
    def generate_content(self, prompt, max_tokens=150, temperature=0.6):
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
        except requests.exceptions.RequestException as e:
            print(f"❌ Gemini API 요청 오류: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return None
    
    def extract_text(self, response):
        if not response:
            return "❌ API 응답 없음"
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError, TypeError):
            return "❌ 응답에서 텍스트를 추출할 수 없습니다."

class ReferralContentGenerator:
    def __init__(self, api_key):
        self.gemini = GeminiAPI(api_key)
        
    def create_promo_prompt(self, title, referral_id):
        prompt = f"""
        다음 정보를 바탕으로, 블로그 포스팅에 사용할 간결하고 매력적인 앱 소개 및 추천인 홍보 문구를 생성해줘.
        - 앱 이름 / 주제: "{title}"
        """
        if referral_id and pd.notna(referral_id) and str(referral_id).strip():
            prompt += f'- 추천인 ID: "{referral_id}"\n'
        prompt += """
        [요청사항]
        1. 앱의 핵심 기능을 한두 문장으로 요약해서 소개해줘.
        2. 만약 추천인 ID가 제공되었다면, 가입 시 해당 ID를 입력하면 혜택이 있다는 점을 강조하며 가입을 유도하는 문구를 포함해줘.
        3. 전체 내용은 1~2개의 문장으로 매우 간결하고 명확하게 작성해줘.
        4. 최종 결과물은 완성된 한글 문장만 제공하고, 다른 설명은 절대 추가하지 마.
        [생성 예시]
        - 입력 정보: 앱 이름="패널파워", 추천인 ID="partybucket"
        - 완벽한 출력: 틈틈이 설문조사하고 용돈 버는 앱테크, 패널파워! 가입 시 추천인 partybucket 입력하고 추가 혜택 받아가세요.
        """
        return prompt
    
    def generate_promo_content(self, title, referral_id):
        prompt = self.create_promo_prompt(title, referral_id)
        response = self.gemini.generate_content(prompt)
        content = self.gemini.extract_text(response)
        return content.strip().replace('"', '')

def create_content_excel(excel_file_path, api_key):
    print("🚀 1단계: 앱 소개 및 추천인 홍보 문구 생성 시작")
    print("=" * 60)
    excel_path = Path(excel_file_path)
    if not excel_path.exists():
        print(f"❌ 원본 파일을 찾을 수 없습니다: {excel_file_path}")
        return None
    
    try:
        df = pd.read_excel(excel_path, header=0)
        expected_cols = ['제목', 'URL1', 'URL2', 'referral_id', '내용']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        df['내용'] = df['내용'].astype('object')
        
        generator = ReferralContentGenerator(api_key)
        
        for idx, row in df.iterrows():
            title = row.get('제목')
            if pd.isna(title) or str(title).strip() == "":
                continue
            
            referral_id = row.get('referral_id')
            
            print(f"🔄 내용 생성 중 ({idx + 1}/{len(df)}): {title}")
            promo_content = generator.generate_promo_content(str(title), referral_id)
            df.at[idx, '내용'] = promo_content
            time.sleep(2) # API 과부하 방지

        output_file = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"✅ 내용 생성이 완료되었습니다!")
        print(f"📁 결과 파일: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ 내용 생성 중 오류 발생: {e}")
        return None

# ==============================================================================
# PART 2: NAVER BLOG AUTOMATION CLASS
# ==============================================================================

class NaverAutoPoster:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        try:
            print("\n🚀 2단계: 네이버 로그인 시작")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            time.sleep(2)
            id_input = self.wait.until(EC.element_to_be_clickable((By.ID, "id")))
            pyperclip.copy(username)
            id_input.send_keys(Keys.CONTROL, "v")
            time.sleep(1)
            pw_input = self.driver.find_element(By.ID, "pw")
            pyperclip.copy(password)
            pw_input.send_keys(Keys.CONTROL, "v")
            time.sleep(1)
            self.driver.find_element(By.ID, "log.login").click()
            WebDriverWait(self.driver, 10).until(lambda d: "nidlogin" not in d.current_url)
            print("✅ 로그인 성공!")
            return True
        except Exception as e:
            print(f"❌ 로그인 실패 또는 추가 인증 필요. 오류: {e}")
            return False
    
    def post(self, title, content):
        try:
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame")))
            time.sleep(2)

            try:
                cancel_button = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-popup-button-cancel")))
                cancel_button.click()
            except:
                pass

            title_area = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-title-placeholder, .se-title-text")))
            title_area.click()
            time.sleep(0.5)
            pyperclip.copy(title)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(1)

            content_area = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-main-container")))
            content_area.click()
            time.sleep(0.5)
            pyperclip.copy(content)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            self.driver.switch_to.default_content()
            publish_button = self.wait.until(EC.element_to_be_clickable((By.ID, "publish_top_btn")))
            publish_button.click()
            
            final_publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_apply[type='button']")))
            final_publish_button.click()

            WebDriverWait(self.driver, 20).until(EC.url_contains("PostView.naver"))
            print(f"✅ 포스팅 완료: {title}")
            return True
        except Exception as e:
            screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ 포스팅 중 오류 발생! 스크린샷 저장: {screenshot_path}")
            print(f"   오류 상세: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
            print("\n브라우저가 종료되었습니다.")

# ==============================================================================
# PART 3: MAIN ORCHESTRATION LOGIC
# ==============================================================================

def main():
    # ----------------- 설정 -----------------
    # Gemini API 키
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo"
    # 네이버 계정 정보
    NAVER_USERNAME = "alocurl"
    NAVER_PASSWORD = "Winker8893!"
    # 원본 데이터 엑셀 파일
    INPUT_EXCEL_FILE = "data.xlsx"
    # ----------------------------------------

    # 1단계: Gemini API로 내용 생성 후 엑셀 파일로 저장
    output_excel_path = create_content_excel(INPUT_EXCEL_FILE, API_KEY)
    
    if not output_excel_path:
        print("내용 생성에 실패하여 프로그램을 종료합니다.")
        return

    # 2단계: 생성된 엑셀 파일 읽기
    try:
        df = pd.read_excel(output_excel_path)
    except Exception as e:
        print(f"생성된 엑셀 파일({output_excel_path})을 읽는 중 오류 발생: {e}")
        return

    # 3단계: 네이버 로그인 및 자동 포스팅
    poster = NaverAutoPoster()
    try:
        if poster.login(NAVER_USERNAME, NAVER_PASSWORD):
            print("\n🚀 3단계: 네이버 블로그 자동 포스팅 시작")
            print("=" * 60)
            
            for idx, row in df.iterrows():
                title = row.get('제목')
                content = row.get('내용')

                if pd.isna(title) or pd.isna(content) or "❌" in str(content):
                    print(f"⏭️  ({idx + 1}/{len(df)}) 포스팅 건너뛰기 (제목 또는 내용에 문제 있음)")
                    continue

                print(f"\n- ({idx + 1}/{len(df)}) 포스팅 작업 시작: {title}")
                
                if poster.post(str(title), str(content)):
                    print("... 15초 대기 후 다음 포스트를 진행합니다 ...")
                    time.sleep(15)
                else:
                    print("이번 포스팅에 실패했습니다. 5초 후 다음 포스트로 넘어갑니다.")
                    time.sleep(5)
            
            print("\n🎉 모든 포스팅 작업이 완료되었습니다!")

    except Exception as e:
        print(f"자동 포스팅 중 예상치 못한 오류 발생: {e}")
    finally:
        poster.close()

if __name__ == "__main__":
    main()