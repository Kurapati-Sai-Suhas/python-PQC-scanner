"""Module A negative fixture — no supported library imported; operation-shaped method names
must NOT produce method candidates here (the import gate)."""


class Doc:
    def sign(self, who):
        return f"signed by {who}"

    def verify(self, who):
        return who == "me"


def run():
    d = Doc()
    d.sign("me")
    d.verify("me")
    return d
