from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pyperclip
import time

class NaverLogin:
    def __init__(self):
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # WebDriver 초기화
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # 자동화 탐지 방지를 위한 스크립트 실행
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self, username, password):
        """
        네이버 로그인을 수행합니다.
        """
        try:
            print("네이버 로그인 페이지로 이동 중...")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            
            # 페이지 로딩 대기
            time.sleep(2)
            
            # 아이디 입력 필드 찾기 및 클릭
            print("아이디 입력 필드 클릭...")
            id_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "id"))
            )
            id_input.click()
            
            # 클립보드에 아이디 복사 후 붙여넣기
            print("아이디 입력 중...")
            pyperclip.copy(username)
            time.sleep(0.5)
            id_input.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # 비밀번호 입력 필드 찾기 및 클릭
            print("비밀번호 입력 필드 클릭...")
            pw_input = self.driver.find_element(By.ID, "pw")
            pw_input.click()
            
            # 클립보드에 비밀번호 복사 후 붙여넣기
            print("비밀번호 입력 중...")
            pyperclip.copy(password)
            time.sleep(0.5)
            pw_input.send_keys(Keys.CONTROL + "v")
            time.sleep(1)
            
            # 로그인 버튼 클릭
            print("로그인 버튼 클릭...")
            login_btn = self.driver.find_element(By.ID, "log.login")
            login_btn.click()
            
            # 로그인 처리 대기
            print("로그인 처리 중...")
            time.sleep(2)
            
            # 로그인 성공 여부 확인
            current_url = self.driver.current_url
            if "naver.com" in current_url and "nidlogin" not in current_url:
                print("로그인 성공!")
                return True
            else:
                print("로그인 실패 또는 추가 인증 필요")
                return False
                
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            return False
    
    def go_to_blog_write(self):
        """
        블로그 작성 페이지로 이동합니다.
        """
        try:
            print("블로그 작성 페이지로 이동 중...")
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            time.sleep(3)
            print("블로그 작성 페이지 이동 완료!")
            return True
        except Exception as e:
            print(f"블로그 페이지 이동 중 오류 발생: {e}")
            return False
    
    def write_blog_post(self, title="제목 테스트", content="안녕하세요 내용을 입력하고 있습니다\n안녕하세요 내용을 입력하고 있습니다\n안녕하세요 내용을 입력하고 있습니다\n안녕하세요 내용을 입력하고 있습니다\n안녕하세요 내용을 입력하고 있습니다"):
        """
        블로그 글을 작성합니다.
        """
        try:
            print("블로그 글 작성 시작...")
            
            # iframe으로 전환
            print("iframe으로 전환 중...")
            iframe = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame"))
            )
            self.driver.switch_to.frame(iframe)
            time.sleep(2)
            
            # 팝업 취소 버튼이 있으면 클릭
            try:
                cancel_button = self.driver.find_element(By.CSS_SELECTOR, ".se-popup-button-cancel")
                if cancel_button.is_displayed():
                    print("팝업 취소 버튼 클릭...")
                    cancel_button.click()
                    time.sleep(1)
            except:
                print("팝업 취소 버튼 없음 - 넘어감")
            
            # 도움말 패널 닫기 버튼이 있으면 클릭
            try:
                help_close_button = self.driver.find_element(By.CSS_SELECTOR, ".se-help-panel-close-button")
                if help_close_button.is_displayed():
                    print("도움말 패널 닫기 버튼 클릭...")
                    help_close_button.click()
                    time.sleep(1)
            except:
                print("도움말 패널 닫기 버튼 없음 - 넘어감")
            
            # 제목 입력 (여러 번 시도)
            print("제목 입력 중...")
            title_success = False
            
            for attempt in range(3):  # 3번 시도
                try:
                    print(f"제목 입력 시도 {attempt + 1}/3")
                    
                    # .se-section-documentTitle 클래스를 가진 요소 찾기
                    title_section = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-documentTitle"))
                    )
                    
                    # JavaScript로 직접 클릭하고 포커스 설정
                    self.driver.execute_script("arguments[0].click();", title_section)
                    time.sleep(0.5)
                    
                    # 제목 영역의 span.__se-node 요소 찾기
                    title_span = title_section.find_element(By.CSS_SELECTOR, "span.__se-node")
                    
                    # JavaScript로 직접 클릭하고 포커스 설정
                    self.driver.execute_script("arguments[0].click();", title_span)
                    self.driver.execute_script("arguments[0].focus();", title_span)
                    time.sleep(0.5)
                    
                    # 기존 내용 지우기
                    self.driver.execute_script("arguments[0].textContent = '';", title_span)
                    time.sleep(0.2)
                    
                    # ActionChains로 0.01초에 1글자씩 입력
                    actions = ActionChains(self.driver)
                    actions.click(title_span).perform()
                    time.sleep(0.1)
                    
                    # 한 글자씩 천천히 입력
                    for char in title:
                        actions = ActionChains(self.driver)
                        actions.send_keys(char).perform()
                        time.sleep(0.01)  # 0.01초 대기
                    
                    # 입력 완료 후 이벤트 발생
                    self.driver.execute_script("""
                        var events = ['input', 'change', 'keyup', 'blur'];
                        events.forEach(function(eventType) {
                            var event = new Event(eventType, { bubbles: true });
                            arguments[0].dispatchEvent(event);
                        });
                    """, title_span)
                    
                    time.sleep(1)
                    
                    # 입력 확인
                    current_text = title_span.get_attribute("textContent") or title_span.text
                    if title in current_text or len(current_text.strip()) > 0:
                        print(f"제목 입력 성공: {current_text}")
                        title_success = True
                        break
                    else:
                        print(f"제목 입력 확인 실패, 재시도...")
                        
                except Exception as e:
                    print(f"제목 입력 시도 {attempt + 1} 실패: {e}")
                    time.sleep(0.5)
            
            if not title_success:
                print("제목 입력 최종 실패")
            
            # 내용 입력 (여러 번 시도)
            print("내용 입력 중...")
            content_success = False
            
            for attempt in range(3):  # 3번 시도
                try:
                    print(f"내용 입력 시도 {attempt + 1}/3")
                    
                    # .se-section-text 클래스를 가진 요소 찾기
                    content_section = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-section-text"))
                    )
                    
                    # JavaScript로 직접 클릭하고 포커스 설정
                    self.driver.execute_script("arguments[0].click();", content_section)
                    time.sleep(0.5)
                    
                    # 내용 영역의 span.__se-node 요소 찾기
                    content_span = content_section.find_element(By.CSS_SELECTOR, "span.__se-node")
                    
                    # JavaScript로 직접 클릭하고 포커스 설정
                    self.driver.execute_script("arguments[0].click();", content_span)
                    self.driver.execute_script("arguments[0].focus();", content_span)
                    time.sleep(0.5)
                    
                    # 기존 내용 지우기
                    self.driver.execute_script("arguments[0].textContent = '';", content_span)
                    time.sleep(0.2)
                    
                    # ActionChains로 0.01초에 1글자씩 입력
                    actions = ActionChains(self.driver)
                    actions.click(content_span).perform()
                    time.sleep(0.1)
                    
                    # 5줄 내용을 한 글자씩 천천히 입력
                    content_lines = [
                        "안녕하세요 내용을 입력하고 있습니다",
                        "안녕하세요 내용을 입력하고 있습니다", 
                        "안녕하세요 내용을 입력하고 있습니다",
                        "안녕하세요 내용을 입력하고 있습니다",
                        "안녕하세요 내용을 입력하고 있습니다"
                    ]
                    
                    for i, line in enumerate(content_lines):
                        # 각 줄의 글자를 하나씩 입력
                        for char in line:
                            actions = ActionChains(self.driver)
                            actions.send_keys(char).perform()
                            time.sleep(0.01)  # 0.01초 대기
                        
                        # 마지막 줄이 아니면 Enter 키 입력
                        if i < len(content_lines) - 1:
                            actions = ActionChains(self.driver)
                            actions.send_keys(Keys.ENTER).perform()
                            time.sleep(0.05)  # 줄바꿈 후 약간 더 긴 대기
                    
                    # 입력 완료 후 이벤트 발생
                    self.driver.execute_script("""
                        var events = ['input', 'change', 'keyup', 'blur'];
                        events.forEach(function(eventType) {
                            var event = new Event(eventType, { bubbles: true });
                            arguments[0].dispatchEvent(event);
                        });
                    """, content_span)
                    
                    time.sleep(1)
                    
                    # 입력 확인
                    current_text = content_span.get_attribute("textContent") or content_span.text
                    if len(current_text.strip()) > 10:  # 충분한 내용이 입력되었는지 확인
                        print(f"내용 입력 성공 (5줄): {current_text[:50]}...")
                        content_success = True
                        break
                    else:
                        print(f"내용 입력 확인 실패, 재시도...")
                        
                except Exception as e:
                    print(f"내용 입력 시도 {attempt + 1} 실패: {e}")
                    time.sleep(0.5)
            
            if not content_success:
                print("내용 입력 최종 실패")
            
            # 제목과 내용 입력 완료 후 2초 대기
            print("제목과 내용 입력 완료, 2초 후 저장...")
            time.sleep(2)
            
            # 저장 버튼 클릭
            print("저장 버튼 찾는 중...")
            save_success = False
            
            # 여러 가지 저장 버튼 셀렉터 시도
            save_selectors = [
                ".save_btn__bzc5B",
                "button[class*='save_btn']",
                "button:contains('저장')",
                ".text__bK4MD",
                "button .text__bK4MD",
                "[class*='save']",
                "button[type='button']:contains('저장')"
            ]
            
            for selector in save_selectors:
                try:
                    print(f"저장 버튼 셀렉터 시도: {selector}")
                    
                    if ":contains" in selector:
                        # contains는 XPath로 처리
                        xpath_selector = f"//button[contains(text(), '저장')]"
                        save_button = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        save_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if save_button and save_button.is_displayed() and save_button.is_enabled():
                        print(f"저장 버튼 발견: {selector}")
                        
                        # JavaScript로 클릭 시도
                        self.driver.execute_script("arguments[0].click();", save_button)
                        print("저장 버튼 클릭 완료!")
                        save_success = True
                        time.sleep(2)
                        break
                        
                except Exception as e:
                    print(f"셀렉터 {selector} 실패: {e}")
                    continue
            
            # 모든 셀렉터가 실패한 경우 대안 방법
            if not save_success:
                print("일반적인 저장 버튼을 찾을 수 없음. 대안 방법 시도...")
                try:
                    # 모든 버튼 요소를 찾아서 텍스트가 '저장'인 것 찾기
                    all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in all_buttons:
                        button_text = button.get_attribute("textContent") or button.text
                        if "저장" in button_text:
                            print(f"저장 버튼 발견 (텍스트 기반): {button_text}")
                            self.driver.execute_script("arguments[0].click();", button)
                            save_success = True
                            time.sleep(2)
                            break
                            
                    # 여전히 실패한 경우 Ctrl+S 시도
                    if not save_success:
                        print("Ctrl+S로 저장 시도...")
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
                        time.sleep(2)
                        save_success = True
                        
                except Exception as e:
                    print(f"대안 저장 방법 실패: {e}")
            
            if save_success:
                print("블로그 글 저장 완료!")
            else:
                print("저장 버튼을 찾을 수 없습니다. 수동으로 저장해주세요.")
            
            print("블로그 글 작성 완료!")
            return True
            
        except Exception as e:
            print(f"블로그 글 작성 중 오류 발생: {e}")
            return False
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def close(self):
        """
        브라우저를 종료합니다.
        """
        if self.driver:
            self.driver.quit()
            print("브라우저가 종료되었습니다.")

def main():
    # 네이버 계정 정보
    USERNAME = ""
    PASSWORD = ""
    
    # NaverLogin 인스턴스 생성
    naver = NaverLogin()
    
    try:
        # 로그인 수행
        if naver.login(USERNAME, PASSWORD):
            # 로그인 성공 시 블로그 작성 페이지로 이동
            if naver.go_to_blog_write():
                # 블로그 글 작성
                naver.write_blog_post()
            
            # 잠시 대기 (작업을 위해)
            input("작업을 완료하려면 Enter를 누르세요...")
        else:
            print("로그인에 실패했습니다.")
            
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
    finally:
        # 브라우저 종료
        naver.close()

if __name__ == "__main__":
    main() 