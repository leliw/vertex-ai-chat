import logging
import uvicorn


def setup_logging():
    ch = logging.StreamHandler()
    ch.setFormatter(
        uvicorn.logging.DefaultFormatter("%(levelprefix)s %(name)s: %(message)s")
    )
    logging.getLogger().addHandler(ch)

    logging.getLogger("app").setLevel(logging.INFO)
    logging.getLogger("ampf").setLevel(logging.INFO)
    logging.getLogger("gcp").setLevel(logging.INFO)
