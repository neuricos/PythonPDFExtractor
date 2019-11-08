import sys
import os
import PyPDF2

class PDFInputDoc:
    def __init__(self, path):
        self._path = path
        self._file = open(path, 'rb')
        self._reader = PyPDF2.PdfFileReader(self._file)
        self._pcount = self._reader.getNumPages()

    def get_page(self, pnum):
        assert(pnum < self._pcount)
        return self._reader.getPage(pnum)

    def check_page(self, pnum):
        return pnum < self._pcount

    def __str__(self):
        return "<Path:{}; PageCount:{}>".format(self._path, self._pcount)


class PDFOutputDoc:
    def __init__(self):
        self._outpages = []
        self._pcount = 0

    def add_page(self, doc, pnum):
        pnum -= 1
        assert(pnum >= 0)
        assert(doc.check_page(pnum))
        self._outpages.append((doc, pnum))
        self._pcount += 1

    def remove_page(self, pageid):
        assert(pageid >= 0)
        assert(pageid < self._pcount)
        self._outpages.pop(pageid)
        self._pcount -= 1

    def export(self, path):
        from srblib import abs_path
        path = abs_path(path)
        writer = PyPDF2.PdfFileWriter()
        for doc, pnum in self._outpages:
            writer.addPage(doc.get_page(pnum))
        with open(path, 'wb') as f:
            writer.write(f)

    def show(self, prefix=""):
        s = []
        for i, (d, p) in enumerate(self._outpages):
            s.append("{}<Pageid:{}; Path:{}; PageNumber:{}>".format(prefix, i, d._path, p + 1))
        return "\n".join(s)


def show_options():
    print("Options:\n"
          "\thelp\n"
          "\tshow all\n"
          "\tshow target\n"
          "\tadd <document id> <page id>\n"
          "\tremove <page id>\n"
          "\texport\n"
          "\tquit")


def is_pdf(path):
    _, ext = os.path.splitext(path)
    return ext == '.pdf'


def add_parse(s):
    assert("add" in s)
    tokens = s.split()
    assert(len(tokens) == 3)
    try:
        docid = int(tokens[1])
        pagenum = int(tokens[2])
    except ValueError as e:
        raise ValueError("<document id> and <page id> need to be integers")
    return (docid, pagenum)


def remove_parse(s):
    assert("remove" in s)
    tokens = s.split()
    assert(len(tokens) == 2)
    try:
        pageid = int(tokens[1])
    except ValueError as e:
        raise ValueError("<page id> needs to be integer")
    return pageid


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: {} <filename> ...".format(sys.argv[0]))
        sys.exit(1)

    working_docs = []

    for f in sys.argv[1:]:
        if not os.access(f, os.F_OK):
            print("{} does not exist!".format(f))
            sys.exit(2)
        if not os.access(f, os.R_OK):
            print("{} is not readable!".format(f))
            sys.exit(3)
        if not is_pdf(f):
            print("{} is not a pdf!".format(f))
            sys.exit(4)

        try:
            working_docs.append(PDFInputDoc(f))
        except OSError as e:
            print(e)
            print("{} is invalid".format(f))
            sys.exit(5)

        print("Added {} to working documents".format(f))

    target_doc = PDFOutputDoc()
    show_options()

    while True:
        opt = input(">> ").strip()

        if opt == 'quit':
            sys.exit(0)

        if opt == 'help':
            show_options()
            continue

        if opt == 'show all':
            print("Working documents:")
            for i, d in enumerate(working_docs):
                print("\t<Docid:{}> {}".format(i, d))
            continue

        if opt == 'show target':
            print("Target document:")
            print(target_doc.show("\t"))
            continue

        if opt == "export":
            output_path = input("Output path: ").strip()
            target_doc.export(output_path)
            continue

        if "add" in opt:
            docid, pagenum = add_parse(opt)
            target_doc.add_page(working_docs[docid], pagenum)
            continue

        if "remove" in opt:
            pageid = remove_parse(opt)
            target_doc.remove_page(pageid)
            continue

        print("Invalid command")












        