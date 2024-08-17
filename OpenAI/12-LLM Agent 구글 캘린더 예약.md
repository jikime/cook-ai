**주요내용**
- Google 캘린더 API 설정 및 인증 과정 🛠️
- OpenAI GPT를 이용한 자연어 처리 및 일정 관리 🤖
- JSON 형식으로 일정 등록 및 관리 방법 📅

### LLM Agent 기반 구글 캘린더 자동 예약 서비스 구성하기


##### 1. 구글 캘린더 API 사용하기


1-1. [일정 구글 API 연동하기](https://velog.io/@kho5420/Python-%EA%B5%AC%EA%B8%80-Open-API%EB%A1%9C-%EC%BA%98%EB%A6%B0%EB%8D%94-%ED%99%9C%EC%9A%A9%ED%95%B4%EB%B3%B4%EA%B8%B0) 참고하여 OAuth 인증정보를 담은 파일을 다운로드 받아야 합니다.


1-2. [1-1]에서 생성한 `client_secret_xxx.json` 파일을 `credentials.json`라는 이름으로 변경해주고 적당한 곳으로 이동시킵니다.


1-3 구글 캘린더 API / calendar ID 설정


아래 코드는 Google 캘린더 API를 사용하기 위한 설정 정보를 포함하고 있습니다. 사용자는 자신의 Google 캘린더 API 키(`google_calendar_api_key`)와 캘린더 ID(`calendar_id`)를 변수로 저장하여 API 요청에 사용할 수 있습니다.



```python
# Google 캘린더 API 키
google_calendar_api_key = "AIzaSyC2RtqP0BFt3i60rErefJlujbqFEw3apjw"
# 사용자의 캘린더 ID
calendar_id = "jikime@gmail.com"
```

아래 명령어는 `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, 그리고 `openai` 라이브러리를 최신 버전으로 업그레이드하는 명령어입니다. 이 라이브러리들은 Google API와 OpenAI를 사용하는 데 필요하며, `%pip install --upgrade` 명령어를 통해 각각의 라이브러리를 최신 상태로 유지합니다.



```python
# Google API와 OpenAI 관련 라이브러리를 최신 버전으로 업그레이드합니다.
%pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
```

Google Calendar API를 사용하여 Google 캘린더와 상호작용하는 클래스 `GoogleCalendar`를 정의합니다. 이 클래스는 사용자 인증, 이벤트 조회, 이벤트 추가, 이벤트 삭제 등의 기능을 제공합니다. 사용자 인증은 저장된 토큰을 사용하거나 새로운 토큰을 생성하여 진행합니다. `get_today_events` 메소드를 통해 오늘 일정을 조회하고, `set_google_calendar`, `delete_google_calendar`, `get_google_calendar` 메소드를 통해 캘린더에 이벤트를 추가, 삭제, 조회할 수 있습니다. 또한, `get_event_id_list` 메소드를 사용하여 최근 이벤트의 ID 목록을 가져올 수 있습니다. 이 클래스는 Google Calendar API와의 상호작용을 위한 기본적인 메커니즘을 제공하며, API 키와 토큰 관리를 포함한 인증 과정을 캡슐화합니다.



```python
from datetime import datetime
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleCalendar:
    def __init__(self, calendar_id=None, google_calendar_api_key=None, dir_token="./"):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.file_path = os.path.join(dir_token, "token.json")
        self.calendar_id = calendar_id
        self.google_calendar_api_key = google_calendar_api_key
        self.service = self.get_authenticated_service()


    def get_authenticated_service(self):
        # 인증 정보를 저장할 변수
        creds = None
        
        # 이전에 저장된 토큰이 있는지 확인
        if os.path.exists(self.file_path):
            creds = Credentials.from_authorized_user_file(self.file_path, self.SCOPES)
        
        # 유효한 인증 정보가 없는 경우 새로 생성
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(os.path.join(dir_token, 'credentials.json'), self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 생성된 인증 정보를 파일로 저장
            with open(self.file_path, "w") as token:
                token.write(creds.to_json())
                
        return build('calendar', 'v3', credentials=creds)

    def get_today_events(self):
        # 타임존 설정 (예: 'Asia/Seoul')
        timezone = pytz.timezone('Asia/Seoul')
        
        # 오늘 날짜의 시작과 끝 시간 설정
        today_start = datetime.now(timezone).replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start.replace(hour=23, minute=59, second=59)

        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=today_start.isoformat(),
            timeMax=today_end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result
        
    def set_google_calendar(self, event):
        self.service.events().insert(calendarId=self.calendar_id, body=event).execute()

    def delete_google_calendar(self, event_id):
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()

    def get_google_calendar(self, event_id):
        event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
        
        return event

    def get_event_id_list(self, num_events=10):
        events = self.service.events().list(calendarId=self.calendar_id).execute()
        event_id_list = [event["id"] for event in events["items"]]
        
        return event_id_list[-num_events:]
```

아래 코드는 `GoogleCalendar` 클래스의 인스턴스를 생성하여 Google 캘린더와의 연동을 설정합니다. 인스턴스 생성 시, `calendar_id`, `google_calendar_api_key`, 그리고 토큰을 저장할 디렉토리 경로인 `dir_token`을 인자로 전달합니다.



```python
# GoogleCalendar 클래스의 인스턴스를 생성합니다.
dir_token = "../Assets/data"
google_calendar = GoogleCalendar(calendar_id = calendar_id, google_calendar_api_key = google_calendar_api_key, dir_token=dir_token)
```

아래 코드는 `google_calendar` 객체를 사용하여 현재 날짜에 해당하는 이벤트 목록을 검색합니다. 사용자는 이를 통해 오늘 일정에 대한 개요를 얻을 수 있습니다.



```python
google_calendar.get_today_events() # 오늘의 이벤트를 가져옵니다.
```

<pre>
{'kind': 'calendar#events',
 'etag': '"p32g9buchj7ioe0o"',
 'summary': 'Anthony.Kim',
 'description': '',
 'updated': '2024-08-08T10:34:27.940Z',
 'timeZone': 'Asia/Seoul',
 'accessRole': 'owner',
 'defaultReminders': [{'method': 'popup', 'minutes': 30},
  {'method': 'email', 'minutes': 30}],
 'items': [{'kind': 'calendar#event',
   'etag': '"3445742677826000"',
   'id': 'as54jmud22b8te3bo4b6ijeh9k',
   'status': 'confirmed',
   'htmlLink': 'https://www.google.com/calendar/event?eid=YXM1NGptdWQyMmI4dGUzYm80YjZpamVoOWsgamlraW1lQG0',
   'created': '2024-08-05T15:22:18.000Z',
   'updated': '2024-08-05T15:22:18.913Z',
   'summary': 'langchain 모임',
   'description': 'LLM 모임',
   'location': '옐로스톤 스터디룸',
   'creator': {'email': 'jikime@gmail.com', 'self': True},
   'organizer': {'email': 'jikime@gmail.com', 'self': True},
   'start': {'dateTime': '2024-08-08T19:00:00+09:00',
    'timeZone': 'Asia/Seoul'},
   'end': {'dateTime': '2024-08-08T21:00:00+09:00', 'timeZone': 'Asia/Seoul'},
   'iCalUID': 'as54jmud22b8te3bo4b6ijeh9k@google.com',
   'sequence': 0,
   'reminders': {'useDefault': True},
   'eventType': 'default'}]}
</pre>
Google 캘린더의 API를 사용하여 이벤트 ID 목록을 가져오고, 이를 출력합니다. `google_calendar.get_event_id_list()` 함수는 이벤트 ID 목록을 반환합니다. 이 목록은 이후에 다양한 용도로 활용될 수 있습니다.



```python
# Google 캘린더에서 이벤트 ID 목록을 가져옵니다.
event_list= google_calendar.get_event_id_list()
# 이벤트 목록을 출력합니다.
event_list
```

<pre>
['_8h1jig9o64rk8b9h64o32b9k74o48b9o6crj4b9h6p2j4dq2612j0c1m70',
 'as54jmud22b8te3bo4b6ijeh9k',
 '_6kqj4h9i88q4cb9i61242b9k88r44b9p65146b9m8oq32d9l6gq48ghm6c',
 '_8kp42gq16gr4aba46grjgb9k8d0k2ba28h348ba36l234ca16h0jcci668']
</pre>
아래 코드는 `google_calendar` 객체의 `get_google_calendar` 메서드를 사용하여 `event_list`의 첫 번째 이벤트를 가져옵니다. 사용자는 이를 통해 특정 이벤트 정보에 접근할 수 있습니다.



```python
google_calendar.get_google_calendar(event_list[0])  # 첫 번째 이벤트를 구글 캘린더에서 가져옵니다.
```

<pre>
{'kind': 'calendar#event',
 'etag': '"3445732710128000"',
 'id': '_8h1jig9o64rk8b9h64o32b9k74o48b9o6crj4b9h6p2j4dq2612j0c1m70',
 'status': 'confirmed',
 'htmlLink': 'https://www.google.com/calendar/event?eid=XzhoMWppZzlvNjRyazhiOWg2NG8zMmI5azc0bzQ4YjlvNmNyajRiOWg2cDJqNGRxMjYxMmowYzFtNzAgamlraW1lQG0',
 'created': '2024-08-05T13:47:52.000Z',
 'updated': '2024-08-05T13:59:15.064Z',
 'summary': '정희철 교수님 채혈없음',
 'location': '강남세브란스병원, 대한민국 서울특별시 강남구 언주로 211',
 'creator': {'email': 'jikime@gmail.com', 'self': True},
 'organizer': {'email': 'jikime@gmail.com', 'self': True},
 'start': {'dateTime': '2024-08-06T10:20:00+09:00', 'timeZone': 'Asia/Seoul'},
 'end': {'dateTime': '2024-08-06T10:35:00+09:00', 'timeZone': 'Asia/Seoul'},
 'iCalUID': 'DC9A817D-1101-490D-8372-16E27B0E0068',
 'sequence': 0,
 'reminders': {'useDefault': True},
 'eventType': 'default'}
</pre>
아래 코드는 특정 이벤트에 대한 정보를 담고 있는 딕셔너리를 생성합니다. `event` 딕셔너리는 이벤트의 제목(`summary`), 장소(`location`), 설명(`description`), 시작 시간(`start`), 그리고 종료 시간(`end`)을 포함합니다. 시작과 종료 시간은 각각 `dateTime`과 `timeZone` 키를 가진 내부 딕셔너리로 구성됩니다. 이벤트는 2024년 8월 8일 오후 7시부터 오후 9시까지 진행되며, 모든 시간은 서울 시간대(`Asia/Seoul`)를 기준으로 합니다.



```python
event = {
    'summary': 'AI 모임', # 일정 제목
    'location': '강남역', # 일정 장소
    'description': '노트북 지참', # 일정 설명
    'start': { # 시작 날짜
        'dateTime': "2024-08-08" + 'T19:00:00',
        'timeZone': 'Asia/Seoul',
    },
    'end': { # 종료 날짜
        'dateTime': '2024-08-08' + 'T21:00:00',
        'timeZone': 'Asia/Seoul',
    },
}
```

함수 `set_google_calendar`는 Google 캘린더에 이벤트를 설정하는 기능을 수행합니다. 이 함수는 `event` 매개변수를 통해 설정할 이벤트의 정보를 받습니다.



```python
google_calendar.set_google_calendar(event) # Google 캘린더에 이벤트를 설정합니다.
```

##### 2. Open AI Api 연동해서 자동 예약 시스템 만들기


##### 2-1 GTP API를 이용하여 답변 생성하기


`load_dotenv` 함수를 호출함으로써, `.env` 파일 내에 정의된 환경 변수들이 프로그램의 환경 변수로 로드됩니다. 이는 보안이 중요한 설정값들을 코드에 직접 하드코딩하지 않고 관리할 수 있게 해줍니다.



```python
# .env 파일에서 환경 변수를 로드합니다.
from dotenv import load_dotenv

load_dotenv()
```

<pre>
True
</pre>
아래 코드는 OpenAI의 GPT 모델을 사용하여 사용자 입력(`event`)과 시스템 메시지(`system`)를 기반으로 대화를 생성합니다. `model_name` 변수를 통해 사용할 모델을 지정하며, `OpenAI` 클라이언트를 초기화하여 API 요청을 수행합니다. `response_from_llm` 함수는 시스템과 사용자 역할을 구분하여 메시지를 구성하고, 이를 모델에 전달하여 생성된 대화의 첫 번째 메시지 내용을 반환합니다.



```python
from openai import OpenAI

model_name="gpt-4o-mini"

client = OpenAI()

def response_from_llm(event, system, user):
    # OpenAI의 챗봇 모델을 사용하여 대화 완성 생성
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": user.substitute(input=event)
            }
        ],
        model=model_name,
    )

    # 생성된 대화의 첫 번째 메시지 내용을 반환
    return chat_completion.choices[0].message.content
