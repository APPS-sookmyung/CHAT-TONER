"""
기본 서비스 클래스
모든 서비스의 공통 기능을 제공하는 베이스 클래스
"""

import logging
from abc import ABC


class BaseService(ABC):
    """Base class for all services"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
    
    def _log_error(self, message: str, exception: Exception = None):
        """Error logging helper method"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
        else:
            self.logger.error(message)
    
    def _log_info(self, message: str):
        """Info logging helper method"""
        self.logger.info(message)
    
    def _log_debug(self, message: str):
        """Debug logging helper method"""
        self.logger.debug(message)