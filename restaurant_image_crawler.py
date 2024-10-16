import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv
import json

# .env 파일에서 환경 변수를 불러옴
load_dotenv()

# .env 파일에 저장된 API 키를 불러오기
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# CSV 파일을 읽어서 데이터프레임으로 변환
csv_file_path = 'KC_MTPCLT_RSTRNT_DATA_2023.csv'  # 실제 CSV 파일 경로를 입력하세요
df = pd.read_csv(csv_file_path)

# 'PET_POSBL_AT' 열에서 TRUE 값인 항목만 필터링 (반려동물 허용된 곳만 필터링)
df_pet_friendly = df[df['PET_POSBL_AT'] == 'Y'].copy()  # 'Y'가 TRUE에 해당하는 값인 경우, copy() 추가

# 이미지 및 JSON 저장을 위한 폴더 생성
if not os.path.exists('images'):
    os.makedirs('images')
if not os.path.exists('jsons'):
    os.makedirs('jsons')

# 'IMG_EXIST' 열을 기본값 'N'으로 추가
df_pet_friendly['IMG_EXIST'] = 'N'

# 상세 로그를 출력하는 함수
def log(message):
    print(f"[LOG]: {message}")

# Google Places API를 사용하여 장소의 대표 이미지 및 세부 정보를 가져오는 함수
def get_place_details(place_name, place_address):
    search_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': f"{place_name}, {place_address}",
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': API_KEY
    }
    
    # API 호출 및 응답 받기
    log(f"장소 검색 API 호출: {place_name}, {place_address}")
    response = requests.get(search_url, params=params)
    result = response.json()
    log(f"API 응답 코드: {response.status_code}")
    
    # 응답이 정상인지 확인
    if response.status_code == 200:
        candidates = result.get('candidates', [])
        log(f"'{place_name}'에 대해 {len(candidates)}개의 후보 장소가 발견되었습니다.")
        
        if candidates:
            place_id = candidates[0]['place_id']
            log(f"가장 유사한 장소의 Place ID: {place_id}")
            
            # 장소의 세부 정보를 가져오는 API 요청
            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
            details_params = {
                'place_id': place_id,
                'fields': 'photos,name,formatted_address,formatted_phone_number,international_phone_number,geometry,rating,user_ratings_total,reviews,opening_hours,website,price_level,business_status',
                'key': API_KEY
            }
            log(f"장소 세부 정보 API 호출 (Place ID: {place_id})")
            details_response = requests.get(details_url, params=details_params)
            details_result = details_response.json()

            # details_result 반환 및 JSON 저장
            return details_result
        else:
            log(f"'{place_name}'에 대한 유효한 장소를 찾을 수 없습니다.")
    else:
        log(f"API 응답 오류: {response.status_code}, 내용: {response.text}")
    
    return None

# 이미지 다운로드 함수
def download_image(url, save_path):
    log(f"이미지 다운로드 시도: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        log(f"이미지 저장 완료: {save_path}")
        return True
    else:
        log(f"이미지 다운로드 실패: {response.status_code}")
        return False

# N개의 가게에 대해 대표 이미지 및 세부 정보 가져오기 (이미지가 있는 장소만 별도 CSV에 저장)
def process_pet_friendly_places(n):
    total_rows = len(df_pet_friendly)
    if n == -1:
        n = total_rows  # 끝까지 처리

    for i in range(min(n, total_rows)):  # n개의 데이터를 처리
        place_name = df_pet_friendly['FCLTY_NM'].iloc[i]
        place_address = df_pet_friendly['RDNMADR_NM'].iloc[i]
        
        log(f"\n========= {i+1}번째 가게 (반려동물 가능) 정보 처리 =========")
        details_result = get_place_details(place_name, place_address)

        img_exist = 'N'  # 기본값: 이미지가 없는 경우 'N'

        if details_result:
            # 장소 세부 정보 저장 (폴더명: jsons/{i+1})
            json_folder_path = f'jsons/{i+1}'
            if not os.path.exists(json_folder_path):
                os.makedirs(json_folder_path)

            json_file_path = f'{json_folder_path}/details.json'
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(details_result, json_file, ensure_ascii=False, indent=4)
            log(f"장소 세부 정보 JSON 저장 완료: {json_file_path}")
            
            # 이미지 다운로드 처리
            place_details = details_result.get('result', {})
            if 'photos' in place_details:
                photo_reference = place_details['photos'][0]['photo_reference']
                photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}"
                log(f"{i+1}번째 가게 '{place_name}'의 대표 이미지 URL: {photo_url}")
                
                # 이미지 저장 경로 설정 (폴더명: images/{i+1})
                image_folder_path = f'images/{i+1}'
                if not os.path.exists(image_folder_path):
                    os.makedirs(image_folder_path)

                image_save_path = f'{image_folder_path}/image.jpg'
                if download_image(photo_url, image_save_path):
                    img_exist = 'Y'  # 이미지가 성공적으로 다운로드된 경우 'Y'
        
        # 'IMG_EXIST' 열 값 업데이트
        df_pet_friendly.at[df_pet_friendly.index[i], 'IMG_EXIST'] = img_exist
        
        # Google API 호출 간 시간 간격을 두기 위한 지연
        time.sleep(2)

    # 이미지를 가져온 장소만을 새로운 CSV 파일로 저장
    df_pet_friendly.to_csv('pet_friendly_places_with_images.csv', index=False, encoding='utf-8-sig')
    log(f"이미지를 가져온 장소만 포함한 CSV 저장 완료: pet_friendly_places_with_images.csv")

# 예시: 처음 5개 데이터에 대해 처리 (-1을 입력하면 끝까지 처리)
process_pet_friendly_places(-1)  # 원하는 N 값을 입력하세요 (예: 10, -1이면 전체 처리)
