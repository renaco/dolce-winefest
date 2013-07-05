from math import ceil


class Paginator(object):

    def __init__(self, page, total_items, adjacents=2, per_page=10):
        self.page = page
        self.per_page = per_page
        self.total_items = total_items
        self.adjacents = adjacents

    @property
    def total_pages(self):
        return int(ceil(self.total_items / (self.per_page * 1.0)))

    @property
    def pages(self):
        if self.page > self.total_pages:
            pages = []
        elif self.total_pages <= 2 * self.adjacents:
            pages = range(1, self.total_pages + 1)
        else:
            if self.page <= self.adjacents:
                frm = 1
            else:
                if self.total_pages - self.page < self.adjacents:
                    frm = self.total_pages - 2 * self.adjacents
                else:
                    frm = self.page - self.adjacents

            inc = 2 * self.adjacents + 1
            pages = range(frm, frm + inc)

        return pages