```

##### 2-2 사용자의 입력을 주어진 포맷에 맞춰 일정 생성하기


아래 코드는 사용자의 자연어 입력을 받아 특정 포맷의 일정 정보로 변환하는 AI 비서의 기능을 구현합니다. `string.Template`을 사용하여 사용자 입력을 포맷에 맞게 변환하는 템플릿을 생성합니다. 사용자로부터 받은 일정 정보(`sample_event`)는 `response_from_llm` 함수를 통해 처리되며, 이 함수는 사용자의 요청(`system_event_prompt`)과 템플릿(`user_event_prompt`)을 기반으로 일정 정보를 생성합니다. 최종적으로 생성된 일정 정보는 출력됩니다.



```python
from string import Template

system_event_prompt = """
너는 사용자의 요청을 받아서 일정 변경 및 예약을 도와주는 AI 비서야.
주어진 포맷에 맞춰서 일정을 입력해줘.
"""

user_event_prompt = Template("""
사용자의 입력을 다음 포마트에 맞춰서 변경해줘.
만약 년도가 없다면, 2024년으로 간주해도 무방해.
아래 포맷 이외의 결과는 출력하면 안돼.


{
    "summary": "일정 제목",
    "location": "일정 장소",
    "description": "일정 설명",
    "start": {
        "dateTime": "xxxx-xx-xxTxx:xx:xx",
        "timeZone": "Asia/Seoul"
    },
    "end": {
        "dateTime": "xxxx-xx-xxTxx:xx:xx",
        "timeZone": "Asia/Seoul"
    }
}

입력: $input
""")


