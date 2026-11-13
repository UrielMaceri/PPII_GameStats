from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Atributos en snake_case en Python, camelCase en el JSON (contrato, sección 1)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)