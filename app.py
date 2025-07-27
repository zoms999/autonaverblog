from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def index():
    """사용자 입력을 위한 기본 폼을 렌더링합니다."""
    return render_template('index.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    """폼에서 받은 데이터를 data.json 파일로 저장합니다."""
    try:
        sample_urls = [
            request.form.get('url1'),
            request.form.get('url2'),
            request.form.get('url3'),
            request.form.get('url4'),
        ]
        sample_urls = [url for url in sample_urls if url]
        data = {
            "naver_id": request.form.get('naver_id'),
            "naver_pw": request.form.get('naver_pw'),
            "post_info": {
                "title": request.form.get('title'),
                "referral_id": request.form.get('referral_id'),
                "sample_urls": sample_urls
            }
        }
        # data.json 파일에 저장
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # 성공 메시지 반환
        return render_template('result.html', 
                               message="✅ 데이터 저장이 완료되었습니다. 이제 터미널에서 'python automation_runner.py'를 실행해주세요.")
    except Exception as e:
        return render_template('result.html', 
                               message=f"❌ 데이터 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)