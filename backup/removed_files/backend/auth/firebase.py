import pyotp
import qrcode
import io
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient

from backend.config import settings

# — initialize Firebase Admin SDK —
cred = credentials.Certificate(settings.FIREBASE_CERT_PATH)
firebase_admin.initialize_app(cred)

# — MongoDB for storing each user’s TOTP secret and 2FA status —
client = MongoClient(settings.MONGODB_URI)
db = client[settings.MONGODB_DB_NAME]
_users = db["users"]

# — HTTPBearer to pull the Firebase JWT from Authorization header —
bearer_scheme = HTTPBearer()

def verify_firebase_token(
    cred: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """Validate incoming Firebase ID token and return its payload."""
    try:
        decoded = firebase_auth.verify_id_token(cred.credentials)
    except Exception:
        raise HTTPException(401, "Invalid or expired Firebase token")
    return decoded  # contains uid, email, etc.

def require_2fa(user=Depends(verify_firebase_token)):
    """Ensure user has completed TOTP; or if not setup, block."""
    rec = _users.find_one({"uid": user["uid"]})
    if not rec or not rec.get("totp_enabled", False):
        raise HTTPException(403, "2FA not enabled for this account")
    return user

def setup_2fa(user=Depends(verify_firebase_token)):
    """
    Generate a new TOTP secret for this user and return a QR-code PNG.
    Frontend can render this to let the user scan into Google Authenticator.
    """
    uid = user["uid"]
    secret = pyotp.random_base32()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.get("email", uid),
        issuer_name="EchoMarket"
    )
    # store in DB, but don’t mark enabled until verified
    _users.update_one(
        {"uid": uid},
        {"$set": {"totp_secret": secret, "totp_enabled": False}},
        upsert=True
    )
    # build QR code image
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()  # return raw PNG bytes

def verify_2fa_code(code: str, user=Depends(verify_firebase_token)):
    """
    Verify the one-time code. On success, mark 2FA enabled.
    """
    rec = _users.find_one({"uid": user["uid"]})
    if not rec or "totp_secret" not in rec:
        raise HTTPException(400, "2FA not initialized")
    totp = pyotp.TOTP(rec["totp_secret"])
    if not totp.verify(code):
        raise HTTPException(401, "Invalid 2FA code")
    _users.update_one({"uid": user["uid"]}, {"$set": {"totp_enabled": True}})
    return {"status": "2FA enabled"}
