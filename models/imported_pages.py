from pydantic import BaseModel


class ImportedPages(BaseModel):
    page_ids: list
