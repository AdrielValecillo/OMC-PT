import json
from decimal import Decimal

from google import genai
from google.genai import types

from app.core import get_settings

SYSTEM_PROMPT = """Eres un Analista de Ventas y Marketing Experto.
Tu objetivo es analizar los datos de los prospectos (leads) proporcionados y generar un resumen ejecutivo claro y conciso en español.
Identifica tendencias clave, la fuente más efectiva de captación, el presupuesto promedio y da breves recomendaciones estratégicas.
Mantén un tono profesional, directo y orientado a resultados. No inventes datos que no estén en la entrada."""


class AIConfigurationError(Exception):
    pass


class AIService:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.api_key_gemini
        if not self.api_key:
            raise AIConfigurationError("API_KEY_GEMINI no está configurada.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"

    def generate_leads_summary(self, leads_data: list[dict]) -> str:
        if not leads_data:
            return "No hay datos de leads para analizar con los filtros proporcionados."

        # Convert Decimal values to float for JSON serialization
        def custom_serializer(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

        data_str = json.dumps(leads_data, default=custom_serializer, indent=2, ensure_ascii=False)

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"Por favor analiza los siguientes datos de leads y genera un resumen ejecutivo:\n\n{data_str}"
                    ),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        )

        if not response.text:
            return "No se pudo generar un resumen."
            
        return response.text
