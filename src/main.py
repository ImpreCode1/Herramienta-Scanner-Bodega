import sys
from pathlib import Path
from collections import defaultdict
from logger import logger
from image_converter import pdf_to_images
from pdf_processor import split_by_barcode
from utils.file_utils import save_pdf, sanitize_filename

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    if len(sys.argv) < 2:
        print("Uso: scanner.exe archivo1.pdf archivo2.pdf ...")
        sys.exit(1)

    pdf_files = sys.argv[1:]
    counters = defaultdict(int)

    global_report = {
        "total_pdfs": 0,
        "total_pages": 0,
        "total_documents": 0,
        "documents_with_code": 0,
        "documents_without_code": 0,
        "errors": []
    }

    for pdf_path in pdf_files:
        path = Path(pdf_path)

        if not path.exists():
            logger.error(f"No existe: {pdf_path}")
            continue

        logger.info(f"Procesando PDF: {pdf_path}")
        global_report["total_pdfs"] += 1

        report = {
            "total_pages": 0,
            "total_documents": 0,
            "documents_with_code": 0,
            "documents_without_code": 0,
            "errors": []
        }

        images = pdf_to_images(str(path))
        documents = split_by_barcode(images, report)

        global_report["total_pages"] += report["total_pages"]
        global_report["documents_with_code"] += report["documents_with_code"]
        global_report["documents_without_code"] += report["documents_without_code"]

        for code, imgs in documents.items():
            safe_code = sanitize_filename(code)
            counters[safe_code] += 1
            suffix = f"_{counters[safe_code]}" if counters[safe_code] > 1 else ""
            filename = f"factura_{safe_code}{suffix}.pdf"

            save_pdf(imgs, OUTPUT_DIR / filename)

    # REPORTE GLOBAL
    print("\n====== REPORTE GLOBAL ======")
    print(f"PDFs procesados: {global_report['total_pdfs']}")
    print(f"Páginas procesadas: {global_report['total_pages']}")
    print(f"Facturas detectadas: {global_report['documents_with_code']}")
    print(f"Facturas sin código: {global_report['documents_without_code']}")
    print(f"Errores: {len(global_report['errors'])}")
    print("============================\n")

    logger.info("Procesamiento múltiple finalizado.")

if __name__ == "__main__":
    main()
