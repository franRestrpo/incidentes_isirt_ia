"""
Utilidades para el procesamiento de texto en servicios de IA.
"""


def sanitize_for_prompt(text: str) -> str:
    """Escapa caracteres potencialmente peligrosos para la inyección de prompts."""
    if not isinstance(text, str):
        return ""
    # Usar dobles barras para representar una barra literal y evitar SyntaxWarning
    text = text.replace("`", "\\`")
    text = text.replace("'''", "\\'''")
    text = text.replace('"""', '\"""')
    return text