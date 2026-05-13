import httpx


class LLMClient:
    """
    Cliente mínimo para interactuar con un proveedor LLM real.
    Infraestructura pura: IO + errores.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        model: str,
        timeout: float = 10.0,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        response = httpx.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.0,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]