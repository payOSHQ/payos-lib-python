import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from payos import PayOS, WebhookError

load_dotenv()

# To verify webhooks locally you need a public HTTPS endpoint. Use a tunneling tool like ngrok:
# 1. Install ngrok.
# 2. Start a tunnel to your Flask port (default 5000):
#       ngrok http 5000
# 3. Copy the generated HTTPS forwarding URL.
# 4. In your payOS dashboard, set the webhook URL to:
#       <NGROK_URL>/webhooks
#   or use `PayOS.webhooks.confirm('<NGROK_URL>/webhooks')`
# 5. Use the ngrok web UI to inspect and replay requests: http://127.0.0.1:4040
# Notes:
# - Ensure PAYOS_CLIENT_ID, PAYOS_API_KEY and PAYOS_CHECKSUM_KEY are set in your .env.
# - When reloading dev server, restart ngrok only if the public URL changes.

app = Flask(__name__)
client = PayOS(
    client_id=os.getenv("PAYOS_CLIENT_ID"),
    api_key=os.getenv("PAYOS_API_KEY"),
    checksum_key=os.getenv("PAYOS_CHECKSUM_KEY"),
)


@app.route("/webhooks", methods=["POST"])
def webhooks():
    data = request.get_data()

    try:
        webhook_data = client.webhooks.verify(data)
    except WebhookError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"error": None, "data": webhook_data.model_dump_camel_case()})


if __name__ == "__main__":
    app.run(port=int(os.getenv("PORT", 5000)), debug=True)
