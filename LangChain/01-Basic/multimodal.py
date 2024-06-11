import base64
from functools import lru_cache
import os
import requests
from typing import Dict, List, Optional, Any
from IPython.display import Image, display
import concurrent.futures

class MultiModal:
  # model의 타입을 Any로 지정한다. 
  # 이는 invoke와 stream 메서드가 사용하는 모델이 다양한 타입일 수 있기 때문이다.
  # Optional[str]를 사용하여 system_prompt와 user_prompt가 선택적으로 지정될 수 있음을 나타낸다.
  def __init__(self, model: Any, system_prompt: Optional[str]=None, user_prompt: Optional[str]=None) -> None:
    """
    MultiModal 클래스를 초기화한다.
    
    :param model: 응답을 생성할 모델
    :param system_prompt: 시스템 프롬프트 (옵션)
    :param user_prompt: 사용자 프롬프트 (옵션)
    """
    self.model = model
    self.system_prompt = system_prompt
    self.user_prompt = user_prompt
    self.init_prompt()
  
  def init_prompt(self) -> None:
    """
    시스템 및 사용자 프롬프트를 초기화한다.
    """
    if self.system_prompt is None:
      self.system_prompt = "당신은 한국어로 이미지와 관련된 보고서를 작성하는 데 도움이 되는 도우미입니다."
    if self.user_prompt is None:
      self.user_prompt = "한국어로 이미지를 대체 텍스트로 설명해주세요"
  
  # @lru_cache 데코레이터를 사용하여 URL 및 파일 경로의 이미지 인코딩 결과를 캐싱하여 반복 호출 시 성능을 향상시킨다.
  @lru_cache(maxsize=32)
  def encode_image_from_url(self, url: str) -> str:
    """
    URL에서 이미지를 가져와 base64 문자열로 인코딩한다.

    :param url: 이미지를 가져올 URL
    :return: base64로 인코딩된 이미지 문자열
    :raises Exception: 이미지 가져오기 실패 시 예외 발생  
    """
    # 이미지 가져오기 실패시 예외처리
    try:
      response: requests.Response = requests.get(url)
      response.raise_for_status()
      image_content: bytes = response.content
      mime_type: str = self.get_mime_type_from_url(url)
      encoded_image: str = base64.b64encode(image_content).decode('utf-8')
      return f"data:{mime_type};base64,{encoded_image}"
    except requests.RequestException as e:
      raise Exception(f"이미지 가져오기 실패: {e}")
  
  def encode_image_from_file(self, file_path: str) -> str:
    """
    파일에서 이미지를 읽어 base64 문자열로 인코딩한다.

    :param file_path: 이미지 읽을 파일 경로
    :return: base64로 인코딩된 이미지 문자열
    :raises Exception: 이미지 파일 읽기 실패 시 예외 발생
    """
    try:
      with open(file_path, "rb") as image_file:
        image_content: bytes = image_file.read()
        mime_type: str = self.get_mime_type_from_file(file_path)
        encoded_image: str = base64.b64encode(image_content).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_image}"
    except IOError as e:
      raise Exception(f"이미지 파일 읽기 실패: {e}")
  
  def get_mime_type_from_file(self, file_path: str) -> str:
    """
    파일 확장자를 기반으로 MIME 타입을 가져온다.

    :param file_path: 이미지 파일 경로 또는 URL
    :return: MIME 타입 문자열
    """    
    file_ext: str = os.path.splitext(file_path)[1].lower()
    if file_ext in [".jpg", ".jpeg"]:
      return "image/jpeg"
    elif file_ext == ".png":
      return "image/png"
    else:
      return "image/unknown"
    
  def get_mime_type_from_url(image_url: str) -> str:
    """
    주어진 이미지 URL의 MIME 타입을 반환한다.

    :param image_url: 이미지 URL
    :return: 이미지의 MIME 타입
    :raises Exception: 이미지를 다운로드할 수 없는 경우 또는 MIME 타입을 가져올 수 없는 경우
    """
    try:
        # 이미지 URL에서 헤더만 요청하여 content-type 확인
        response = requests.head(image_url)
        response.raise_for_status()

        # content-type 헤더에서 MIME 타입 추출
        mime_type = response.headers.get('content-type')
        if mime_type:
            return mime_type
        else:
            raise Exception("MIME 타입 가져오기 실패")
    except requests.RequestException as e:
        raise Exception(f"이미지 다운로드 실패: {e}")

  
  def encode_image(self, image_path: str) -> str:
    """
    주어진 경로에서 이미지를 인코딩한다.
    
    :param image_path: 이미지의 URL 또는 파일 경로
    :return base64로 인코딩된 이미지 문자열
    """
    if image_path.startswith("http://") or image_path.startswith("https://"):
      return self.encode_image_from_url(image_path)
    else:
      return self.encode_image_from_file(image_path)

  def display_image(self, encoded_image: str) -> None:
    """
    Juptyer Notebook에서 이미지를 표시한다.
    
    :param encoded_image: base64로 인코딩된 이미지 문자열
    """
    display(Image(url=encoded_image))
    
  def create_messages(self, image_url: str, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None, display_image: bool = True) -> List[Dict[str, Any]]:
    """
    모델에 전송할 메시지를 생성한다. (인코딩된 이미지 포함)
    
    :param image_url: 이미지의 URL 또는 파일 경로
    :param system_prompt: 시스템 프롬프트 (옵션)
    :param user_prompt: 사용자 프롬프트 (옵션)
    :param display_image: 이미지를 표시할지 여부
    :return: 메시지 딕셔너리 리스트
    """
    if system_prompt is None:
      system_prompt = self.system_prompt
    if user_prompt is None:
      user_prompt = self.user_prompt
      
    encoded_image: str = self.encode_image(image_url)
    if display_image:
      self.display_image(encoded_image)
      
    messages: List[Dict[str, Any]] = [
      {
        "role": "system",
        "content": system_prompt
      },
      {
        "role": "user",
        "content": [
          {
            "type": "text", 
            "text": user_prompt
          },
          {
            "type": "image_url",
            "image_url": {"url": encoded_image}
          }
        ]
      }
    ]
    return messages
  
  def invoke(self, image_url: str, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None, display_image: bool = True) -> Any:
    """
    생성된 메시지를 모델에 보내고 응답을 반환한다.

    :param image_url: 이미지의 URL 또는 파일 경로
    :param system_prompt: 시스템 프롬프트 (옵션)
    :param user_prompt: 사용자 프롬프트 (옵션)
    :param display_image: 노트북에 이미지를 표시할지 여부
    :return: 모델의 응답 내용
    """
    messages: List[Dict[str, Any]] = self.create_messages(image_url, system_prompt, user_prompt, display_image)
    response: Any = self.model.invoke(messages)
    return response.content
    
  def stream(self, image_url: str, system_prompt: Optional[str] = None, user_prompt: Optional[str] = None, display_image: bool = True) -> Any:
    """
    모델의 스트림 응답을 처리한다.
    
    :param image_url: 이미지의 URL 또는 파일 경로
    :param system_prompt: 시스템 프롬프트 (옵션)
    :param user_prompt: 사용자 프롬프트 (옵션)
    :param display_image: 노트북에 이미지를 표시할지 여부
    :return: 모델의 응답 내용
    """
    messages: List[Dict[str, Any]] = self.create_messages(image_url, system_prompt, user_prompt, display_image)
    response: Any = self.model.stream(messages)
    return response
  
  def encode_images_concurrently(self, image_paths: List[str]) -> List[str]:
    """
    여러 이미지를 병렬로 인코딩한다.

    :param image_paths: 이미지의 URL 또는 파일 경로 목록
    :return: base64로 인코딩된 이미지 문자열 목록
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        encoded_images: List[str] = list(executor.map(self.encode_image, image_paths))
    return encoded_images

