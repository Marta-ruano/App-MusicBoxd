import logging


logger = logging.getLogger("musicboxd_api")
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler("api.log", encoding="utf-8")

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s "
        "[trace_id=%(otelTraceID)s span_id=%(otelSpanID)s]: %(message)s",
        defaults={"otelTraceID": "0" * 32, "otelSpanID": "0" * 16}
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)