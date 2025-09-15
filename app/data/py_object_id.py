from typing import Annotated

from pydantic import BeforeValidator

py_object_id = Annotated[str, BeforeValidator(str)]
