import os
from datetime import datetime, timezone, timedelta
from uuid import UUID

import pyotp
import qrcode
from dotenv import load_dotenv
from jose import jwt
from qrcode.image.svg import SvgImage
import app.constants as c
from app.models.models import Users

load_dotenv()


class AuthService:
    def generate_access_token (self, user_id: UUID) -> str:
        to_encode = {
            "user_id": str (user_id),
        }
        expire = datetime.utcnow () + timedelta (minutes=60)
        to_encode.update ({"exp": expire})
        encoded_jwt = jwt.encode (to_encode, os.getenv ('SECRET_KEY'), algorithm=c.ALGORITHM)
        return encoded_jwt

    def generate_qr_code (self, totp_auth: str, email):
        directory = "app/qr_codes"
        if not os.path.exists (directory):
            os.makedirs (directory)

        qr = qrcode.QRCode (
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data (self, totp_auth)
        qr.make(fit=True)
        img = qr.make_image (fill_color="black", back_color="white", image_factory=SvgImage)
        file = f"qr_{email}.svg"
        with open(f"app/qr_codes/{file}", "wb") as f:
            f.write(img.to_string ())
        return img

    def google_2f_auth(self, user: Users):
        totp_auth: str = pyotp.totp.TOTP(user.secret).provisioning_uri (
            name=user.email,
            issuer_name='BankSystem'
        )

        self.generate_qr_code(totp_auth, user.email)

    @staticmethod
    def verify_otp(otp: str, user: Users):
        token = pyotp.TOTP(user.secret).now()

        if otp != token:
            return False
        return True

