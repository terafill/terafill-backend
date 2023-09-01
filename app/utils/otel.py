import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


api_token = os.getenv("AXIOM_API_TOKEN")
org_id = os.getenv("AXIOM_ORG_ID")

resource = Resource(
    attributes={"service.name": "backend-srv", "env": os.getenv("ENV", "LOCAL")}
)

# Create a TracerProvider and configure it to use the OTLP exporter
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Set the OTLP exporter to use HTTP and point it to the Axiom URL
otlp_exporter = OTLPSpanExporter(
    endpoint="https://api.axiom.co/v1/traces",
    headers={
        "Authorization": f"Bearer {api_token}",
        "X-Axiom-Dataset": "traces",  # Add your dataset here
    },
)

# Configure the tracer to use the BatchSpanProcessor with the OTLP exporter
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
