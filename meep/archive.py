import json
from typing import Any, Dict


def parse_twitter_data(content: bytes) -> Dict[str, Any]:
    start_index = content.index(b"[")
    end_index = content.rindex(b"]") + 1
    return json.loads(content[start_index:end_index])
