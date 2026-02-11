import ui
import dialogs

from . import db
from . import planner


class HomeTableDataSource(object):
    def __init__(self, frogs, tadpoles):
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
        cell = ui.TableViewCell()
        if section == 0:
            cell.text_label.text = self.frogs[row]
        else:
            cell.text_label.text = self.tadpoles[row]
        return cell


class HomeView(ui.View):
    def __init__(self):
        super().__init__()
        self.name = 'LifeOS'
        self.background_color = 'white'

        frogs, tadpoles = planner.build_today_lists()
        self.data_source = HomeTableDataSource(frogs, tadpoles)

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

    def capture_tapped(self, sender):
        text = dialogs.text_dialog('Capture', '')
        if text:
            db.insert_inbox(text)
            self.last_capture_label.text = 'Last capture: ' + text


def present_home():
    db.init_db()
    view = HomeView()
    view.present('fullscreen')

