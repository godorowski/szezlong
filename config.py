from datetime import datetime
from django.db.models import Q

from beret_utils import get_config
from beret_utils import get_path_fun
from beret_utils.config import bool_value
from beret_utils.config import join_path_value

get_path = get_path_fun()


def split_hosts(hosts_txt: str):
    return hosts_txt.split()


DEFAULT_SETTINGS = (
    ("PORT", 8082, int),
    ("SECRET_KEY",),
    ("ALLOWED_HOSTS", '127.0.0.1', split_hosts)
)

# database settings
DEFAULT_SETTINGS += (
    ("POSTGRES_DB",),
    ("POSTGRES_USER", "admin"),
    ("POSTGRES_PASSWORD", "password"),
    ("POSTGRES_HOST", "localhost"),
    ("POSTGRES_PORT", 5432, int),
)

# celery settings
# rabbitmq as default broker
DEFAULT_SETTINGS += (
    ("CELERY_BROKER_URL", "amqp://localhost"),
)

# debugging settings
DEFAULT_SETTINGS += (
    ("DEBUG", 1, bool_value),

)

# i18n settings
DEFAULT_SETTINGS += (
    ("TZ", "Europe/Warsaw"),
    ("LANGUAGE_CODE", "pl"),
)

# static settings
DEFAULT_SETTINGS += (
    ("STATICFILES_DIRS", "static", get_path),
    ("WEBPACK_SLUG", "frontend"),
    ("FRONTEND_DIR", "frontend", get_path),
    ("WEBPACK_STATIC", "build", join_path_value("FRONTEND_DIR")),
    ("MANIFEST_FILE", "manifest.json", join_path_value("WEBPACK_STATIC")),
)

ENV_FILE = (
    '.local.env',
)

ConfigClass = get_config(DEFAULT_SETTINGS, ENV_FILE)
config = ConfigClass()


def expires(queryset):
    return queryset.filter(expiration_date__lte=datetime.now())


def attentions(queryset):
    return expires(queryset) \
        .filter(Q(oxygen=True) & Q(use_oxygen=False) & Q(bed__oxygen=False)) \
        .filter(Q(respirator=True) & Q(use_respirator=False) & Q(bed__respirator=False)) \
        .filter(Q(oxygen=False) & Q(use_oxygen=True) | Q(bed__oxygen=True)) \
        .filter(Q(respirator=True) & Q(use_respirator=False) & Q(bed__respirator=False))


def available(queryset):
    return queryset.filter(ticket__isnull=True, child=False)


def children_available(queryset):
    return queryset.filter(ticket__isnull=True, child=True)


if __name__ == '__main__':
    for key, value in config.items():
        print(f"{key}={value}")
