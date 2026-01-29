import os
import base64
from smolagents import CodeAgent, MCPClient
from contextlib import ExitStack
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from openinference.instrumentation import using_session, using_user


def setup_smolagents_instrumentation(session_id: str = None, user_id: str = None, tracing_enabled: bool = False):
    """Configures OpenTelemetry and OpenInference for smolagents (Langfuse)."""
    # otel_env = os.getenv("ENABLE_OPEN_TELEMETRY", "false").lower()
    # tracing_enabled = otel_env in ("true", "1", "t", "yes")

    if tracing_enabled:
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            # Construct Auth header if not present (Basic Auth with PK:SK)
            if "OTEL_EXPORTER_OTLP_HEADERS" not in os.environ:
                pk = os.getenv("LANGFUSE_PUBLIC_KEY")
                sk = os.getenv("LANGFUSE_SECRET_KEY")
                auth = f"{pk}:{sk}"
                auth_b64 = base64.b64encode(auth.encode()).decode()
                os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth_b64}"

            attributes = {}

            resource = Resource(attributes=attributes) if attributes else None
            trace_provider = TracerProvider(resource=resource)

            # Default Langfuse OTLP endpoint if not set
            endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "https://cloud.langfuse.com/api/public/otel/v1/traces")
            trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
            SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)
            print(f"--- smolagents instrumentation enabled (Langfuse) [Session: {session_id}, User: {user_id}] ---")
            return
        else:
            print(f"--- smolagents: Langfuse not properly configured [Session: {session_id}, User: {user_id}] ---")


def get_agent(model_object, tools=None, system_prompt=None):
    if tools is None:
        tools = []

    try:
        verbosity_level = int(os.getenv("SMOLAGENTS_LOG_LEVEL", "1"))
    except ValueError:
        verbosity_level = 1

    kwargs = {
        "tools": tools,
        "model": model_object,
        "additional_authorized_imports": ["json", "datetime", "math"],
        "verbosity_level": verbosity_level
    }
    if system_prompt:
        kwargs["system_prompt"] = system_prompt

    return CodeAgent(**kwargs)


def get_mcp_tools(server_urls: list[str]):
    mcp_servers = [{"url": url} for url in server_urls]
    try:
        client = MCPClient(mcp_servers, structured_output=True)
        tools = client.get_tools()
        print(f"[Factory] Connected to MCP servers: {server_urls}. Found {len(tools)} tools.")
        return client, tools
    except Exception as e:
        print(f"[Factory] MCP Connection Error: {e}")
        return None, []


def run_agent_with_context(agent, task: str, session_id: str = None, user_id: str = None):
    with ExitStack() as stack:
        if session_id:
            stack.enter_context(using_session(session_id))
        if user_id:
            stack.enter_context(using_user(user_id))
        return agent.run(task)
