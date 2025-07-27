import requests
import json
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

class GeminiAPI:
    def __init__(self, api_key):
        """
        Gemini API 클래스 초기화
        
        Args:
            api_key (str): Gemini API 키
        """
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-2.0-flash"
        
    def generate_content(self, prompt, max_tokens=None, temperature=None):
        """
        Gemini API를 사용하여 콘텐츠 생성
        
        Args:
            prompt (str): 입력 프롬프트
            max_tokens (int): 최대 토큰 수 (선택적)
            temperature (float): 창의성 수준 0.0-1.0 (선택적)
            
        Returns:
            dict: API 응답 결과
        """
        url = f"{self.base_url}/{self.model}:generateContent"
        headers = {'Content-Type': 'application/json'}
        params = {'key': self.api_key}
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        generation_config = {}
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
        if temperature is not None:
            generation_config["temperature"] = temperature
        if generation_config:
            payload["generationConfig"] = generation_config
        
        try:
            response = requests.post(url, headers=headers, params=params, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 오류: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return None
    
    def extract_text(self, response):
        """
        API 응답에서 생성된 텍스트 추출
        
        Args:
            response (dict): API 응답 결과
            
        Returns:
            str: 생성된 텍스트
        """
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError, TypeError):
            return "응답에서 텍스트를 추출할 수 없습니다."

class ReferralContentGenerator:
    def __init__(self, api_key):
        """
        추천인 홍보 콘텐츠 생성기 초기화
        """
        self.gemini = GeminiAPI(api_key)
        
    def create_promo_prompt(self, title, url2, referral_id):
        """
        앱 소개 및 추천인 홍보를 위한 프롬프트 생성
        """
        prompt = f"""
        다음 정보를 바탕으로, 엑셀의 '내용' 컬럼에 들어갈 간결하고 매력적인 앱 소개 및 추천인 홍보 문구를 생성해줘.

        - 앱 이름 / 주제: "{title}"
        - 앱 다운로드 URL (참고용): "{url2}"
        """
        
        # referral_id가 있는 경우에만 프롬프트에 추가
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
    
    def generate_promo_content(self, title, url2, referral_id):
        """
        앱 소개 및 추천인 홍보 콘텐츠 생성
        """
        prompt = self.create_promo_prompt(title, url2, referral_id)
        response = self.gemini.generate_content(prompt, max_tokens=150, temperature=0.6)
        
        if response:
            content = self.gemini.extract_text(response)
            return content.strip().replace('"', '') # 불필요한 따옴표 제거
        else:
            return "❌ 콘텐츠 생성 실패"

def process_excel_file(excel_file_path, api_key):
    """
    엑셀 파일을 처리하여 '내용' 컬럼에 홍보 문구 생성
    """
    print("🚀 앱 소개 및 추천인 홍보 문구 자동 생성 프로그램")
    print("=" * 60)
    
    excel_path = Path(excel_file_path)
    if not excel_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {excel_file_path}")
        return
    
    try:
        print(f"📖 엑셀 파일 읽는 중: {excel_file_path}")
        df = pd.read_excel(excel_path, header=0)
        
        # 필요한 컬럼 확인 및 추가
        expected_cols = ['제목', 'URL1', 'URL2', 'referral_id', '내용']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None
        
        # '내용' 컬럼의 데이터 타입을 object로 설정하여 문자열 저장이 가능하도록 함
        df['내용'] = df['내용'].astype('object')
        
        generator = ReferralContentGenerator(api_key)
        
        total_rows = len(df)
        if total_rows == 0:
            print("❌ 처리할 데이터가 없습니다.")
            return
            
        print(f"📊 총 {total_rows}개의 데이터를 처리합니다.")
        print("-" * 60)
        
        for idx, row in df.iterrows():
            title = row.get('제목')
            
            if pd.isna(title) or str(title).strip() == "":
                print(f"⏭️  {idx + 2}행: '제목'이 비어있어 건너뜁니다.")
                continue
            
            # referral_id 컬럼에서 직접 값을 가져옴
            url2 = row.get('URL2')
            referral_id = row.get('referral_id')
            
            print(f"🔄 처리 중 ({idx + 1}/{total_rows}): {title} (추천인: {referral_id if pd.notna(referral_id) else '없음'})")
            
            try:
                # referral_id를 직접 전달하여 콘텐츠 생성
                promo_content = generator.generate_promo_content(str(title), url2, referral_id)
                df.at[idx, '내용'] = promo_content
                print(f"✅ 완료: {promo_content[:50]}...")
                
                time.sleep(1)
                
            except Exception as e:
                error_msg = f"오류 발생: {e}"
                df.at[idx, '내용'] = error_msg
                print(f"❌ 실패: {error_msg}")
            
            print("-" * 40)
        
        # 결과 파일 저장
        output_file = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        print(f"\n💾 결과를 {output_file} 파일로 저장 중...")
        
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"✅ 모든 처리가 완료되었습니다!")
        print(f"📁 결과 파일: {output_file}")
        
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류 발생: {e}")

def main():
    """
    메인 실행 함수
    """
    # ----------------- 설정 -----------------
    # 사용자의 Gemini API 키를 입력하세요.
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo" # 여기에 실제 Gemini API 키를 입력하세요.
    
    # 처리할 엑셀 파일의 이름을 지정하세요.
    excel_file = "data.xlsx"
    # ----------------------------------------
    
    if API_KEY == "YOUR_GEMINI_API_KEY":
        print("⚠️  API 키를 설정해주세요. 코드의 'YOUR_GEMINI_API_KEY' 부분을 실제 키로 변경해야 합니다.")
        return

    try:
        process_excel_file(excel_file, API_KEY)
    except KeyboardInterrupt:
        print("\n\n⏹️ 프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")

if __name__ == "__main__":
    main()