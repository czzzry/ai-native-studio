"""Small standard-library HTTP endpoint for local webhook experiments."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .adapter import RecordingLinearAdapter
from .dedup import WebhookReceiptStore
from .role_config import load_product_agent_role
from .service import ProductAgentWebhookService


def _handler(service: ProductAgentWebhookService) -> type[BaseHTTPRequestHandler]:
    class ProductAgentRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/webhooks/linear":
                self.send_error(404, "Use POST /webhooks/linear")
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            result = service.handle(raw_body, dict(self.headers.items()))
            response = result.model_dump_json(by_alias=True).encode()

            self.send_response(result.http_status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: object) -> None:
            print(json.dumps({"client": self.client_address[0], "message": format % args}))

    return ProductAgentRequestHandler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument(
        "--secret",
        required=True,
        help="Synthetic local signing secret. Never use or paste a real Linear secret here.",
    )
    parser.add_argument(
        "--database",
        default="data/private/product_agent_proof.sqlite3",
        help="Local SQLite receipt ledger path.",
    )
    args = parser.parse_args()

    database = Path(args.database)
    database.parent.mkdir(parents=True, exist_ok=True)
    store = WebhookReceiptStore(database)
    service = ProductAgentWebhookService(
        secret=args.secret.encode(),
        role=load_product_agent_role(),
        receipt_store=store,
        linear_adapter=RecordingLinearAdapter(),
    )
    server = ThreadingHTTPServer((args.host, args.port), _handler(service))
    print(f"ProductAgent proof listening on http://{args.host}:{args.port}/webhooks/linear")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()


if __name__ == "__main__":
    main()
