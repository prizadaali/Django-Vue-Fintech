"""
Core views for shared functionality.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import connection
from .utils import create_api_response


class HealthCheckView(APIView):
    """
    Health check endpoint for monitoring application status.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Return application health status."""
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            health_data = {
                "status": "healthy",
                "database": "connected",
                "version": "1.0.0"
            }
            
            return Response(
                create_api_response(
                    data=health_data,
                    message="Application is healthy"
                ),
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            health_data = {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
            
            return Response(
                create_api_response(
                    data=health_data,
                    message="Application health check failed",
                    success=False
                ),
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )