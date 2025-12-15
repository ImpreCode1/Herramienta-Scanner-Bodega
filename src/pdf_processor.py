from collections import defaultdict
from loguru import logger
from barcode_reader import read_barcode

def split_by_barcode(images, report: dict):
    documents = defaultdict(list)
    current_code = "SIN_CODIGO"

    report["total_pages"] = len(images)

    for index, image in enumerate(images, start=1):
        try:
            code = read_barcode(image)

            if code:
                current_code = code
                logger.info(f"Página {index}: nuevo documento -> {code}")
            else:
                logger.debug(f"Página {index}: sin código")

            documents[current_code].append(image)

        except Exception as e:
            report["errors"].append(f"Página {index}: {e}")
            logger.error(f"Error en página {index}: {e}")

    report["total_documents"] = len(documents)
    report["documents_with_code"] = len(
        [k for k in documents.keys() if k != "SIN_CODIGO"]
    )
    report["documents_without_code"] = 1 if "SIN_CODIGO" in documents else 0

    return documents