sample_event = """
강남역에서 8월 22일 19시부터 21시까지 AI 모임을 잡아줘. 그리고 노트북을 지참해야해
"""

result = response_from_llm(sample_event, system_event_prompt, user_event_prompt)
print(result)
```

<pre>
{
    "summary": "AI 모임",
    "location": "강남역",
    "description": "노트북을 지참해야함",
    "start": {
        "dateTime": "2024-08-22T19:00:00",
        "timeZone": "Asia/Seoul"
    },
    "end": {
        "dateTime": "2024-08-22T21:00:00",
        "timeZone": "Asia/Seoul"
    }
}
</pre>
##### 2-3 json 문자열을 객체로 만들어 일정 등록하기


아래 코드는 문자열 형태의 JSON 데이터를 파싱하여 Python 객체로 변환합니다. 성공적으로 변환되면 해당 객체를 반환하고, 변환 과정에서 `json.JSONDecodeError` 예외가 발생하면 에러 메시지를 출력한 후 `None`을 반환합니다. 함수는 `load_json`이라 명명되어 있으며, 이는 입력된 문자열이 유효한 JSON 형식인지 검증하고, 그 결과를 반환하는 역할을 합니다. 사용자는 이 함수를 통해 JSON 데이터의 로딩 및 에러 핸들링을 손쉽게 수행할 수 있습니다.



```python
import json 

