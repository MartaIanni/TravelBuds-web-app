from typing import Annotated
from pydantic import StringConstraints, Strict, Ge


DateStr = Annotated[str, StringConstraints(pattern=[r'^\d{2}/\d{2}/\d{4}$'])]
StrictBool = Annotated[bool, Strict()]
#Stringa con sole lettere e spazi in mezzo
StrictLiteral = Annotated[str, StringConstraints(pattern=[r'^[a-zA-Z ]+$'])]