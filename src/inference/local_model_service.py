import os
import subprocess
import time
from typing import Optional, Dict, Any, List
import httpx


class LocalModelService:
    """
    Isolated Model Service adapter for local llama.cpp-compatible inference sidecar.
    Handles communication with local server via HTTP and optional child-process management.
    Never crashes the application if the model is unreachable.
    """

    def __init__(
        self,
        server_url: Optional[str] = "http://127.0.0.1:8080",
        binary_path: Optional[str] = None,
        model_path: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.server_url = (server_url or "http://127.0.0.1:8080").rstrip("/")
        self.binary_path = binary_path
        self.model_path = model_path
        self.timeout = timeout
        self._process: Optional[subprocess.Popen] = None

    def start_sidecar(self) -> bool:
        """
        Attempts to start the local llama.cpp server if binary and model paths are valid.
        Returns True if started, False otherwise.
        """
        if not self.binary_path or not self.model_path:
            return False

        if not os.path.isfile(self.binary_path) or not os.path.isfile(self.model_path):
            return False

        try:
            # Check if server is already running
            if self.is_available_sync(timeout=1.0):
                return True

            cmd = [
                self.binary_path,
                "-m", self.model_path,
                "--host", "127.0.0.1",
                "--port", "8080",
                "-c", "2048",
            ]
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Give server up to 3 seconds to bind
            for _ in range(15):
                time.sleep(0.2)
                if self.is_available_sync(timeout=0.5):
                    return True
            return False
        except Exception:
            return False

    def stop_sidecar(self) -> None:
        """Terminate the sidecar process if managed by this instance."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2.0)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

    def is_available_sync(self, timeout: float = 1.0) -> bool:
        """Synchronous check if local model endpoint responds."""
        try:
            with httpx.Client(timeout=timeout) as client:
                res = client.get(f"{self.server_url}/health")
                if res.status_code == 200:
                    return True
                res = client.get(f"{self.server_url}/v1/models")
                return res.status_code == 200
        except Exception:
            return False

    async def is_available(self, timeout: float = 1.5) -> bool:
        """Asynchronous check if local model endpoint responds."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.get(f"{self.server_url}/health")
                if res.status_code == 200:
                    return True
                res = await client.get(f"{self.server_url}/v1/models")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.2,
    ) -> Optional[str]:
        """
        Sends generation request to local llama.cpp server.
        Tries OpenAI-compatible /v1/chat/completions first, falls back to /completion.
        Returns generated string if successful, None if unavailable or error.
        """
        sys_msg = system_prompt or "You are Crystal, a privacy-first edge AI running locally."

        # 1. Try /v1/chat/completions (standard OpenAI format for llama-server)
        chat_url = f"{self.server_url}/v1/chat/completions"
        chat_payload = {
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(chat_url, json=chat_payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content:
                            return content.strip()
        except Exception:
            pass

        # 2. Fallback to /completion (native llama.cpp endpoint)
        raw_url = f"{self.server_url}/completion"
        formatted_prompt = f"{sys_msg}\n\nUser: {prompt}\n\nAssistant:"
        raw_payload = {
            "prompt": formatted_prompt,
            "n_predict": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(raw_url, json=raw_payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("content", "")
                    if content:
                        return content.strip()
        except Exception:
            pass

        return None
