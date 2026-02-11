import ui
import dialogs

from . import db
from . import planner
from . import log
from .ui_inbox import InboxView


class HomeTableDataSource(object):
    def __init__(self):
        self.frogs = []
        self.tadpoles = []

    def set_lists(self, frogs, tadpoles):
        self.frogs = frogs
        self.tadpoles = tadpoles

    def tableview_number_of_sections(self, tableview):
        return 2

    def tableview_number_of_rows(self, tableview, section):
        if section == 0:
            return len(self.frogs)
        return len(self.tadpoles)

    def tableview_title_for_header(self, tableview, section):
        return "Today's Frogs" if section == 0 else "Today's Tadpoles"

    def tableview_cell_for_row(self, tableview, section, row):
        cell = ui.TableViewCell('subtitle')
        task = self._task_for_row(section, row)
        cell.text_label.text = task['title']
        return cell

    def tableview_can_edit(self, tableview, section, row):
        return True

    def tableview_edit_actions(self, tableview, section, row):
        task = self._task_for_row(section, row)

        def done_action(sender, tableview, row):
            db.mark_task_done(task['id'])
            if hasattr(tableview.superview, 'refresh_lists'):
                tableview.superview.refresh_lists()

        def snooze_action(sender, tableview, row):
            db.snooze_task_1d(task['id'])
            if hasattr(tableview.superview, 'refresh_lists'):
                tableview.superview.refresh_lists()

        done = ui.TableViewRowAction('Done', done_action)
        done.background_color = '#2ecc71'

        snooze = ui.TableViewRowAction('Snooze 1d', snooze_action)
        snooze.background_color = '#f1c40f'

        return [done, snooze]

    def _task_for_row(self, section, row):
        if section == 0:
            return self.frogs[row]
        return self.tadpoles[row]


class HomeView(ui.View):
    def __init__(self):
        super().__init__()
        self.name = 'LifeOS'
        self.background_color = 'white'

        self.data_source = HomeTableDataSource()

        self.table = ui.TableView()
        self.table.data_source = self.data_source
        self.table.delegate = self.data_source
        self.table.allows_selection = False
        self.add_subview(self.table)

        self.last_capture_label = ui.Label()
        self.last_capture_label.text = 'Last capture: (none)'
        self.last_capture_label.text_color = '#555'
        self.last_capture_label.font = ('<System>', 13)
        self.add_subview(self.last_capture_label)

        self.capture_button = ui.Button()
        self.capture_button.title = '+ Capture'
        self.capture_button.background_color = '#2a7de1'
        self.capture_button.tint_color = 'white'
        self.capture_button.corner_radius = 22
        self.capture_button.action = self.capture_tapped
        self.add_subview(self.capture_button)

        self.right_button_items = [
            ui.ButtonItem(title='Inbox', action=self.open_inbox)
        ]

        self.refresh_lists()

    def layout(self):
        padding = 12
        label_height = 20
        button_size = (120, 44)
        self.table.frame = (0, 0, self.width, self.height - label_height - padding)
        self.last_capture_label.frame = (
            padding,
            self.height - label_height - padding,
            self.width - (button_size[0] + padding * 3),
            label_height,
        )
        self.capture_button.frame = (
            self.width - button_size[0] - padding,
            self.height - button_size[1] - padding,
            button_size[0],
            button_size[1],
        )

    def will_appear(self):
        self.refresh_lists()

    def refresh_lists(self):
        frogs, tadpoles = planner.build_today_lists()
        self.data_source.set_lists(frogs, tadpoles)
        self.table.reload()

    def capture_tapped(self, sender):
        text = dialogs.text_dialog('Capture', '')
        if text:
            db.insert_inbox(text)
            self.last_capture_label.text = 'Last capture: ' + text

    def open_inbox(self, sender):
        log('Opening Inbox')
        inbox_view = InboxView(on_change=self.refresh_lists)
        if self.navigation_view:
            self.navigation_view.push_view(inbox_view)
        else:
            inbox_view.present('fullscreen')


def present_home():
    db.init_db()
    view = HomeView()
    nav = ui.NavigationView(view)
    nav.present('fullscreen')

