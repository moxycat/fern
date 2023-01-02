from rply.token import BaseBox
import tags

class Element(BaseBox):
    def __init__(self, tag):
        self.children = []
        self.next = None
        self.tag = tag
        self.attrs = {}
        self.innertext = None
        taginfo = tags.tags.get(self.tag, None)
        if taginfo is None:
            self.is_single = False
            return
        else: self.is_single = taginfo[0]
        # fill required attributes
        for attr in taginfo[1]:
            self.add_attr(attr, "")

    def repr(self, depth=0):
        a = []
        for k, v in self.attrs.items():
            if v is not None: a.append("%s=\"%s\"" % (k, v))
            else: a.append(k)
        return "%s<%s%s>%s%s%s%s%s%s" % (
            "  " * depth,
            self.tag,
            " " + " ".join(a) if any(a) else "",
            self.innertext if self.innertext else "",
            "\n" if len(self.children) else "",
            "".join([c.repr(depth + 1) for c in self.children]),
            ("  " * depth if len(self.children) else "") + f"</{self.tag}>" if not self.is_single else "",
            ("\n" if self.next or depth > 0 else ""),
            self.next.repr(depth) if self.next is not None else ""
        )
    def add_attr(self, key: str, value: str):
        key = key.lower()
        # special case for class attribute
        if (key == "class") and (self.attrs.get("class") is not None):
            self.attrs["class"] += " " + value
        else:
            self.attrs[key] = value
    def add_child(self, child): self.children.append(child)
    def add_next(self, thing):
        cur = self
        while cur.next:
            cur = cur.next
        cur.next = thing
    def duplicate(self, n=0):
        start = self
        end = self
        while end.next:
            end = end.next
        