# 주어진 텍스트에서 JSON을 로드하는 함수
def load_json(text):
    try:
        # 텍스트를 JSON으로 변환
        event = json.loads(text)
        return event
    except json.JSONDecodeError as e:
        # JSON 디코딩 중 발생한 에러를 출력
        print(f"JSON 디코딩 에러: {e}")
        return None
    
# 결과 문자열에서 JSON 객체를 로드
event = load_json(result)
```

`google_calendar.set_google_calendar(event)` 함수는 Google 캘린더에 주어진 `event`를 설정합니다. 이 함수는 `google_calendar` 객체의 메서드로, 특정 이벤트를 Google 캘린더에 추가하는 기능을 수행합니다.



```python
google_calendar.set_google_calendar(event) # Google 캘린더에 이벤트를 설정합니다.
```

##### 2-3 일정 예약 기능 추가하기


아래 코드는 사용자의 입력에 따라 인공지능 챗봇이 수행할 작업을 분류하고, 해당 작업에 대한 결과를 반환하는 방식을 설명합니다. `Template` 클래스를 사용하여 사용자의 작업 유형과 예시를 동적으로 포함하는 문자열 템플릿을 생성합니다. 이 템플릿은 사용자가 요청할 수 있는 세 가지 작업 유형(`오늘 일정 가져오기`, `일정 id 목록 가져오기`, `일정 추가하기`)과 각 작업에 대한 예상 응답(`today`, `list`, `add`)을 설명합니다. 마지막으로, `substitute` 메소드를 사용하여 사용자의 구체적인 요청(`오늘의 일정을 알려줘.`)을 템플릿에 삽입하고, 이를 출력하여 실제 사용 사례를 보여줍니다.



```python
from string import Template

