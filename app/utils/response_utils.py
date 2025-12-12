"""
Response utilities for standardized API responses.
Provides consistent response formatting across all endpoints.
"""

from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from fastapi import status


class ResponseUtils:
    """
    Utility class for creating standardized API responses.
    Ensures consistent response structure across the application.
    """
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """
        Create a standardized success response.
        
        Args:
            data: Response data (can be dict, list, or any JSON-serializable object)
            message: Success message
            status_code: HTTP status code
            
        Returns:
            JSONResponse with standardized format
        """
        response_body = {
            "success": True,
            "message": message,
            "data": data
        }
        
        return JSONResponse(
            status_code=status_code,
            content=response_body
        )
    
    @staticmethod
    def error_response(
        message: str = "An error occurred",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            errors: Optional additional error details
            
        Returns:
            JSONResponse with standardized error format
        """
        response_body = {
            "success": False,
            "message": message
        }
        
        if errors:
            response_body["errors"] = errors
        
        return JSONResponse(
            status_code=status_code,
            content=response_body
        )
    
    @staticmethod
    def created_response(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> JSONResponse:
        """
        Create a standardized 201 Created response.
        
        Args:
            data: Created resource data
            message: Success message
            
        Returns:
            JSONResponse with 201 status code
        """
        return ResponseUtils.success_response(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED
        )
    
    @staticmethod
    def not_found_response(
        message: str = "Resource not found"
    ) -> JSONResponse:
        """
        Create a standardized 404 Not Found response.
        
        Args:
            message: Not found message
            
        Returns:
            JSONResponse with 404 status code
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def conflict_response(
        message: str = "Resource already exists"
    ) -> JSONResponse:
        """
        Create a standardized 409 Conflict response.
        
        Args:
            message: Conflict message
            
        Returns:
            JSONResponse with 409 status code
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=status.HTTP_409_CONFLICT
        )
    
    @staticmethod
    def unauthorized_response(
        message: str = "Unauthorized"
    ) -> JSONResponse:
        """
        Create a standardized 401 Unauthorized response.
        
        Args:
            message: Unauthorized message
            
        Returns:
            JSONResponse with 401 status code
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden_response(
        message: str = "Forbidden"
    ) -> JSONResponse:
        """
        Create a standardized 403 Forbidden response.
        
        Args:
            message: Forbidden message
            
        Returns:
            JSONResponse with 403 status code
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )
