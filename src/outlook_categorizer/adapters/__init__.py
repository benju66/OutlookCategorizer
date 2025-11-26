"""Adapters for external integrations."""

from .outlook_client import OutlookClient
from .config_loader import ConfigLoader
# EmailMessage is in core.models, not here
from ..core.models import EmailMessage

__all__ = ["OutlookClient", "EmailMessage", "ConfigLoader"]
