import os
import httpx
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from agentic.application.portal_interface import IPortalApiClient

# Ensure environment variables are loaded
load_dotenv()

class PortalApiClient(IPortalApiClient):
    def __init__(self):
        self.base_url = os.getenv("PORTAL_API_BASE_URL", "http://localhost:5080")
        self.version = os.getenv("PORTAL_API_VERSION", "v1")
        print(f"DEBUG: PortalApiClient initialized with Base URL: {self.base_url}")

    async def _get(self, endpoint: str, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.version}/{endpoint}"
        
        # Headers MUST use the JWT Token
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        } 
        
        print(f"DEBUG: AI calling C# Portal -> {url}")
        
        # verify=False is used for local testing with self-signed certs
        # Increased timeout to 30s to handle slow C# backend responses
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            try:
                response = await client.get(url, headers=headers)
                print(f"DEBUG: C# Response Status -> {response.status_code}")
                
                if response.status_code == 401:
                    print("DEBUG: ERROR - 401 Unauthorized. The Token is invalid or expired.")
                
                response.raise_for_status()
                return response.json()
            except Exception as e:
                error_msg = str(e)
                print(f"DEBUG: API Error -> {error_msg}")
                return {"error": error_msg, "message": f"Could not retrieve data from {endpoint}"}

    async def get_profile(self, token: str) -> Dict[str, Any]:
        return await self._get("students/profile", token)

    async def get_dashboard(self, token: str) -> Dict[str, Any]:
        return await self._get("students/dashboard", token)

    async def get_ledger(self, token: str) -> Dict[str, Any]:
        return await self._get("students/my-ledger", token)

    async def get_payments(self, token: str) -> Dict[str, Any]:
        return await self._get("students/my-payments", token)
