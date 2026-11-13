"""Errores de la API según docs/contrato_api_json.md (sección 2)."""
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, details: list[dict[str, str]] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or []


class SolicitudInvalidaError(AppError):
    status_code = 400
    code = "INVALID_REQUEST"


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppError):
    status_code = 409
    code = "DUPLICATE_RESOURCE"


class ValidacionError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


def _cuerpo(code: str, message: str, details: list[dict[str, str]] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


def _mensaje(e: dict[str, Any]) -> str:
    ctx = e.get("ctx") or {}
    tipo = e["type"]
    if tipo == "missing":
        return "Este campo es obligatorio."
    if tipo == "greater_than_equal":
        return f"Debe ser un número mayor o igual a {ctx.get('ge')}."
    if tipo == "greater_than":
        return f"Debe ser un número mayor que {ctx.get('gt')}."
    if tipo == "less_than_equal":
        return f"Debe ser un número menor o igual a {ctx.get('le')}."
    if tipo == "less_than":
        return f"Debe ser un número menor que {ctx.get('lt')}."
    if tipo == "string_too_short":
        return f"Debe tener al menos {ctx.get('min_length')} caracteres."
    if tipo == "string_too_long":
        return f"No puede superar los {ctx.get('max_length')} caracteres."
    if tipo in ("int_parsing", "int_type", "int_from_float"):
        return "Debe ser un número entero."
    if tipo in ("float_parsing", "float_type"):
        return "Debe ser un número."
    if tipo == "string_type":
        return "Debe ser un texto."
    if tipo == "json_invalid":
        return "El cuerpo de la solicitud no es un JSON válido."
    if tipo == "value_error":
        return e["msg"].removeprefix("Value error, ")
    return e["msg"]


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_cuerpo(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        errores = exc.errors()
        detalles = [
            {"field": ".".join(str(p) for p in e["loc"][1:]), "message": _mensaje(e)}
            for e in errores
        ]
        # Cuerpo inválido -> 422; parámetros de ruta/consulta inválidos -> 400
        if any(e["loc"] and e["loc"][0] == "body" for e in errores):
            return JSONResponse(
                status_code=422,
                content=_cuerpo("VALIDATION_ERROR", "Hay campos que requieren corrección.", detalles),
            )
        return JSONResponse(
            status_code=400,
            content=_cuerpo("INVALID_REQUEST", "La solicitud contiene parámetros inválidos.", detalles),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == 404:
            code, msg = "NOT_FOUND", "El recurso solicitado no existe."
        else:
            code, msg = "INVALID_REQUEST", "La solicitud no es válida."
        return JSONResponse(
            status_code=exc.status_code,
            content=_cuerpo(code, msg),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(Exception)
    async def _inesperado(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=_cuerpo("INTERNAL_ERROR", "Ocurrió un error inesperado."),
        )