import os
import httpx
import logging
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from agentic.application.portal_interface import IPortalApiClient

# Ensure environment variables are loaded
load_dotenv()

class PortalApiClient(IPortalApiClient):
    def __init__(self):
        self.base_url = os.getenv("PORTAL_API_BASE_URL", "http://localhost:5080")
        self.version = os.getenv("PORTAL_API_VERSION", "v1")
        # Persistent client for connection pooling
        self.client = httpx.AsyncClient(verify=False, timeout=30.0)
        # Simple in-memory cache: (endpoint, token) -> (timestamp, data)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes TTL
        print(f"DEBUG: PortalApiClient initialized with Base URL: {self.base_url}")

    async def _get(self, endpoint: str, token: str) -> Dict[str, Any]:
        cache_key = (endpoint, token)
        current_time = time.time()

        # Check cache
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if current_time - timestamp < self._cache_ttl:
                print(f"DEBUG: Returning CACHED data for {endpoint}")
                return data

        url = f"{self.base_url}/{self.version}/{endpoint}"
        
        # Headers MUST use the JWT Token
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        } 
        
        print(f"DEBUG: AI calling C# Portal -> {url}")
        
        try:
            response = await self.client.get(url, headers=headers)
            print(f"DEBUG: C# Response Status -> {response.status_code}")
            
            if response.status_code == 401:
                print("DEBUG: ERROR - 401 Unauthorized. The Token is invalid or expired.")
            
            response.raise_for_status()
            data = response.json()
            
            # Update cache
            self._cache[cache_key] = (current_time, data)
            return data
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
