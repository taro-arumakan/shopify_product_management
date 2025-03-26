import pytesseract
from PIL import Image
import re
import os

korean_pattern = re.compile(r'[\uac00-\ud7a3]')

def contains_korean_characters(text):
    return bool(korean_pattern.search(text))

def is_model_info_image(image):
    extracted_text = pytesseract.image_to_string(image, lang='eng')
    return 'model info' in extracted_text.lower()

def check_images_for_korean(file_path):
    try:
        image = Image.open(file_path)
        if is_model_info_image(image):
            return 'model_info'
        extracted_text = pytesseract.image_to_string(image, lang='kor')
        return contains_korean_characters(extracted_text)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def already_translated_for_psd(psd_path):
    parts = psd_path.split('_')
    seq = str(int(parts[-2]) - 1).zfill(2)
    return ['_'.join(parts[:-2] + [seq] + parts[-1:]).replace('.psd', '.jpg')] + [psd_path.replace('.psd', '.jpg')]

localdir = '/Users/taro/Downloads/apricot_studios_images_all'
image_files = [f'{localdir}/{p}' for p in sorted(os.listdir(localdir))]
psds = [p for p in image_files if p.endswith('.psd')]
already_translated = sum([already_translated_for_psd(p) for p in psds], [])

result = {}
for path in [p for p in image_files if p not in already_translated]:
    result.setdefault(check_images_for_korean(path), []).append(path)

print('model_info')
for path in result['model_info']:
    print(path)

print()
print()
print('possible hangul')
for path in result[True]:
    print(path)
