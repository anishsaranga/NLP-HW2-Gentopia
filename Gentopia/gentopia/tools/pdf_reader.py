# Importing required packages
from typing import *
import requests
from io import BytesIO
from pypdf import PdfReader
from gentopia.tools.basetool import BaseTool, BaseModel, Field

# required for pydantic validation
class ReadingPDFArgs(BaseModel):
    link: str = Field(..., description="a url to read pdf from")


class ReadingPDF(BaseTool):
    # below three fields are also required for pydantic validatins
    name = "pdf_reader"
    description = "a mini tool to read pdf files"
    args_schema: Optional[Type[BaseModel]] = ReadingPDFArgs
    text = ""

    # keeping a default url value, just in case it gets called without a link
    def _run(self, link="https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf"):

        response = requests.get(url=link)
        if response.status_code != 200:
            print("Error!! Unable to read pdf")
            return
        
        text = ""
        ### NIPS links are shortened versions, and to get exact pdf link I get the url from response instead
        if response.url != link:
            link = response.url
            response = requests.get(url=link)
        # handling NIPS abstract html landing page if found by the LLM agent
        NIPS = ["https://proceedings.neurips.cc/", "-Abstract.html"]
        # hash replace and ending replace
        try:
            if link.startswith(NIPS[0]) and link.endswith(NIPS[1]):
                link = link.replace("hash", "file")
                link = link.replace(NIPS[1], "-Paper.pdf")
                # replaced link -> get response again
                response = requests.get(url=link)


            pdf_io = BytesIO(response.content)
            pdf_file = PdfReader(pdf_io, strict=False)
            for page in pdf_file.pages:
                text += page.extract_text()
                text += "\n\n"
        
        except Exception:
            print("Error! Unable to read pdf file")
            

        return text if text!="" else None

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError


if __name__ == "__main__":
    print(ReadingPDF()._run())

