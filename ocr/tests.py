import os
import io
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from PIL import Image
import cv2
import numpy as np

User = get_user_model()

def draw_bounding_boxes(image, res, output_path):
    # OpenCV에서 처리할 수 있도록 이미지 변환
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    for field in res['images'][0]['fields']:
        bounding_box = field['boundingPoly']['vertices']
        pts = np.array([[vertex['x'], vertex['y']] for vertex in bounding_box], np.int32)
        pts = pts.reshape((-1, 1, 2))

        # 필드 값이 없는 경우 빨간색, 있는 경우 초록색
        if field['inferText']:
            color = (0, 255, 0)
            thickness = 2
        else:
            color = (0, 0, 255)
            thickness = 4

        cv2.polylines(image, [pts], isClosed=True, color=color, thickness=thickness)

    cv2.imwrite(output_path, image)

def merge_images_horizontally(image_files):
    # 이미지 열기
    image1 = Image.open(image_files[0])
    image2 = Image.open(image_files[1])
    
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
    
    # 최종 이미지 반환
    return new_image

class OCRTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='testuser@example.com',
            password=make_password('testpassword'),
            nickname='testuser',
            username='testusername',
            nationality='testnation',
            work_at='testwork',
            is_active=True
        )
        self.client = APIClient()
        login_url = reverse('account:login')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # BASE_DIR을 사용하여 테스트 이미지 파일 경로 설정
        self.image_path1 = os.path.join(settings.BASE_DIR, 'test_img', 'kor.png')  
        self.image_path2 = os.path.join(settings.BASE_DIR, 'test_img', 'for_1.jpg')
        self.image_path3 = os.path.join(settings.BASE_DIR, 'test_img', 'for_del.jpg')

        # 테스트 이미지를 SimpleUploadedFile 객체로 변환
        self.image_file1 = SimpleUploadedFile(name='test_image1.png', content=open(self.image_path1, 'rb').read(), content_type='image/png')
        self.image_file2 = SimpleUploadedFile(name='test_image2.jpg', content=open(self.image_path2, 'rb').read(), content_type='image/jpeg')
        self.image_file3 = SimpleUploadedFile(name='test_image3.jpg', content=open(self.image_path3, 'rb').read(), content_type='image/jpeg')

    def test_foreigner_contract_upload(self):
        print("\nRunning foreigner_contract upload test...")
        data = {
            'contract': 'foreigner_contract',
            'image_files': [self.image_file2, self.image_file3],
        }
        response = self.client.post('/ocr/upload/', data, format='multipart')
        
        print("Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('result', response.data)
        self.assertIn('missing_items', response.data)

        # 결과 이미지를 저장
        merged_image = merge_images_horizontally([self.image_file2, self.image_file3])
        output_image_path = os.path.join(settings.BASE_DIR, 'boxed_image_foreigner.jpg')
        draw_bounding_boxes(merged_image, response.data['result'], output_image_path)
        print(f"Output image saved to: {output_image_path}")

    def test_standard_contract_upload(self):
        print("\nRunning standard_contract upload test...")
        data = {
            'contract': 'standard_contract',
            'image_files': [self.image_file1],
        }
        response = self.client.post('/ocr/upload/', data, format='multipart')

        print("Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('result', response.data)
        self.assertIn('missing_items', response.data)

        # 결과 이미지를 저장
        self.image_file1.seek(0)  # 파일 포인터를 시작으로 되돌림
        image = Image.open(io.BytesIO(self.image_file1.read()))
        output_image_path = os.path.join(settings.BASE_DIR, 'boxed_image_standard.jpg')
        draw_bounding_boxes(image, response.data['result'], output_image_path)
        print(f"Output image saved to: {output_image_path}")

    def test_foreigner_contract_upload_with_one_image(self):
        print("\nRunning foreigner_contract upload test with one image...")
        data = {
            'contract': 'foreigner_contract',
            'image_files': [self.image_file2],
        }
        response = self.client.post('/ocr/upload/', data, format='multipart')
        
        print("Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Two images are required for foreigner_contract.')

    def test_standard_contract_upload_with_multiple_images(self):
        print("\nRunning standard_contract upload test with multiple images...")
        data = {
            'contract': 'standard_contract',
            'image_files': [self.image_file1, self.image_file2],
        }
        response = self.client.post('/ocr/upload/', data, format='multipart')

        print("Status Code:", response.status_code)
        print("Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'One image is required for standard_contract.')
