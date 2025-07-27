import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment

def create_sample_data():
    """
    블로그 포스팅용 샘플 데이터가 포함된 Excel 파일을 생성합니다.
    """
    
    # 많은 사람들이 클릭할 것 같은 블로그 포스팅 제목 데이터
    blog_titles = [
        "직장인 월급 200만원으로 1년에 1000만원 모으는 비법",
        "30대가 꼭 알아야 할 투자 상식 10가지",
        "집에서 할 수 있는 부업 추천 BEST 7",
        "다이어트 성공률 90% 올리는 간단한 방법",
        "연봉 협상에서 절대 실패하지 않는 말하기 기술",
        "20대에 꼭 해야 할 자기계발 리스트",
        "스마트폰으로 월 50만원 벌기 실제 후기",
        "면접에서 100% 합격하는 자기소개 공식",
        "주식 초보자도 수익내는 종목 선택법",
        "혼자 사는 사람을 위한 절약 생활 꿀팁"
    ]
    
    # 각 제목에 맞는 내용 생성
    blog_contents = [
        "직장인이라면 누구나 고민하는 돈 모으기! 실제로 월급 200만원으로 1년에 1000만원을 모은 저의 경험을 공유합니다. 가계부 작성법부터 투자 방법까지 상세히 알려드려요.",
        
        "30대는 인생의 황금기! 하지만 투자에 대해 모르면 큰 손해를 볼 수 있어요. 30대가 꼭 알아야 할 투자 상식 10가지를 정리했습니다. 주식, 부동산, 펀드까지 모든 것을 다뤄요.",
        
        "코로나 시대, 집에서도 충분히 돈을 벌 수 있어요! 실제로 제가 해본 부업들 중에서 정말 돈이 되는 것들만 골라서 추천드립니다. 온라인 쇼핑몰부터 블로그까지!",
        
        "다이어트, 작심삼일로 끝나시나요? 성공률 90%를 자랑하는 다이어트 방법을 공개합니다. 운동 없이도 가능한 식단 조절법과 생활 습관 개선 방법을 알려드려요.",
        
        "연봉 협상, 어떻게 해야 할지 모르겠다고요? 10년차 직장인이 알려주는 연봉 협상 노하우! 이 방법으로 연봉을 30% 올렸습니다. 실제 대화 예시까지 포함되어 있어요.",
        
        "20대는 자기계발의 골든타임! 30대가 되어서 후회하지 않으려면 지금 당장 시작해야 할 것들이 있어요. 독서, 운동, 인맥 관리 등 20대 필수 자기계발 리스트를 공개합니다.",
        
        "스마트폰만 있으면 누구나 할 수 있는 부업! 실제로 월 50만원을 벌고 있는 저의 후기를 솔직하게 공유합니다. 어떤 앱을 사용했는지, 얼마나 시간을 투자했는지 모두 공개해요.",
        
        "면접에서 떨어지는 이유, 자기소개 때문일 수도 있어요! 100% 합격하는 자기소개 공식을 알려드립니다. 실제 면접관이 좋아하는 키워드와 구성 방법까지 상세히 설명해요.",
        
        "주식 투자, 어려워 보이지만 원리만 알면 쉬워요! 주식 초보자도 수익을 낼 수 있는 종목 선택법을 공개합니다. 차트 보는 법부터 매매 타이밍까지 모든 것을 알려드려요.",
        
        "혼자 살면서 돈 관리하기 어려우시죠? 1인 가구를 위한 절약 생활 꿀팁을 공유합니다. 식비, 교통비, 통신비까지 모든 생활비를 줄이는 방법을 알려드려요."
    ]
    
    # 데이터프레임 생성
    data = {
        '제목': blog_titles,
        '내용': blog_contents
    }
    
    df = pd.DataFrame(data)
    
    # Excel 파일로 저장
    with pd.ExcelWriter('data.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='블로그데이터')
        
        # 워크시트 가져오기
        worksheet = writer.sheets['블로그데이터']
        
        # 헤더 스타일 설정
        header_font = Font(bold=True, size=12)
        header_alignment = Alignment(horizontal='center', vertical='center')
        
        # A1, B1 셀 스타일 적용
        worksheet['A1'].font = header_font
        worksheet['A1'].alignment = header_alignment
        worksheet['B1'].font = header_font
        worksheet['B1'].alignment = header_alignment
        
        # 열 너비 조정
        worksheet.column_dimensions['A'].width = 50  # 제목 열
        worksheet.column_dimensions['B'].width = 80  # 내용 열
        
        # 행 높이 조정 (내용이 길어서)
        for row in range(2, 12):  # A2부터 A11까지
            worksheet.row_dimensions[row].height = 60
    
    print("✅ data.xlsx 파일이 성공적으로 생성되었습니다!")
    print(f"📊 총 {len(blog_titles)}개의 블로그 포스팅 샘플 데이터가 포함되어 있습니다.")
    print("\n📝 생성된 블로그 제목 목록:")
    for i, title in enumerate(blog_titles, 1):
        print(f"{i:2d}. {title}")
    
    return df

def main():
    """
    메인 실행 함수
    """
    print("🚀 블로그 포스팅 샘플 데이터 생성 시작...")
    print("=" * 60)
    
    try:
        # 샘플 데이터 생성
        df = create_sample_data()
        
        print("\n" + "=" * 60)
        print("✨ 작업 완료!")
        print("📁 현재 폴더에 'data.xlsx' 파일을 확인해보세요.")
        print("💡 이 데이터는 네이버 블로그 자동 포스팅에 사용할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")
        print("💡 pandas와 openpyxl 패키지가 설치되어 있는지 확인해주세요.")
        print("   설치 명령어: pip install pandas openpyxl")

if __name__ == "__main__":
    main() 