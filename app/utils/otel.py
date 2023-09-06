import os

from opentelemetry import trace
# from opentelemetry.exporter.otlp.exporter import OTLPSpanExporter

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# from opentelemetry.exporter.jaeger import JaegerSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


api_token = os.environ["AXIOM_API_TOKEN"]
org_id = os.environ["AXIOM_ORG_ID"]
env = os.getenv("ENV", "LOCAL")

service_name = f"backend-srv-{env.lower()}"

resource = Resource(attributes={"service.name": service_name, "env": env})

# Create a TracerProvider and configure it to use the OTLP exporter
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)


# Determine which exporter to use based on the environment
if env.lower() == "local":
    # Instantiate Jaeger exporter for the local environment
    jaeger_exporter = JaegerExporter(
        # service_name=service_name,
        agent_host_name="localhost",
        agent_port=6831,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
else:
    # Instantiate OTLP exporter for other environments
    otlp_exporter = OTLPSpanExporter(
        endpoint="https://api.axiom.co/v1/traces",
        headers={
            "Authorization": f"Bearer {api_token}",
            "X-Axiom-Dataset": "traces",
        },
    )
    span_processor = BatchSpanProcessor(otlp_exporter)

# Add the span processor to the tracer provider
trace.get_tracer_provider().add_span_processor(span_processor)
