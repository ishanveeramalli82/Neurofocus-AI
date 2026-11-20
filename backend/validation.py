import datetime as dt
import re


class ValidationError(ValueError):
    pass


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def text(d, key, *, required=False, max_len=200, default=""):
    v = d.get(key, default)
    if v is None:
        v = default
    if not isinstance(v, str):
        raise ValidationError(f"{key} must be text")
    v = v.strip()
    if required and not v:
        raise ValidationError(f"{key} is required")
    if len(v) > max_len:
        raise ValidationError(f"{key} must be at most {max_len} characters")
    return v


def choice(d, key, options, default):
    v = d.get(key, default)
    if v not in options:
        raise ValidationError(f"{key} must be one of: {', '.join(options)}")
    return v


def integer(d, key, *, lo, hi, default=None, required=False):
    v = d.get(key, default)
    if v is None or v == "":
        if required:
            raise ValidationError(f"{key} is required")
        return default
    try:
        v = int(v)
    except (TypeError, ValueError):
        raise ValidationError(f"{key} must be a whole number")
    if not lo <= v <= hi:
        raise ValidationError(f"{key} must be between {lo} and {hi}")
    return v


def local_datetime(d, key, *, required=False):
    """Accepts 'YYYY-MM-DDTHH:MM' (local wall-clock time, as from <input type=datetime-local>)."""
    v = d.get(key)
    if not v:
        if required:
            raise ValidationError(f"{key} is required")
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(v))
    except ValueError:
        raise ValidationError(f"{key} must be a date and time")
    return parsed.replace(tzinfo=None, second=0, microsecond=0).isoformat(timespec="minutes")


def email(d, key="email"):
    v = text(d, key, required=True, max_len=254).lower()
    if not EMAIL_RE.match(v):
        raise ValidationError("Enter a valid email address")
    return v


def password(d, key="password"):
    v = d.get(key)
    if not isinstance(v, str) or len(v) < 10:
        raise ValidationError("Password must be at least 10 characters")
    if len(v) > 200:
        raise ValidationError("Password is too long")
    if v.isalpha() or v.isdigit():
        raise ValidationError("Password must mix letters with numbers or symbols")
    return v


def date(d, key, *, label=None, required=False):
    """Accepts 'YYYY-MM-DD'. Returns the same string, or None if optional and empty."""
    v = d.get(key)
    if not v:
        if required:
            raise ValidationError(f"{label or key} is required")
        return None
    try:
        return dt.date.fromisoformat(str(v)).isoformat()
    except ValueError:
        raise ValidationError(f"{label or key} must be a date")
