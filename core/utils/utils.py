from django.core.mail import EmailMessage
from django.conf import settings
import hmac, hashlib, time, base64, uuid, json
import requests


def send_notification(data):
    subject, emails, html_content = data.get('subject'), data.get('emails'), data.get('body')
    print('manager info: ', emails)
    msg = EmailMessage(subject, html_content, settings.EMAIL_HOST_USER, emails)
    msg.send()
    print('notification sent successfully')


class SMSClient:
    LOCAL_GSM_CODE = "994"

    POCT_GOYERCHINI_USERNAME = settings.POCT_GOYERCHINI_USERNAME
    POCT_GOYERCHINI_PASSWORD = settings.POCT_GOYERCHINI_PASSWORD
    POCT_GOYERCHINI_API = "http://www.poctgoyercini.com/api_http/sendsms.asp"

    SMS_GLOBAL_HOST = "api.smsglobal.com"
    SMS_GLOBAL_API_KEY = settings.SMS_GLOBAL_API_KEY
    SMS_GLOBAL_API_SECRET = settings.SMS_GLOBAL_API_SECRET
    SMS_GLOBAL_SENDER_NAME = settings.SMS_SENDER_NAME

    def send(self, phone_number: str, content: str) -> bool:
        if phone_number.startswith(self.LOCAL_GSM_CODE):
            status = self.send_local_sms(phone_number, content)
        else:
            status = self.send_global_sms(phone_number, content)
        return bool(status)

    def send_local_sms(self, phone_number, content):
        params = {
            "user": self.POCT_GOYERCHINI_USERNAME,
            "password": self.POCT_GOYERCHINI_PASSWORD,
            "gsm": phone_number,
            "text": content,
        }
        re = requests.request("POST", self.POCT_GOYERCHINI_API, params=params)
        return re.text[6:7]

    def get_global_authorization(
        self,
        method: str = "POST",
        uri: str = "/v2/sms/",
        port: int = 443,
        extra_data: str = "",
    ) -> str:
        timestamp = int(time.time())
        nonce = str(uuid.uuid4())
        raw_str = "%s\n%s\n%s\n%s\n%s\n%d\n%s\n" % (
            timestamp,
            nonce,
            method,
            uri,
            self.SMS_GLOBAL_HOST,
            port,
            extra_data,
        )

        raw_str = raw_str.encode()
        mac = hmac.new(
            self.SMS_GLOBAL_API_SECRET.encode(), raw_str, hashlib.sha256
        ).digest()
        mac = base64.b64encode(mac)

        return f'MAC id="{self.SMS_GLOBAL_API_KEY}", ts="{timestamp}", nonce="{nonce}", mac="{mac.decode()}"'

    def send_global_sms(self, phone_number: str, content: str) -> bool:
        url = "https://api.smsglobal.com/v2/sms/"
        data = {
            "message": content,
            "destination": phone_number,
            "origin": self.SMS_GLOBAL_SENDER_NAME,
        }
        headers = {
            "Content-type": "application/json",
            "Authorization": self.get_global_authorization(),
        }
        r = requests.post(url, json.dumps(data), headers=headers)
        return r.ok


SMS = SMSClient()


