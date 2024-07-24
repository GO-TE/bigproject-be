from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

import requests
import uuid
import time
import json
import pandas as pd
from PIL import Image
import io

with open('secrets.json') as f:
    keys = json.load(f)

ocr_secret_key = keys['ocr_api_key']

api_url = 'https://ri3uhqhxwl.apigw.ntruss.com/custom/v1/32453/641c0e4c0576bd73c35830c04172874cdc68a38740076ebdfdff028ad834b69d/infer'

def merge_images_horizontally(image_file):
    # 이미지 열기
    image1 = Image.open(image_file[0])
    image2 = Image.open(image_file[1])
    
    # 두 이미지의 높이 중 더 큰 높이를 선택
    max_height = max(image1.height, image2.height)
    
    # 두 이미지의 너비를 합산
    total_width = image1.width + image2.width
    
    # 새로운 빈 이미지 생성 (RGB 모드)
    new_image = Image.new('RGB', (total_width, max_height))
    
    # 새로운 이미지에 첫 번째 이미지 붙이기
    new_image.paste(image1, (0, 0))
    
    # 새로운 이미지에 두 번째 이미지 붙이기
    new_image.paste(image2, (image1.width, 0))
    
    # 이미지 바이트를 메모리에 저장
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    return img_byte_arr

def ocr(api_url, secret_key, templateId, image_data):
    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'demo',
                'templateIds': [templateId]
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [
        ('file', ('image.jpg', image_data, 'image/jpeg'))
    ]
    headers = {
        'X-OCR-SECRET': secret_key
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
    res = json.loads(response.text.encode('utf8'))
    fields = res['images'][0]['fields']

    data = {
        'Field Name': [field['name'] for field in fields],
        'Value': [field['inferText'] for field in fields]
    }

    df = pd.DataFrame(data)

    return df, res

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        contract = request.data.get('contract')
        image_files = request.FILES.getlist('image_files')
        
        if not image_files:
            return Response({"error": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if contract == 'standard_contract':
            if len(image_files) != 1:
                return Response({"error": "One image is required for standard_contract."}, status=status.HTTP_400_BAD_REQUEST)
            templateId = 30895
            check_list = ['근로개시일', '근무장소', '업무내용', '소정근로시간', '근무일_휴일', '임금', '연차유급휴가', 
                          '사회보험_적용여부', '근로계약서_교부', '성실한_이행의무', '기타', '날짜', '사업주', '근로자']
            image_data = image_files[0].read()
        elif contract == 'foreigner_contract':
            if len(image_files) != 2:
                return Response({"error": "Two images are required for foreigner_contract."}, status=status.HTTP_400_BAD_REQUEST)
            templateId = 30944
            check_list = ['사용자', '취업자', '근로계약기간', '취업장소', '업무내용', '근무시간', '휴게시간', '휴일', '임금',
                          '임금지급일', '지급방법', '숙식제공', '근로기준법', '날짜', '사용자_서명', '취업자_서명']
            image_data = merge_images_horizontally(image_files)
        else:
            return Response({"error": "Invalid contract type."}, status=status.HTTP_400_BAD_REQUEST)
        
        df, res = ocr(api_url, ocr_secret_key, templateId, image_data)

        def check_items(df, check_list):
            field_names = df['Field Name'].tolist()
            missing_items = []

            for item in check_list:
                if item not in field_names:
                    missing_items.append(item)
                else:
                    value = df.loc[df['Field Name'] == item, 'Value'].values[0]
                    if not value:
                        missing_items.append(item)

            return missing_items

        missing_items = check_items(df, check_list)

        return Response({"result": res, "missing_items": missing_items}, status=status.HTTP_200_OK)