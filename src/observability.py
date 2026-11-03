import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.config import settings

tracer = trace.get_tracer("satzwerk")


def setup_observability(app: FastAPI) -> None:
    # Ensure LangSmith variables are accessible to LangChain if not already exported
    if settings.LANGCHAIN_TRACING_V2.lower() == "true" and settings.LANGCHAIN_API_KEY:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.LANGCHAIN_API_KEY)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.LANGCHAIN_PROJECT)

    traces_endpoint = (
        settings.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
        or settings.OTEL_EXPORTER_OTLP_ENDPOINT
    )

    if traces_endpoint:
        if not traces_endpoint.endswith("/v1/traces"):
            traces_endpoint = f"{traces_endpoint.rstrip('/')}/v1/traces"

        resource = Resource.create(
            {
                "service.name": settings.OTEL_SERVICE_NAME,
                "deployment.environment": settings.ENVIRONMENT,
            }
        )

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=traces_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
        HTTPXClientInstrumentor().instrument(tracer_provider=provider)
