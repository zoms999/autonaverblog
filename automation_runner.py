import requests
import json
import time
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
    def generate_content(self, prompt, max_tokens=1000, temperature=0.7):
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
        
        # 자동화 탐지 방지를 위한 스크립트 실행
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 20)
    def login(self, username, password):
        try:
            print("네이버 로그인 페이지로 이동 중...")
            self.driver.get("https://nid.naver.com/nidlogin.login")
            time.sleep(2)
            
            # 아이디 입력 필드 찾기 및 클릭
            print("아이디 입력 필드 클릭...")
            id_input = self.wait.until(EC.element_to_be_clickable((By.ID, "id")))
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
            time.sleep(3)
            
            # 로그인 성공 여부 확인
            current_url = self.driver.current_url
            if "naver.com" in current_url and "nidlogin" not in current_url:
                print("✅ 로그인 성공!")
                return True
            else:
                # 추가 대기 시간을 두고 다시 확인
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
    def post(self, title, content):
        try:
            print("블로그 작성 페이지로 이동 중...")
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            
            # iframe으로 전환
            print("iframe으로 전환 중...")
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame")))
            self.driver.switch_to.frame(iframe)
            time.sleep(2)
            
            # 팝업 및 도움말 패널 처리 (있을 경우)
            try:
                # 1초의 짧은 대기 시간으로 팝업을 찾고 없으면 바로 넘어갑니다.
                short_wait = WebDriverWait(self.driver, 1)
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
            try:
                title_element = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-title-text"))
                )
                pyperclip.copy(title)
                
                actions = ActionChains(self.driver)
                actions.click(title_element)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                actions.pause(0.5)
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
                actions.perform()
                
                time.sleep(2)

                # === ★★★ 제목 확인 로직 수정 ★★★ ===
                current_text = title_element.text
                
                # 비교를 위해 두 문자열에서 '**'를 제거하고 공백을 정규화합니다.
                expected_clean = " ".join(title.replace("**", "").split())
                current_clean = " ".join(current_text.replace("**", "").split())

                if expected_clean == current_clean:
                    print(f"✅ 제목 입력 성공: {current_text}")
                else:
                    # 디버깅을 위해 두 문자열을 모두 출력
                    print(f"--- 비교 실패 디버깅 ---")
                    print(f"  - 예상(정제 후): '{expected_clean}'")
                    print(f"  - 실제(정제 후): '{current_clean}'")
                    print(f"----------------------")
                    raise Exception(f"제목 입력 확인 실패. 현재 텍스트: '{current_text}'")

            except Exception as e:
                print(f"❌ 제목 입력/확인 중 오류 발생: {e}")
                raise # 오류 발생 시 포스팅 중단

            # === 내용 입력 로직 ===
            print("내용 입력 중...")
            try:
                # 내용 입력 필드는 플레이스홀더 텍스트를 포함한 첫 번째 텍스트 블록을 찾습니다.
                content_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".se-component.se-text.se-l-default"))
                )
                content_element.click()
                time.sleep(1)

                pyperclip.copy(content)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(3)
                print("✅ 내용 입력 성공.")
            except Exception as e:
                print(f"❌ 내용 입력 중 오류 발생: {e}")
                raise

            # iframe에서 빠져나오기
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # 발행(게시) 버튼 클릭
            print("발행 버튼 클릭 중...")
            publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='publish']")))
            publish_button.click()
            time.sleep(2)
            
            # 최종 발행 확인 버튼 클릭
            print("최종 발행 확인 버튼 클릭 중...")
            # '발행' 버튼이 있는 패널이 나타날 때까지 기다립니다.
            publish_panel = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class*='layer_popup']")))
            final_publish_button = publish_panel.find_element(By.CSS_SELECTOR, "button[class*='btn_apply']")
            final_publish_button.click()
            
            # 포스팅 완료 확인 (게시글 URL로 이동했는지 확인)
            WebDriverWait(self.driver, 20).until(EC.url_contains("PostView.naver"))
            print(f"✅ 포스팅 최종 완료: {title}")
            return True
            
        except Exception as e:
            screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ 포스팅 중 심각한 오류 발생! 스크린샷 저장: {screenshot_path}")
            print(f"   오류 상세 정보: {e}")
            return False
        try:
            print("블로그 작성 페이지로 이동 중...")
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            
            # iframe으로 전환
            print("iframe으로 전환 중...")
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame")))
            self.driver.switch_to.frame(iframe)
            time.sleep(2)
            
            # 팝업 및 도움말 패널 처리 (있을 경우)
            try:
                # 1초의 짧은 대기 시간으로 팝업을 찾고 없으면 바로 넘어갑니다.
                short_wait = WebDriverWait(self.driver, 1)
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

            # === ★★★ 제목 입력 로직 수정 ★★★ ===
            print("제목 입력 중...")
            try:
                # 1. 제목 입력란을 더 명확한 선택자(.se-title-text)로 찾고 클릭 대기
                title_element = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-title-text"))
                )
                
                # 2. 클립보드를 사용해 제목 복사 (특수문자 및 한글 깨짐 방지)
                pyperclip.copy(title)
                
                # 3. ActionChains를 사용해 실제 사용자처럼 클릭, 전체 선택(Ctrl+A), 붙여넣기(Ctrl+V) 실행
                # 이 방법이 JavaScript 이벤트를 가장 확실하게 발생시킵니다.
                actions = ActionChains(self.driver)
                actions.click(title_element)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL)
                actions.pause(0.5)
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL)
                actions.perform()
                
                time.sleep(2) # 에디터가 입력을 처리할 시간을 줌

                # 4. 입력 확인
                # 참고: title에 포함된 '**'는 서식이 아니라 문자 그대로 입력됩니다.
                current_text = title_element.text
                if title.replace("**", "") in current_text:
                    print(f"✅ 제목 입력 성공: {current_text}")
                else:
                    raise Exception(f"제목 입력 확인 실패. 현재 텍스트: '{current_text}'")
            except Exception as e:
                print(f"❌ 제목 입력 중 오류 발생: {e}")
                raise # 오류 발생 시 포스팅 중단

            # === 내용 입력 로직 (기존 코드와 유사하게 유지) ===
            print("내용 입력 중...")
            try:
                # 내용 입력 필드를 클릭하여 활성화
                content_element = self.driver.find_element(By.CSS_SELECTOR, ".se-component.se-text.se-l-default")
                content_element.click()
                time.sleep(1)

                # 클립보드로 내용 붙여넣기
                pyperclip.copy(content)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(3) # 내용이 길 수 있으므로 충분히 대기
                print("✅ 내용 입력 성공.")
            except Exception as e:
                print(f"❌ 내용 입력 중 오류 발생: {e}")
                raise # 오류 발생 시 포스팅 중단

            # iframe에서 빠져나오기
            self.driver.switch_to.default_content()
            time.sleep(1)
            
            # 발행(게시) 버튼 클릭
            print("발행 버튼 클릭 중...")
            publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='publish']")))
            publish_button.click()
            time.sleep(2)
            
            # 최종 발행 확인 버튼 클릭
            print("최종 발행 확인 버튼 클릭 중...")
            final_publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='btn_apply']")))
            final_publish_button.click()
            
            # 포스팅 완료 확인
            WebDriverWait(self.driver, 20).until(EC.url_contains("PostView.naver"))
            print(f"✅ 포스팅 최종 완료: {title}")
            return True
            
        except Exception as e:
            screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ 포스팅 중 심각한 오류 발생! 스크린샷 저장: {screenshot_path}")
            print(f"   오류 상세 정보: {e}")
            return False
        try:
            print("블로그 작성 페이지로 이동 중...")
            self.driver.get("https://blog.naver.com/GoBlogWrite.naver")
            time.sleep(3)
            
            # iframe으로 전환
            print("iframe으로 전환 중...")
            iframe = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainFrame")))
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
            
            # 제목 입력 - 제목 전용 셀렉터 사용
            print("제목 입력 중...")
            title_success = False
            
            # 제목 전용 셀렉터들 (documentTitle 포함)
            title_selectors = [
                ".se-section-documentTitle span.__se-node",
                ".se-section-documentTitle",
                "[data-module='title'] span.__se-node",
                "[data-module='title']"
            ]
            
            for attempt in range(len(title_selectors)):
                try:
                    selector = title_selectors[attempt]
                    print(f"제목 입력 시도 {attempt + 1}/{len(title_selectors)} - 셀렉터: {selector}")
                    
                    # 제목 요소 찾기
                    title_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if not title_elements:
                        print(f"제목 셀렉터 {selector} 요소를 찾을 수 없음")
                        continue
                    
                    title_element = title_elements[0]  # 첫 번째 요소 사용
                    
                    # 제목 영역인지 확인 (documentTitle 클래스가 있는지)
                    parent_classes = ""
                    try:
                        parent = title_element.find_element(By.XPATH, "..")
                        parent_classes = parent.get_attribute("class") or ""
                        if "documentTitle" not in parent_classes:
                            # 더 상위 요소 확인
                            grandparent = parent.find_element(By.XPATH, "..")
                            grandparent_classes = grandparent.get_attribute("class") or ""
                            if "documentTitle" not in grandparent_classes:
                                print(f"제목 영역이 아님: {parent_classes}")
                                continue
                    except:
                        pass
                    
                    print(f"제목 요소 선택됨: {title_element.tag_name}, 부모 클래스: {parent_classes}")
                    
                    # JavaScript로 직접 클릭하고 포커스 설정
                    self.driver.execute_script("arguments[0].click();", title_element)
                    self.driver.execute_script("arguments[0].focus();", title_element)
                    time.sleep(0.5)
                    
                    # 기존 내용 지우기
                    self.driver.execute_script("arguments[0].textContent = '';", title_element)
                    time.sleep(0.3)
                    
                    # 제목 입력 (짧은 텍스트이므로 직접 입력)
                    try:
                        # JavaScript로 안전하게 제목 설정
                        self.driver.execute_script("arguments[0].textContent = arguments[1];", title_element, title)
                        time.sleep(0.5)
                        
                        # 이벤트 발생시키기
                        self.driver.execute_script("""
                            var events = ['input', 'change', 'keyup'];
                            events.forEach(function(eventType) {
                                var event = new Event(eventType, { bubbles: true });
                                arguments[0].dispatchEvent(event);
                            });
                        """, title_element)
                        
                    except Exception as e:
                        print(f"JavaScript 제목 입력 실패: {e}")
                        # 대안: 클립보드 사용
                        pyperclip.copy(title)
                        ActionChains(self.driver).click(title_element).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                        time.sleep(0.2)
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                    
                    time.sleep(1)
                    
                    # 입력 확인
                    current_text = title_element.get_attribute("textContent") or title_element.text or ""
                    if title in current_text or (len(current_text.strip()) > 0 and len(current_text.strip()) < 200):  # 제목은 보통 200자 미만
                        print(f"✅ 제목 입력 성공: {current_text}")
                        title_success = True
                        break
                    else:
                        print(f"제목 입력 확인 실패, 현재 텍스트: '{current_text[:50]}...'")
                        
                except Exception as e:
                    print(f"제목 입력 시도 {attempt + 1} 실패: {e}")
                    time.sleep(0.5)
            
            if not title_success:
                print("❌ 제목 입력 최종 실패")
            
            # 제목 입력 완료 후 잠시 대기
            time.sleep(2)
            
            # 내용 입력 - 더 간단하고 직접적인 방법 사용
            print("내용 입력 중...")
            content_success = False
            
            # 방법 1: Tab 키로 내용 영역 이동
            try:
                print("Tab 키로 내용 영역 이동 시도...")
                # Tab 키를 눌러서 다음 입력 영역으로 이동
                ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(1)
                
                # 현재 포커스된 요소에 내용 입력
                pyperclip.copy(content)
                ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(3)
                
                # 입력 확인 - 모든 텍스트 요소 검사
                all_elements = self.driver.find_elements(By.CSS_SELECTOR, "span.__se-node")
                content_found = False
                for element in all_elements:
                    element_text = element.get_attribute("textContent") or element.text or ""
                    # 내용의 일부가 포함되어 있는지 확인 (제목이 아닌)
                    if len(element_text.strip()) > 100 and title.replace("**", "") not in element_text:
                        print(f"✅ Tab 방법으로 내용 입력 성공: {element_text[:50]}...")
                        content_success = True
                        content_found = True
                        break
                
                if not content_found:
                    print("Tab 방법 실패 - 내용이 제대로 입력되지 않음")
                    
            except Exception as e:
                print(f"Tab 방법 실패: {e}")
            
            # 방법 2: 직접 내용 영역 찾아서 입력
            if not content_success:
                try:
                    print("직접 내용 영역 찾기 시도...")
                    
                    # 모든 span.__se-node 요소 찾기
                    all_spans = self.driver.find_elements(By.CSS_SELECTOR, "span.__se-node")
                    print(f"총 {len(all_spans)}개의 span.__se-node 요소 발견")
                    
                    # 제목이 아닌 빈 span 찾기
                    target_span = None
                    for i, span in enumerate(all_spans):
                        try:
                            if not span.is_displayed():
                                continue
                                
                            span_text = span.get_attribute("textContent") or span.text or ""
                            print(f"span {i+1}: '{span_text[:30]}...'")
                            
                            # 제목이 들어있는 span은 제외
                            if title.replace("**", "") in span_text:
                                print(f"  -> 제목이 포함된 span이므로 제외")
                                continue
                            
                            # 빈 span이거나 placeholder가 있는 span 선택
                            if (len(span_text.strip()) == 0 or 
                                "기록해보세요" in span_text or 
                                "최근 다녀온" in span_text or
                                "placeholder" in span.get_attribute("class") or ""):
                                target_span = span
                                print(f"  -> 내용 입력 대상으로 선택")
                                break
                                
                        except Exception as e:
                            print(f"span {i+1} 검사 중 오류: {e}")
                            continue
                    
                    if target_span:
                        print("내용 입력 대상 span 발견, 입력 시작...")
                        
                        # 해당 span에 포커스하고 내용 입력
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", target_span)
                        time.sleep(0.5)
                        self.driver.execute_script("arguments[0].click();", target_span)
                        self.driver.execute_script("arguments[0].focus();", target_span)
                        time.sleep(1)
                        
                        # 기존 내용 지우기
                        self.driver.execute_script("arguments[0].textContent = '';", target_span)
                        time.sleep(0.5)
                        
                        # 내용 입력
                        pyperclip.copy(content)
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                        time.sleep(3)
                        
                        # 입력 확인
                        new_text = target_span.get_attribute("textContent") or target_span.text or ""
                        if len(new_text.strip()) > 50:
                            print(f"✅ 직접 방법으로 내용 입력 성공: {new_text[:50]}...")
                            content_success = True
                        else:
                            print(f"직접 방법 실패 - 입력된 텍스트: '{new_text[:30]}...'")
                    else:
                        print("적절한 내용 입력 span을 찾을 수 없음")
                        
                except Exception as e:
                    print(f"직접 방법 실패: {e}")
            
            # 방법 3: 강제로 새 텍스트 블록 생성
            if not content_success:
                try:
                    print("강제로 새 텍스트 블록 생성 시도...")
                    
                    # 에디터 메인 컨테이너 클릭
                    main_container = self.driver.find_element(By.CSS_SELECTOR, ".se-main-container")
                    self.driver.execute_script("arguments[0].click();", main_container)
                    time.sleep(1)
                    
                    # 여러 번 Enter를 눌러서 새 블록 생성
                    for _ in range(3):
                        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                        time.sleep(0.5)
                    
                    # 내용 입력
                    pyperclip.copy(content)
                    ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                    time.sleep(3)
                    
                    # 입력 확인
                    all_spans = self.driver.find_elements(By.CSS_SELECTOR, "span.__se-node")
                    for span in all_spans:
                        span_text = span.get_attribute("textContent") or span.text or ""
                        if len(span_text.strip()) > 100 and title.replace("**", "") not in span_text:
                            print(f"✅ 강제 생성 방법으로 내용 입력 성공: {span_text[:50]}...")
                            content_success = True
                            break
                            
                except Exception as e:
                    print(f"강제 생성 방법 실패: {e}")
            
            if not content_success:
                print("❌ 내용 입력 최종 실패 - 모든 방법 시도했으나 실패")
                # 디버깅을 위해 현재 모든 span 내용 출력
                try:
                    all_spans = self.driver.find_elements(By.CSS_SELECTOR, "span.__se-node")
                    print("현재 페이지의 모든 span.__se-node 내용:")
                    for i, span in enumerate(all_spans):
                        span_text = span.get_attribute("textContent") or span.text or ""
                        print(f"  span {i+1}: '{span_text[:50]}...'")
                except:
                    pass
            
            # iframe에서 나오기
            self.driver.switch_to.default_content()
            time.sleep(2)
            
            # 저장 버튼 클릭 (HTML 분석 결과에 따른 새로운 셀렉터)
            print("저장 버튼 클릭 중...")
            save_success = False
            
            # 저장 버튼 셀렉터들
            save_selectors = [
                ".save_btn__bzc5B",
                "button.save_btn__bzc5B",
                ".save_btn_area__Qo0W7 button",
                "button:contains('저장')",
                ".text__bK4MD"
            ]
            
            for selector in save_selectors:
                try:
                    if ":contains" in selector:
                        # XPath로 처리
                        save_button = self.driver.find_element(By.XPATH, "//button[contains(., '저장')]")
                    else:
                        save_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if save_button and save_button.is_displayed():
                        print(f"저장 버튼 발견: {selector}")
                        self.driver.execute_script("arguments[0].click();", save_button)
                        save_success = True
                        time.sleep(3)
                        break
                        
                except Exception as e:
                    print(f"저장 버튼 셀렉터 {selector} 실패: {e}")
                    continue
            
            if save_success:
                print("✅ 저장 완료!")
                return True
            else:
                print("❌ 저장 버튼을 찾을 수 없어 발행 시도...")
                
                # 저장이 실패하면 발행 시도
                try:
                    publish_button = self.wait.until(EC.element_to_be_clickable((By.ID, "publish_top_btn")))
                    publish_button.click()
                    time.sleep(2)
                    
                    final_publish_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_apply[type='button']")))
                    final_publish_button.click()
                    
                    WebDriverWait(self.driver, 20).until(EC.url_contains("PostView.naver"))
                    print(f"✅ 포스팅 최종 완료: {title}")
                    return True
                except Exception as e:
                    print(f"발행도 실패: {e}")
                    return False
            
        except Exception as e:
            screenshot_path = f"error_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ 포스팅 중 오류! 스크린샷 저장: {screenshot_path}")
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
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator='\n', strip=True)
        return text[:1500]
    except Exception as e:
        print(f"   - URL 크롤링 실패: {url}, 오류: {e}")
        return ""

