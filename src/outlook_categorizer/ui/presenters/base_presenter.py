"""
Base presenter class for MVP pattern.
All presenters inherit from this to ensure consistent interface.
"""

from typing import Optional
from abc import ABC, abstractmethod


class BasePresenter(ABC):
    """Base class for all presenters in MVP pattern."""
    
    def __init__(self):
        """Initialize base presenter."""
        self._view = None
    
    def set_view(self, view):
        """Set the view this presenter manages."""
        self._view = view
    
    def get_view(self):
        """Get the view this presenter manages."""
        return self._view
    
    @abstractmethod
    def initialize(self):
        """Initialize presenter - called after view is set."""
        pass
    
    def cleanup(self):
        """Cleanup resources - called when presenter is destroyed."""
        pass

