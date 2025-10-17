from .interaction import Interaction

# This line tells Python that when another file does `from api.db.models import *`,
# it should make the 'Interaction' class available. It silences the F401 error.
__all__ = ["Interaction"]
