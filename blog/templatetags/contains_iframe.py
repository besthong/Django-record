# 23/12/27 생성 파일 👇🏼
# 유투브 소스코드를 markdown content에 작성시, 유투브 재생이 되는데
# post_list에서 미리보기 화면에서 content가 전부 미리보여지는바람에, 유투브 재생 화면까지 캡쳐가 되어 보여짐
# 따라서 해당 py 코드와 post_list 내 content를 보여주는 부분을 분기처리하여, iframe 태그가 있을경우엔, 미리보기 안하도록 설정

from django import template
import re

register = template.Library() #Django 템플릿 라이브러리 인스턴스를 생성합니다.

def contains_iframe(content):  # <iframe 태그를 확인하는 함수 정의
    return bool(re.search(r'<iframe', content, re.IGNORECASE)) # <iframe 문자열을 대소문자를 구분하지 않고 검색하고, 결과가 있는지 확인합니다.

@register.filter #다음 함수를 Django 템플릿 필터로 등록합니다.
def has_iframe(value): #템플릿 필터를 정의합니다. 이 필터는 value에 contains_iframe 함수를 적용합니다.
    return contains_iframe(value) #value에 contains_iframe 함수를 적용하고 결과를 반환합니다.