# 사용자의 작업을 분류해서 해당하는 기능을 수행하는 인공지능 챗봇에 대한 설명
system_task_prompt = """
너는 사용자의 작업을 분류해서 해당하는 기능을 수행하는 인공지능 챗봇이야
"""

# 사용자의 작업 유형과 예시를 설명하는 템플릿
user_task_prompt = Template("""
사용자의 작업은 다음과 같이 3가지 종류가 있어.

1. 오늘 일정 가져오기
2. 일정 id 목록 가져오기
3. 일정 추가하기

사용자의 작업을 받아서 해당하는 작업과 관련된 결과를 반환해줘.
결과는 today, list, add 만 응답해야돼.

---
예시)

작업 : 오늘 처리해야 하는 일정을 알려줘.
today

작업 : 일정 id 목록을 알려줘.
list

작업 : 강남역에서 8월 15일 10시부터 11시까지 회의 일정을 잡아줘.
add

---

작업 : $input

"""
)

# 사용자 입력에 따른 작업 유형 예시 출력
print(user_task_prompt.substitute(input="오늘의 일정을 알려줘."))
```

<pre>

사용자의 작업은 다음과 같이 3가지 종류가 있어.

1. 오늘 일정 가져오기
2. 일정 id 목록 가져오기
3. 일정 추가하기

사용자의 작업을 받아서 해당하는 작업과 관련된 결과를 반환해줘.
결과는 today, list, add 만 응답해야돼.

---
예시)

작업 : 오늘 처리해야 하는 일정을 알려줘.
today

작업 : 일정 id 목록을 알려줘.
list

작업 : 강남역에서 8월 15일 10시부터 11시까지 회의 일정을 잡아줘.
add

---

작업 : 오늘의 일정을 알려줘.


</pre>
아래 코드는 이벤트를 처리하여 Google 캘린더와 상호작용하는 기능을 제공합니다. 사용자의 요청(`event`)을 받아 `response_from_llm` 함수를 통해 처리 결과를 얻습니다. 결과가 `list`, `add`, `today` 중 하나가 아니면 유효하지 않은 결과로 간주하고 `None`을 반환합니다. `today` 결과는 오늘의 일정을 가져오는 기능을, `list` 결과는 일정 ID 목록을 가져오는 기능을, `add` 결과는 새로운 일정을 추가하는 기능을 수행합니다. 각 기능은 `google_calendar` 객체의 메서드를 호출하여 구현됩니다.



```python
def calendar_process(event):
    # 이벤트에 대한 응답을 얻습니다.
    result = response_from_llm(event, system_task_prompt, user_task_prompt)
    print(result)
    
    # 결과가 유효한 명령어가 아닌 경우
    if result not in ['list', 'add', 'today']:
        print(f"유효하지 않은 결과입니다 : {result}")
        return None

    # 오늘의 일정을 가져오는 경우
    if result == 'today':
        print("오늘의 일정을 가져오는 기능을 수행합니다.")
        return google_calendar.get_today_events()
    # 일정 목록을 가져오는 경우
    elif result == 'list':
        print("일정 id 목록을 가져오는 기능을 수행합니다.")
        return google_calendar.get_event_id_list()
    # 일정을 추가하는 경우
    elif result == 'add':
        print("일정 추가하기 기능을 수행합니다.")
        result = response_from_llm(event, system_event_prompt, user_event_prompt)
        result = load_json(result)
        google_calendar.set_google_calendar(result)
