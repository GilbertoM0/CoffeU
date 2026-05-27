import glob
import logging
import os
from pathlib import Path

# --- Firebase Admin SDK ---
_firebase_app = None
logger = logging.getLogger(__name__)


def _get_firebase_credentials_path() -> str:
    """Obtiene la ruta al service account por variable de entorno o autodeteccion."""
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if cred_path:
        return cred_path

    base_dir = Path(__file__).resolve().parents[2]
    matches = glob.glob(str(base_dir / "*firebase-adminsdk*.json"))
    if matches:
        return matches[0]

    raise ValueError(
        "No se encontro archivo de credenciales Firebase. Configura FIREBASE_CREDENTIALS_PATH o agrega el JSON de service account en la raiz del proyecto."
    )


def _init_firebase():
    import firebase_admin
    from firebase_admin import credentials

    global _firebase_app
    if not firebase_admin._apps:
        cred_path = _get_firebase_credentials_path()
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)


def _normalizar_id_token(id_token: str) -> str:
    if not id_token or not isinstance(id_token, str):
        raise ValueError("El id_token es requerido")

    token = id_token.strip()

    # Soporta formatos comunes: 'Bearer <token>' o token entre comillas.
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1].strip()

    if token.startswith('"') and token.endswith('"'):
        token = token[1:-1].strip()

    if not token:
        raise ValueError("El id_token esta vacio")

    return token


def verificar_firebase_token(id_token: str) -> dict:
    """Verifica un ID token de Firebase y retorna el token decodificado."""
    from firebase_admin import auth as firebase_auth

    _init_firebase()
    token_limpio = _normalizar_id_token(id_token)
    try:
        decoded = firebase_auth.verify_id_token(token_limpio)
    except Exception as e:
        print(f"[Firebase DEBUG] tipo={type(e).__name__} | msg={e}")
        raise
    return decoded  # contiene: uid, phone_number, firebase.sign_in_provider, etc.


def _mask_email(email: str | None) -> str | None:
    if not email:
        return None
    try:
        local, domain = email.split("@", 1)
        if not local:
            return f"***@{domain}"
        return f"{local[0]}***@{domain}"
    except ValueError:
        return "***"


def _mask_phone(phone_number: str | None) -> str | None:
    if not phone_number:
        return None
    if len(phone_number) <= 4:
        return "***"
    return f"***{phone_number[-4:]}"


def validar_token_firebase(id_token: str) -> dict:
    """Valida ID token de Firebase y devuelve claims normalizados para autenticacion backend."""
    decoded = verificar_firebase_token(id_token)

    provider = (decoded.get("firebase") or {}).get("sign_in_provider")
    claims = {
        "uid": decoded.get("uid"),
        "email": decoded.get("email"),
        "phone_number": decoded.get("phone_number"),
        "sign_in_provider": provider,
        "decoded": decoded,
    }

    logger.info(
        "Firebase token verificado provider=%s uid=%s email=%s phone=%s",
        claims["sign_in_provider"],
        (claims["uid"] or "")[:8],
        _mask_email(claims["email"]),
        _mask_phone(claims["phone_number"]),
    )

    return claims
