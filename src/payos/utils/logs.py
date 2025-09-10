import logging
import os
from typing import Optional, Union

from typing_extensions import override

logger: logging.Logger = logging.getLogger("payos")
httpx_logger: logging.Logger = logging.getLogger("httpx")

SENSITIVE_HEADERS = {"x-client-id", "x-api-key", "authorization", "cookie", "set-cookie"}


def setup_logging(level: Optional[Union[str, int]] = None) -> None:
    log_level: int
    if level is not None:
        if isinstance(level, str):
            log_level = getattr(logging, level.upper(), logging.WARNING)
        else:
            log_level = level
        if not logging.getLogger().handlers:
            logging.basicConfig(
                format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
    else:
        env = os.getenv("PAYOS_LOG")
        if env == "debug":
            log_level = logging.DEBUG
            if not logging.getLogger().handlers:
                logging.basicConfig(
                    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
        elif env == "info":
            log_level = logging.INFO
            if not logging.getLogger().handlers:
                logging.basicConfig(
                    format="[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
        else:
            log_level = logging.WARNING

    logger.setLevel(log_level)
    httpx_logger.setLevel(log_level)


setup_logging()


class SensitiveHeadersFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        if (
            isinstance(record.args, dict)
            and "headers" in record.args
            and isinstance(record.args["headers"], dict)
        ):
            headers = record.args["headers"] = {**record.args["headers"]}
            for header in headers:
                if str(header).lower() in SENSITIVE_HEADERS:
                    headers[header] = "<redacted>"
        return True
