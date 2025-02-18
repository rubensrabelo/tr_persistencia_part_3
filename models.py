from odmantic import Model, Reference


class Collaborator(Model):
    name: str
    email: str
    function: str