```

아래 코드는 문자열 인자를 받아, 해당 문자열 내의 정보(장소, 날짜, 시간)를 분석하여 캘린더에 회의 일정을 등록합니다. 예를 들어, `"장소를 강냠역으로 하고, 8월 15일 오후 9시부터 10시까지 회의 일정을 등록해줘"`와 같은 문자열이 주어지면, 이를 분석하여 적절한 날짜와 시간에 회의 일정을 캘린더에 추가합니다.



```python
print(calendar_process("장소를 강냠역으로 하고, 8월 15일 오후 9시부터 10시까지 회의 일정을 등록해줘")) # 주어진 문자열 정보를 사용하여 캘린더에 회의 일정을 등록하는 함수를 호출
```

<pre>
add
일정 추가하기 기능을 수행합니다.
None
</pre>
아래 코드는 사용자로부터 "오늘의 일정을 알려줘"라는 입력을 받아, 해당 요청을 처리하는 `calendar_process` 함수를 호출합니다. `calendar_process` 함수는 입력된 문자열에 따라 오늘의 일정 정보를 반환하는 역할을 합니다.



```python
# 오늘의 일정을 알려주는 함수를 호출합니다.
print(calendar_process("오늘의 일정을 알려줘"))
```

<pre>
today
오늘의 일정을 가져오는 기능을 수행합니다.
{'kind': 'calendar#events', 'etag': '"p32s8j2fnkjioe0o"', 'summary': 'Anthony.Kim', 'description': '', 'updated': '2024-08-08T11:27:12.803Z', 'timeZone': 'Asia/Seoul', 'accessRole': 'owner', 'defaultReminders': [{'method': 'popup', 'minutes': 30}, {'method': 'email', 'minutes': 30}], 'items': [{'kind': 'calendar#event', 'etag': '"3445742677826000"', 'id': 'as54jmud22b8te3bo4b6ijeh9k', 'status': 'confirmed', 'htmlLink': 'https://www.google.com/calendar/event?eid=YXM1NGptdWQyMmI4dGUzYm80YjZpamVoOWsgamlraW1lQG0', 'created': '2024-08-05T15:22:18.000Z', 'updated': '2024-08-05T15:22:18.913Z', 'summary': 'langchain 모임', 'description': 'LLM 모임', 'location': '옐로스톤 스터디룸', 'creator': {'email': 'jikime@gmail.com', 'self': True}, 'organizer': {'email': 'jikime@gmail.com', 'self': True}, 'start': {'dateTime': '2024-08-08T19:00:00+09:00', 'timeZone': 'Asia/Seoul'}, 'end': {'dateTime': '2024-08-08T21:00:00+09:00', 'timeZone': 'Asia/Seoul'}, 'iCalUID': 'as54jmud22b8te3bo4b6ijeh9k@google.com', 'sequence': 0, 'reminders': {'useDefault': True}, 'eventType': 'default'}]}
</pre>
아래 코드는 `calendar_process`는 문자열 인자를 받아 처리하며, 이 예제에서는 "일정 id 목록 10개만 가져와줘"라는 요청을 처리합니다. 이 함수의 정확한 작동 방식은 코드만으로는 명확하지 않으나, 주어진 문자열에 따라 일정 관련 정보를 처리하는 것으로 추정됩니다.



```python
# 일정 id 목록 10개만 가져오는 함수 호출
print(calendar_process("일정 id 목록 10개만 가져와줘"))
```

<pre>
list
일정 id 목록을 가져오는 기능을 수행합니다.
['_8h1jig9o64rk8b9h64o32b9k74o48b9o6crj4b9h6p2j4dq2612j0c1m70', 'as54jmud22b8te3bo4b6ijeh9k', '_6kqj4h9i88q4cb9i61242b9k88r44b9p65146b9m8oq32d9l6gq48ghm6c', '_8kp42gq16gr4aba46grjgb9k8d0k2ba28h348ba36l234ca16h0jcci668', 'tm54c8quf1mt99cdqt0184nf64', 'ec48ehui8kh49dnmkthi45bm7o']
</pre>