def create_advanced_prompt(title, referral_id, crawled_contents):
    # 제목에 추천인 코드 포함 (있는 경우)
    enhanced_title = title
    if referral_id and referral_id != '없음':
        enhanced_title = f"{title} (추천인: {referral_id})"
    
    prompt = f"""
    당신은 전문 블로그 작가입니다. 다음 정보를 바탕으로 독자에게 유용하고 흥미로운 블로그 포스트를 작성해주세요.

    ### 최종 포스트의 주제
    "{enhanced_title}"

    ### 참고 자료 (아래 웹사이트들에서 크롤링한 내용)
    """
    for i, content in enumerate(crawled_contents):
        if content:
            prompt += f"\n--- 참고 자료 {i+1} ---\n{content}\n"
    prompt += f"""
    ### 작성 지침
    1.  위 '참고 자료'들의 핵심 내용을 분석하고 종합하여 완전히 새로운 글을 작성해주세요. 내용을 그대로 복사하지 마세요.
    2.  글의 구조는 서론, 본론(2~3개의 소주제), 결론으로 구성해주세요.
    3.  독자들이 이해하기 쉽고 친근한 어조로 작성해주세요.
    4.  글의 마지막에는 자연스럽게 아래 '추천인 ID'를 언급하며 가입이나 사용을 유도하는 문장을 추가해주세요. (만약 ID가 있다면)
    5.  중요한 소제목들은 ## 또는 ### 마크다운 형식으로 작성해주세요.

    ### 포함할 정보
    - 추천인 ID: "{referral_id if referral_id else '없음'}"

    위 지침에 따라, 완성된 형태의 블로그 포스트를 작성해주세요.
    """
    return prompt

