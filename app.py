import os
import json
from openai import OpenAI

INPUT_FILE = "products_input.json"
OUTPUT_FILE = "products_output.json"

SCHEMA = {
  "type": "object",
  "properties": {
    "selected_products": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": ["string", "number", "null"]},
          "name": {"type": "string"}
        },
        "required": ["id", "name"],
        "additionalProperties": False
      }
    }
  },
  "required": ["selected_products"],
  "additionalProperties": False
}



def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        products = json.load(f)

    user_command = "食べられる商品を選択してください。"

    client = OpenAI()

    resp = client.responses.create(
        model="gpt-4.1-mini",
        instructions=(
            "あなたは厳格なJSON生成器です。"
            "スキーマに一致するJSONのみを返してください。"
            "判断に迷う場合は除外してください。"
        ),
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"COMMAND: {user_command}"},
                    {"type": "input_text", "text": "PRODUCTS_JSON:"},
                    {"type": "input_text", "text": json.dumps(products, ensure_ascii=False)},
                ],
            }
        ],
        # ✅ correct way (Responses API): text.format
        text={
            "format": {
                "type": "json_schema",
                "name": "product_selector",
                "schema": SCHEMA,
                "strict": True
            }
        }
    )

    result_obj = json.loads(resp.output_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result_obj, f, ensure_ascii=False, indent=2)

    print(f"OK: wrote {OUTPUT_FILE} ({len(result_obj['selected_products'])} items)")

if __name__ == "__main__":
    main()
