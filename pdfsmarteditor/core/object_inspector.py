import fitz

from .exceptions import InvalidOperationError


class ObjectInspector:
    def __init__(self, document):
        if document is None:
            raise InvalidOperationError("Document is None")
        self.document = document

    def get_page_count(self):
        return len(self.document)

    def get_page(self, page_num: int):
        if page_num < 0 or page_num >= self.get_page_count():
            raise InvalidOperationError(f"Invalid page number: {page_num}")
        return self.document[page_num]

    def get_text_blocks(self, page_num: int):
        page = self.get_page(page_num)
        return page.get_text("dict")["blocks"]

    def get_images(self, page_num: int):
        page = self.get_page(page_num)
        return page.get_images(full=True)

    def get_annotations(self, page_num: int):
        page = self.get_page(page_num)
        return list(page.annots())

    def get_fonts(self, page_num: int):
        """Get list of fonts used on the page."""
        page = self.get_page(page_num)
        return page.get_fonts()

    def get_links(self, page_num: int):
        """Get list of links on the page."""
        page = self.get_page(page_num)
        return list(page.get_links())

    def inspect_object_tree(self, max_pages=None):
        """
        Inspect object tree for pages. For performance on large PDFs,
        limit with max_pages parameter.
        """
        tree = {}
        page_count = self.get_page_count()
        pages_to_check = (
            range(min(max_pages, page_count)) if max_pages else range(page_count)
        )
        for i in pages_to_check:
            tree[f"page_{i}"] = {
                "text_blocks": len(self.get_text_blocks(i)),
                "images": len(self.get_images(i)),
                "annotations": len(self.get_annotations(i)),
            }
        return tree
