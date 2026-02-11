import ui
from datetime import datetime

from . import db
from . import log


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except Exception:
        try:
            return datetime.strptime(value.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        except Exception:
            return None


def _short_dt(value):
    dt = _parse_dt(value)
    if not dt:
        return value or ''
    return dt.strftime('%b %d %H:%M')


class InboxTableDataSource(object):
    def __init__(self):
        self.items = []

    def set_items(self, items):
        self.items = items

    def tableview_number_of_rows(self, tableview, section):
        return len(self.items)

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        item = self.items[row]
        cell.text_label.text = item['text']
        cell.detail_text_label.text = _short_dt(item['created_at'])
        return cell


class InboxDetailView(ui.View):
    def __init__(self, inbox_item, on_change=None):
        super().__init__()
        self.name = 'Inbox Item'
        self.background_color = 'white'
        self.inbox_item = inbox_item
        self.on_change = on_change

        self.text_label = ui.Label()
        self.text_label.text = inbox_item['text']
        self.text_label.font = ('<System>', 17)
        self.text_label.number_of_lines = 0
        self.add_subview(self.text_label)

        self.date_label = ui.Label()
        self.date_label.text = _short_dt(inbox_item['created_at'])
        self.date_label.text_color = '#666'
        self.date_label.font = ('<System>', 12)
        self.add_subview(self.date_label)

        self.tadpole_button = ui.Button()
        self.tadpole_button.title = 'Convert to Tadpole'
        self.tadpole_button.background_color = '#2a7de1'
        self.tadpole_button.tint_color = 'white'
        self.tadpole_button.corner_radius = 6
        self.tadpole_button.action = self.convert_tadpole
        self.add_subview(self.tadpole_button)

        self.frog_button = ui.Button()
        self.frog_button.title = 'Convert to Frog'
        self.frog_button.background_color = '#16a085'
        self.frog_button.tint_color = 'white'
        self.frog_button.corner_radius = 6
        self.frog_button.action = self.convert_frog
        self.add_subview(self.frog_button)

        self.reference_button = ui.Button()
        self.reference_button.title = 'Mark as Reference'
        self.reference_button.background_color = '#9b59b6'
        self.reference_button.tint_color = 'white'
        self.reference_button.corner_radius = 6
        self.reference_button.action = self.mark_reference
        self.add_subview(self.reference_button)

        self.trash_button = ui.Button()
        self.trash_button.title = 'Trash'
        self.trash_button.background_color = '#e74c3c'
        self.trash_button.tint_color = 'white'
        self.trash_button.corner_radius = 6
        self.trash_button.action = self.trash_item
        self.add_subview(self.trash_button)

    def layout(self):
        padding = 16
        y = padding
        width = self.width - padding * 2

        self.text_label.frame = (padding, y, width, 80)
        y += 88
        self.date_label.frame = (padding, y, width, 16)
        y += 32

        button_height = 40
        for button in [
            self.tadpole_button,
            self.frog_button,
            self.reference_button,
            self.trash_button,
        ]:
            button.frame = (padding, y, width, button_height)
            y += button_height + 10

    def _finish(self):
        if self.on_change:
            self.on_change()
        if self.navigation_view:
            self.navigation_view.pop_view()
        else:
            self.close()

    def convert_tadpole(self, sender):
        db.insert_task_from_inbox(self.inbox_item, 'tadpole', 10)
        self._finish()

    def convert_frog(self, sender):
        db.insert_task_from_inbox(self.inbox_item, 'frog', 30)
        self._finish()

    def mark_reference(self, sender):
        db.insert_reference_from_inbox(self.inbox_item)
        self._finish()

    def trash_item(self, sender):
        db.delete_inbox_item(self.inbox_item['id'])
        self._finish()


class InboxView(ui.View):
    def __init__(self, on_change=None):
        super().__init__()
        self.name = 'Inbox'
        self.background_color = 'white'
        self.on_change = on_change

        self.data_source = InboxTableDataSource()

        self.table = ui.TableView()
        self.table.data_source = self.data_source
        self.table.delegate = self
        self.add_subview(self.table)

        self.refresh()

    def layout(self):
        self.table.frame = self.bounds

    def refresh(self):
        items = db.list_inbox_items()
        self.data_source.set_items(items)
        self.table.reload()

    def tableview_did_select(self, tableview, section, row):
        item = self.data_source.items[row]
        log('Selected inbox item {}'.format(item['id']))
        detail = InboxDetailView(item, on_change=self._on_detail_change)
        if self.navigation_view:
            self.navigation_view.push_view(detail)
        else:
            detail.present('fullscreen')

    def _on_detail_change(self):
        self.refresh()
        if self.on_change:
            self.on_change()