def main():
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo"
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        NAVER_USERNAME = config['naver_id']
        NAVER_PASSWORD = config['naver_pw']
        post_info = config['post_info']
    except Exception as e:
        print(f"❌ 'data.json' 파일을 읽는 데 실패했습니다. 웹 UI에서 먼저 데이터를 저장해주세요. 오류: {e}")
        return
    print("🚀 1단계: 샘플 URL 내용 분석 시작")
    crawled_contents = []
    for url in post_info['sample_urls']:
        print(f"   - 크롤링 중: {url[:50]}...")
        content = crawl_url_content(url)
        crawled_contents.append(content)
    print("\n🚀 2단계: 크롤링한 내용을 바탕으로 Gemini API 콘텐츠 생성")
    title = post_info['title']
    referral_id = post_info.get('referral_id', '')
    
    # 제목을 굵게 처리하고 추천인 코드 포함
    enhanced_title = title
    if referral_id and referral_id != '없음':
        enhanced_title = f"**{title}** (추천인: {referral_id})"
    else:
        enhanced_title = f"**{title}**"
    
    advanced_prompt = create_advanced_prompt(title, referral_id, crawled_contents)
    gemini_api = GeminiAPI(API_KEY)
    response = gemini_api.generate_content(advanced_prompt)
    final_content = gemini_api.extract_text(response)
    if "❌" in final_content:
        print(f"콘텐츠 생성에 실패했습니다: {final_content}")
        return
    print("✅ 응용 콘텐츠 생성 완료!")
    poster = NaverAutoPoster()
    try:
        if poster.login(NAVER_USERNAME, NAVER_PASSWORD):
            print("\n🚀 3단계: 네이버 블로그 자동 포스팅 시작")
            poster.post(enhanced_title, final_content)
    finally:
        poster.close()
        print("\n🎉 모든 자동화 작업이 완료되었습니다!")

if __name__ == "__main__":
    main() 