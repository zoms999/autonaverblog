import requests
import json

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
        
        # API 엔드포인트 URL 구성
        url = f"{self.base_url}/{self.model}:generateContent"
        
        # 헤더 설정
        headers = {
            'Content-Type': 'application/json'
        }
        
        # 요청 파라미터에 API 키 추가
        params = {
            'key': self.api_key
        }
        
        # 요청 본문 구성
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # 선택적 매개변수 추가
        generation_config = {}
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
        if temperature is not None:
            generation_config["temperature"] = temperature
            
        if generation_config:
            payload["generationConfig"] = generation_config
        
        try:
            # API 요청 전송
            response = requests.post(
                url, 
                headers=headers, 
                params=params, 
                data=json.dumps(payload)
            )
            
            # 응답 상태 확인
            response.raise_for_status()
            
            # JSON 응답 파싱
            result = response.json()
            return result
            
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
            if response and 'candidates' in response:
                candidate = response['candidates'][0]
                if 'content' in candidate:
                    parts = candidate['content']['parts']
                    if parts and 'text' in parts[0]:
                        return parts[0]['text']
            return "응답에서 텍스트를 추출할 수 없습니다."
        except (KeyError, IndexError) as e:
            print(f"❌ 텍스트 추출 오류: {e}")
            return "텍스트 추출 실패"

def test_basic_functionality():
    """
    기본 기능 테스트
    """
    print("🤖 Gemini API 기본 기능 테스트")
    print("=" * 50)
    
    # API 키 설정
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo"
    
    # Gemini API 인스턴스 생성
    gemini = GeminiAPI(API_KEY)
    
    # 테스트 프롬프트
    test_prompts = [
        "Explain how AI works in a few words",
        "Write a short poem about coding",
        "List 3 benefits of using Python programming language"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🔍 테스트 {i}: {prompt}")
        print("-" * 30)
        
        # API 호출
        response = gemini.generate_content(prompt)
        
        if response:
            # 응답 출력
            generated_text = gemini.extract_text(response)
            print(f"✅ 응답: {generated_text}")
            
            # 원시 응답도 출력 (디버깅용)
            print(f"\n📄 전체 응답:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print("❌ API 호출 실패")
        
        print("\n" + "="*50)

def test_blog_content_generation():
    """
    블로그 콘텐츠 생성 테스트
    """
    print("\n📝 블로그 콘텐츠 생성 테스트")
    print("=" * 50)
    
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo"
    gemini = GeminiAPI(API_KEY)
    
    # 블로그 제목과 내용 생성 프롬프트
    blog_prompt = """
    다음 블로그 제목에 대한 흥미로운 블로그 포스트 내용을 한국어로 작성해주세요:
    
    제목: "직장인이 알아야 할 효율적인 시간 관리 방법 5가지"
    
    요구사항:
    - 친근하고 읽기 쉬운 말투
    - 실용적인 팁 포함
    - 300-500자 정도의 분량
    """
    
    print("🔍 프롬프트:", blog_prompt[:100] + "...")
    print("-" * 30)
    
    # 창의성 있는 응답을 위해 temperature 설정
    response = gemini.generate_content(
        blog_prompt, 
        max_tokens=1000, 
        temperature=0.7
    )
    
    if response:
        generated_content = gemini.extract_text(response)
        print(f"✅ 생성된 블로그 내용:\n\n{generated_content}")
    else:
        print("❌ 블로그 콘텐츠 생성 실패")

def interactive_mode():
    """
    대화형 모드
    """
    print("\n💬 대화형 모드 (종료하려면 'quit' 입력)")
    print("=" * 50)
    
    API_KEY = "AIzaSyB_WcULiuWEF75vMr8NMfwtxCubnh9WBlo"
    gemini = GeminiAPI(API_KEY)
    
    while True:
        user_input = input("\n👤 질문을 입력하세요: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '종료']:
            print("👋 대화형 모드를 종료합니다.")
            break
            
        if not user_input:
            print("⚠️ 질문을 입력해주세요.")
            continue
            
        print("🤖 생각 중...")
        response = gemini.generate_content(user_input, temperature=0.8)
        
        if response:
            generated_text = gemini.extract_text(response)
            print(f"🤖 Gemini: {generated_text}")
        else:
            print("❌ 응답 생성에 실패했습니다.")

def main():
    """
    메인 실행 함수
    """
    print("🚀 Gemini API 테스트 프로그램")
    print("=" * 60)
    
    try:
        # 1. 기본 기능 테스트
        test_basic_functionality()
        
        # 2. 블로그 콘텐츠 생성 테스트
        test_blog_content_generation()
        
        # 3. 대화형 모드 실행 여부 확인
        print("\n" + "=" * 60)
        user_choice = input("대화형 모드를 실행하시겠습니까? (y/n): ").strip().lower()
        
        if user_choice in ['y', 'yes', '예', 'ㅇ']:
            interactive_mode()
        
        print("\n✨ 테스트 완료!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")

if __name__ == "__main__":
    main() 