
import sys
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QDate, QTime, Signal, QObject, QTimer, QSignalBlocker, QThread
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QSpinBox,
    QAbstractSpinBox,
    QRadioButton,
    QDialogButtonBox,
    QDialog,
    QApplication,
    QComboBox,
    QCompleter,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app import run_sunseat
from engine.gtfs_reader import get_stop_names, preload_gtfs_data


# =========================================================
# SUNSEAT MODERN THEME
# =========================================================

BG = "#0B1324"
PANEL = "#16233D"
PANEL_2 = "#1C2B48"
INPUT = "#202F4C"
INPUT_HOVER = "#263A5B"
BORDER = "#31415F"

TEXT = "#F5F7FB"
MUTED = "#AAB5C9"
SUBTLE = "#71809A"

SUN = "#FFB000"
SUN_SOFT = "#342A18"

SUCCESS = "#62E26B"
SUCCESS_SOFT = "#173522"

WHITE = "#FFFFFF"


# =========================================================
# HELPERS
# =========================================================

def card(parent=None):
    widget = QFrame(parent)
    widget.setObjectName("Card")
    return widget


def title_label(text, size=18):
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size, QFont.Weight.Bold))
    label.setStyleSheet(f"color: {TEXT};")
    return label


def muted_label(text, size=10):
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", size))
    label.setStyleSheet(f"color: {MUTED};")
    return label


# =========================================================
# STARTUP WORKER
# =========================================================

class StartupWorker(QObject):
    finished = Signal()
    failed = Signal(str)

    def __init__(self, stop_times_file, stops_file):
        super().__init__()
        self.stop_times_file = stop_times_file
        self.stops_file = stops_file

    def run(self):
        try:
            preload_gtfs_data(
                self.stop_times_file,
                self.stops_file
            )
            self.finished.emit()
        except Exception as error:
            self.failed.emit(str(error))


# =========================================================
# MAIN WINDOW
# =========================================================

class SunSeatWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SunSeat")
        self.resize(1240, 860)
        self.setMinimumSize(920, 700)

        base_dir = Path(__file__).resolve().parent
        data_dir = base_dir / "data" / "DE-RV"

        self.stop_times_file = data_dir / "stop_times.txt"
        self.stops_file = data_dir / "stops.txt"

        self.station_names = get_stop_names(
            self.stops_file
        )

        self.setup_style()
        self.build_ui()
        self.start_timetable_loading()

    # -----------------------------------------------------
    # STYLE
    # -----------------------------------------------------

    def setup_style(self):

        self.setStyleSheet(f"""
            QMainWindow {{
                background: {BG};
            }}

            QWidget {{
                font-family: "Segoe UI";
                color: {TEXT};
            }}

            QFrame#Card {{
                background: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 18px;
            }}

            QFrame#InnerCard {{
                background: {PANEL_2};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}

            QLabel#SectionLabel {{
                color: {MUTED};
                font-size: 10px;
                font-weight: 700;
            }}

            QLineEdit,
            QDateEdit,
            QTimeEdit {{
                background: {INPUT};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 10px 12px;
                font-size: 11px;
                selection-background-color: {SUN};
                selection-color: {BG};
            }}

            QLineEdit:focus,
            QDateEdit:focus,
            QTimeEdit:focus {{
                border: 1px solid {SUN};
            }}

            QLineEdit:hover,
            QDateEdit:hover,
            QTimeEdit:hover {{
                background: {INPUT_HOVER};
            }}


            QCalendarWidget {{
                background: {PANEL};
                color: {TEXT};
            }}

            QCalendarWidget QWidget {{
                background: {PANEL};
                color: {TEXT};
            }}

            QCalendarWidget QToolButton {{
                color: {TEXT};
                background: {PANEL};
                border: none;
                padding: 6px;
                font-weight: 700;
            }}

            QCalendarWidget QToolButton:hover {{
                background: {INPUT_HOVER};
                border-radius: 6px;
            }}

            QCalendarWidget QMenu {{
                background: {PANEL_2};
                color: {TEXT};
            }}

            QCalendarWidget QSpinBox {{
                color: {TEXT};
                background: {INPUT};
                border: 1px solid {BORDER};
                border-radius: 6px;
            }}

            QCalendarWidget QAbstractItemView {{
                background: {PANEL_2};
                color: {TEXT};
                selection-background-color: {SUN};
                selection-color: {BG};
                alternate-background-color: {PANEL};
            }}

            QComboBox {{
                background: {INPUT};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 10px 12px;
            }}

            QComboBox QAbstractItemView {{
                background: {PANEL_2};
                color: {TEXT};
                border: 1px solid {BORDER};
                selection-background-color: {SUN};
                selection-color: {BG};
            }}

            QDialog#TimePicker {{
                background: {PANEL};
                color: {TEXT};
            }}

            QLabel#TimePickerTitle {{
                color: {TEXT};
                font-size: 15px;
                font-weight: 800;
            }}

            QLabel#TimePickerHint {{
                color: {MUTED};
                font-size: 10px;
            }}

            QSpinBox#TimeSpinner {{
                background: {INPUT};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 8px;
                font-size: 22px;
                font-weight: 700;
            }}

            QSpinBox#TimeSpinner:focus {{
                border: 1px solid {SUN};
            }}

            QPushButton#PeriodButton {{
                background: {INPUT};
                color: {TEXT};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 12px;
                font-weight: 800;
                min-width: 64px;
            }}

            QPushButton#PeriodButton:checked {{
                background: {SUN};
                color: {BG};
                border: 1px solid {SUN};
            }}

            QPushButton#TimeDone {{
                background: {SUN};
                color: {BG};
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 11px;
                font-weight: 800;
            }}

            QPushButton#TimeDone:hover {{
                background: #FFC238;
            }}

            QPushButton#FindButton {{
                background: {SUN};
                color: {BG};
                border: none;
                border-radius: 11px;
                padding: 12px;
                font-size: 12px;
                font-weight: 800;
            }}

            QPushButton#FindButton:hover {{
                background: #FFC238;
            }}

            QPushButton#FindButton:pressed {{
                background: #E99D00;
            }}

            QPushButton#FindButton:disabled {{
                background: #5A5B55;
                color: #C8C8C8;
            }}

            QLabel#StatusReady {{
                color: {SUCCESS};
                background: {SUCCESS_SOFT};
                border: 1px solid #285936;
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 700;
            }}

            QLabel#StatusLoading {{
                color: {SUN};
                background: {SUN_SOFT};
                border: 1px solid #5A481D;
                border-radius: 10px;
                padding: 9px 14px;
                font-weight: 700;
            }}

            QLabel#Hero {{
                color: {SUN};
                font-size: 30px;
                font-weight: 900;
            }}

            QLabel#RouteTitle {{
                color: {TEXT};
                font-size: 13px;
                font-weight: 800;
            }}

            QLabel#HeroDirection {{
                color: {MUTED};
                font-size: 10px;
            }}

            QFrame#HeroVisual {{
                background: #13213A;
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}

            QFrame#ExposureBest {{
                background: #173A2A;
                border: 1px solid #3A8A58;
                border-radius: 14px;
            }}

            QLabel#TimelineTime {{
                color: {SUCCESS};
                font-size: 14px;
                font-weight: 800;
            }}

            QLabel#TimelineStation {{
                color: {TEXT};
                font-size: 11px;
                font-weight: 700;
            }}

            QLabel#TimelineMeta {{
                color: {MUTED};
                font-size: 9px;
            }}

            QLabel#Recommendation {{
                color: {SUCCESS};
                font-size: 30px;
                font-weight: 900;
            }}

            QLabel#Confidence {{
                color: {TEXT};
                font-size: 13px;
                font-weight: 600;
            }}

            QLabel#ExposureValue {{
                color: {TEXT};
                font-size: 19px;
                font-weight: 800;
            }}

            QLabel#ExposureName {{
                color: {MUTED};
                font-size: 10px;
                font-weight: 700;
            }}
        """)

    # -----------------------------------------------------
    # UI
    # -----------------------------------------------------

    def build_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(28, 22, 28, 18)
        root.setSpacing(18)

        # Header
        header = QHBoxLayout()
        header.setSpacing(14)

        logo = QLabel("☀")
        logo.setFont(QFont("Segoe UI Symbol", 34))
        logo.setStyleSheet(f"color: {SUN};")

        brand_box = QVBoxLayout()
        brand_box.setSpacing(0)

        brand = QLabel("SUNSEAT")
        brand.setFont(QFont("Segoe UI", 27, QFont.Weight.Black))
        brand.setStyleSheet(f"color: {TEXT};")

        subtitle = QLabel("Find the sunnier side of your journey.")
        subtitle.setStyleSheet(f"color: {MUTED}; font-size: 12px;")

        brand_box.addWidget(brand)
        brand_box.addWidget(subtitle)

        header.addWidget(logo)
        header.addLayout(brand_box)
        header.addStretch()

        self.status = QLabel("●  Loading timetable...")
        self.status.setObjectName("StatusLoading")
        header.addWidget(self.status)

        root.addLayout(header)

        # Main two-column area
        columns = QHBoxLayout()
        columns.setSpacing(18)

        # Left journey card
        journey = card()
        journey_layout = QVBoxLayout(journey)
        journey_layout.setContentsMargins(22, 20, 22, 22)
        journey_layout.setSpacing(12)

        journey_layout.addWidget(title_label("▣  PLAN YOUR JOURNEY", 16))
        journey_layout.addSpacing(4)

        self.from_edit = self.create_station_input("From")
        self.to_edit = self.create_station_input("To")

        journey_layout.addWidget(self.section_text("FROM"))
        journey_layout.addWidget(self.from_edit)
        journey_layout.addWidget(muted_label("Start station", 9))

        journey_layout.addSpacing(4)

        journey_layout.addWidget(self.section_text("TO"))
        journey_layout.addWidget(self.to_edit)
        journey_layout.addWidget(muted_label("Destination station", 9))

        journey_layout.addSpacing(4)

        date_time_row = QHBoxLayout()
        date_time_row.setSpacing(10)

        date_box = QVBoxLayout()
        date_box.addWidget(self.section_text("DATE"))

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd MMM yyyy")
        self.date_edit.setDate(QDate.currentDate())
        date_box.addWidget(self.date_edit)

        time_box = QVBoxLayout()
        time_box.addWidget(self.section_text("DEPARTURE TIME"))

        # Professional departure-time control.
        # The displayed value is user-friendly, while the underlying QTime
        # remains compatible with the existing search logic.
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("h:mm AP")
        self.time_edit.setTime(QTime(10, 0))
        self.time_edit.setToolTip(
            "Click the time to edit it, or use the arrow controls"
        )
        # Keep the control directly editable. The previous custom popup made
        # the field read-only, which prevented normal typing/editing.
        self.time_edit.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.UpDownArrows
        )
        self.time_edit.setReadOnly(False)
        self.time_edit.setKeyboardTracking(False)
        self.time_edit.setAccelerated(True)
        time_box.addWidget(self.time_edit)

        date_time_row.addLayout(date_box, 1)
        date_time_row.addLayout(time_box, 1)

        journey_layout.addLayout(date_time_row)
        journey_layout.addSpacing(8)

        self.find_button = QPushButton("☀  FIND MY SUNSEAT")
        self.find_button.setObjectName("FindButton")
        self.find_button.clicked.connect(self.find_sunseat)
        self.find_button.setEnabled(False)
        journey_layout.addWidget(self.find_button)

        journey_layout.addStretch()

        tips = QFrame()
        tips.setObjectName("InnerCard")
        tips_layout = QVBoxLayout(tips)
        tips_layout.setContentsMargins(14, 12, 14, 12)

        tips_layout.addWidget(
            QLabel(
                "💡  QUICK TIPS",
                styleSheet=f"color: {MUTED}; font-size: 10px; font-weight: 800;"
            )
        )
        tips_layout.addWidget(
            QLabel(
                "We analyze the sunlight along your route\n"
                "and recommend the best side to sit on.",
                styleSheet=f"color: {MUTED}; font-size: 10px;"
            )
        )

        journey_layout.addWidget(tips)

        columns.addWidget(journey, 1)

        # Right result card
        result = card()
        result_layout = QVBoxLayout(result)
        result_layout.setContentsMargins(22, 20, 22, 22)
        result_layout.setSpacing(12)

        result_header = QHBoxLayout()
        result_header.addWidget(title_label("☀  YOUR SUNSEAT", 16))
        result_header.addStretch()

        self.confidence_badge = QLabel("Waiting for journey")
        self.confidence_badge.setStyleSheet(
            f"""
            color: {MUTED};
            background: {INPUT};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 8px 12px;
            font-size: 10px;
            font-weight: 700;
            """
        )
        result_header.addWidget(self.confidence_badge)

        result_layout.addLayout(result_header)

        hero = QFrame()
        hero.setObjectName("HeroVisual")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(18, 16, 18, 16)
        hero_layout.setSpacing(4)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hero_route = QLabel("Your journey")
        self.hero_route.setObjectName("RouteTitle")
        self.hero_route.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hero_sun = QLabel("☀")
        self.hero_sun.setFont(QFont("Segoe UI Symbol", 52))
        self.hero_sun.setStyleSheet(f"color: {SUN};")
        self.hero_sun.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hero_direction = QLabel("Sun exposure along your route")
        self.hero_direction.setObjectName("HeroDirection")
        self.hero_direction.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.recommendation = QLabel("YOUR SUNSEAT")
        self.recommendation.setObjectName("Recommendation")
        self.recommendation.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.confidence = QLabel("Enter a journey to calculate the sunny side.")
        self.confidence.setObjectName("Confidence")
        self.confidence.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_layout.addWidget(self.hero_route)
        hero_layout.addWidget(self.hero_sun)
        hero_layout.addWidget(self.hero_direction)
        hero_layout.addWidget(self.recommendation)
        hero_layout.addWidget(self.confidence)

        result_layout.addWidget(hero)

        exposure = QHBoxLayout()
        exposure.setSpacing(10)

        self.exposure_cards = {}
        self.exposure_labels = {}

        for side in ("FRONT", "RIGHT", "LEFT", "BACK"):
            item = QFrame()
            item.setObjectName("InnerCard")

            item_layout = QVBoxLayout(item)
            item_layout.setContentsMargins(8, 11, 8, 11)
            item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            name = QLabel(side)
            name.setObjectName("ExposureName")
            name.setAlignment(Qt.AlignmentFlag.AlignCenter)

            value = QLabel("—")
            value.setObjectName("ExposureValue")
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)

            item_layout.addWidget(name)
            item_layout.addWidget(value)

            exposure.addWidget(item, 1)
            self.exposure_cards[side] = item
            self.exposure_labels[side] = value

        result_layout.addLayout(exposure)

        sun_info = QFrame()
        sun_info.setObjectName("InnerCard")
        info_layout = QHBoxLayout(sun_info)
        info_layout.setContentsMargins(14, 11, 14, 11)

        self.route_label = QLabel("No journey selected")
        self.route_label.setStyleSheet(
            f"color: {TEXT}; font-size: 11px; font-weight: 700;"
        )

        self.departure_label = QLabel("")
        self.departure_label.setStyleSheet(
            f"color: {MUTED}; font-size: 10px;"
        )

        info_layout.addWidget(self.route_label)
        info_layout.addStretch()
        info_layout.addWidget(self.departure_label)

        result_layout.addWidget(sun_info)
        result_layout.addStretch()

        columns.addWidget(result, 1)

        root.addLayout(columns, 1)

        # Bottom journey card
        journey_result = card()
        bottom_layout = QHBoxLayout(journey_result)
        bottom_layout.setContentsMargins(20, 14, 20, 14)

        self.bottom_origin = QLabel("—")
        self.bottom_origin.setStyleSheet(
            f"color: {TEXT}; font-size: 11px; font-weight: 700;"
        )

        self.bottom_destination = QLabel("—")
        self.bottom_destination.setStyleSheet(
            f"color: {TEXT}; font-size: 11px; font-weight: 700;"
        )

        self.bottom_middle = QLabel("Your journey will appear here")
        self.bottom_middle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottom_middle.setStyleSheet(
            f"color: {MUTED}; font-size: 10px;"
        )

        bottom_layout.addWidget(self.bottom_origin)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.bottom_middle)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.bottom_destination)

        root.addWidget(journey_result)

        footer = QHBoxLayout()

        footer.addWidget(
            self.make_footer_label("◈  GTFS timetable data")
        )
        footer.addStretch()
        footer.addWidget(
            self.make_footer_label("SunSeat v1.0")
        )

        root.addLayout(footer)

    # -----------------------------------------------------
    # INPUTS
    # -----------------------------------------------------

    def make_footer_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {SUBTLE}; font-size: 9px;")
        return label

    def section_text(self, text):
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label

    def canonical_station_name(self, value):
        """
        Return the exact station name from GTFS for a user-entered value.
        Matching is case-insensitive so 'karlsruhe hbf' becomes
        'Karlsruhe Hbf' before the engine is called.
        """
        value = value.strip()

        for name in self.station_names:
            if name.casefold() == value.casefold():
                return name

        return value

    def ranked_station_names(self, query):
        """
        Rank suggestions by usefulness rather than plain alphabetical order.

        Priority:
        1. Exact station name
        2. '<query> Hbf' / Hbf-style match
        3. Names beginning with the query
        4. Names containing the query elsewhere
        """
        query = query.strip().casefold()

        if not query:
            return self.station_names[:]

        def score(name):
            folded = name.casefold()

            if folded == query:
                return (0, folded)

            # Prioritize a major Hbf station when the user has typed
            # only the beginning of its city/station name.
            # Example: "karls" -> "Karlsruhe Hbf" should rank above
            # less relevant stations such as "Karlsburg" or "Karlsfeld".
            if folded.endswith(" hbf") and folded.startswith(query):
                return (1, folded)

            if folded == query + " hbf":
                return (1, folded)

            if folded.startswith(query + " hbf"):
                return (1, folded)

            if folded.startswith(query):
                return (2, folded)

            if query in folded:
                return (3, folded)

            return (4, folded)

        matches = [
            name
            for name in self.station_names
            if query in name.casefold()
        ]

        return sorted(matches, key=score)

    def create_station_input(self, placeholder):

        edit = QLineEdit()
        edit.setPlaceholderText(
            f"{placeholder} station"
        )

        completer = QCompleter(
            self.ranked_station_names(""),
            edit
        )

        completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        completer.setFilterMode(
            Qt.MatchFlag.MatchContains
        )

        completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )

        completer.setMaxVisibleItems(10)

        popup = completer.popup()
        popup.setMinimumWidth(520)
        popup.setUniformItemSizes(True)

        edit.setCompleter(completer)

        # Prevent the textChanged handler from reopening the popup while
        # we are programmatically inserting a selected completion.
        completion_state = {"accepting": False}

        def update_suggestions(query):
            if completion_state["accepting"]:
                return

            ranked = self.ranked_station_names(query)

            # Keep the useful relevance order generated above.
            from PySide6.QtCore import QStringListModel
            model = QStringListModel(ranked, completer)
            completer.setModel(model)

            if query.strip() and ranked:
                completer.complete()
            else:
                completer.popup().hide()

        def accept_completion(value):
            completion_state["accepting"] = True

            exact = self.canonical_station_name(value)

            # Block the textChanged handler while inserting the selected
            # station.
            blocker = QSignalBlocker(edit)
            edit.setText(exact)
            del blocker

            # Clear the completer's model before hiding it. This prevents Qt
            # from immediately reopening the popup with the selected text.
            from PySide6.QtCore import QStringListModel
            empty_model = QStringListModel([], completer)
            completer.setModel(empty_model)

            completer.popup().hide()
            edit.setFocus()

            # One extra event-loop hide handles Qt's internal completion
            # processing after the activated signal.
            QTimer.singleShot(
                0,
                completer.popup().hide
            )

            completion_state["accepting"] = False

        edit.textChanged.connect(update_suggestions)
        completer.activated.connect(accept_completion)

        return edit

    # -----------------------------------------------------
    # STARTUP
    # -----------------------------------------------------

    def start_timetable_loading(self):

        self.find_button.setEnabled(False)

        self.startup_thread = QThread(self)
        self.startup_worker = StartupWorker(
            self.stop_times_file,
            self.stops_file
        )

        self.startup_worker.moveToThread(self.startup_thread)

        self.startup_thread.started.connect(
            self.startup_worker.run
        )

        self.startup_worker.finished.connect(
            self.status_ready
        )

        self.startup_worker.failed.connect(
            self.status_failed
        )

        self.startup_worker.finished.connect(
            self.startup_thread.quit
        )

        self.startup_worker.failed.connect(
            self.startup_thread.quit
        )

        self.startup_thread.finished.connect(
            self.startup_worker.deleteLater
        )

        self.startup_thread.finished.connect(
            self.startup_thread.deleteLater
        )

        self.startup_thread.start()

    def status_ready(self):
        self.status.setText("●  Timetable ready")
        self.status.setObjectName("StatusReady")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.find_button.setEnabled(True)

    def status_failed(self, error):
        self.status.setText("●  Timetable unavailable")
        self.status.setObjectName("StatusLoading")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.find_button.setEnabled(False)

        QMessageBox.critical(
            self,
            "SunSeat Startup Error",
            "SunSeat could not load the timetable data.\n\n"
            "Please check that the GTFS files are available."
        )

        print("GTFS startup error:", error)

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    def open_time_picker(self, event):
        """Open a compact, branded time picker instead of the native spinner."""
        dialog = QDialog(self)
        dialog.setObjectName("TimePicker")
        dialog.setWindowTitle("Departure time")
        dialog.setModal(True)
        dialog.setFixedSize(360, 230)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title = QLabel("Departure time")
        title.setObjectName("TimePickerTitle")
        layout.addWidget(title)

        hint = QLabel("Choose when you want to leave")
        hint.setObjectName("TimePickerHint")
        layout.addWidget(hint)

        current = self.time_edit.time()
        hour12 = current.hour() % 12 or 12
        minute = current.minute()
        is_pm = current.hour() >= 12

        row = QHBoxLayout()
        row.setSpacing(8)

        hour = QSpinBox()
        hour.setObjectName("TimeSpinner")
        hour.setRange(1, 12)
        hour.setValue(hour12)
        hour.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        hour.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(hour, 1)

        colon = QLabel(":")
        colon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        colon.setStyleSheet(
            f"color: {MUTED}; font-size: 22px; font-weight: 700;"
        )
        row.addWidget(colon)

        minute_box = QSpinBox()
        minute_box.setObjectName("TimeSpinner")
        minute_box.setRange(0, 59)
        minute_box.setValue(minute)
        minute_box.setSingleStep(5)
        minute_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        minute_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(minute_box, 1)

        am_button = QPushButton("AM")
        am_button.setObjectName("PeriodButton")
        am_button.setCheckable(True)

        pm_button = QPushButton("PM")
        pm_button.setObjectName("PeriodButton")
        pm_button.setCheckable(True)

        am_button.setChecked(not is_pm)
        pm_button.setChecked(is_pm)

        am_button.clicked.connect(lambda: pm_button.setChecked(False))
        pm_button.clicked.connect(lambda: am_button.setChecked(False))

        row.addWidget(am_button)
        row.addWidget(pm_button)

        layout.addLayout(row)

        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel = QPushButton("Cancel")
        cancel.setObjectName("PeriodButton")
        cancel.clicked.connect(dialog.reject)

        done = QPushButton("SET TIME")
        done.setObjectName("TimeDone")

        def apply_time():
            hour_value = hour.value() % 12
            if pm_button.isChecked():
                hour_value += 12
            self.time_edit.setTime(
                QTime(hour_value, minute_box.value())
            )
            dialog.accept()

        done.clicked.connect(apply_time)

        buttons.addWidget(cancel)
        buttons.addWidget(done)
        layout.addLayout(buttons)

        dialog.exec()

    def find_sunseat(self):

        origin = self.canonical_station_name(
            self.from_edit.text()
        )

        destination = self.canonical_station_name(
            self.to_edit.text()
        )

        # Put the canonical GTFS spelling back into the fields.
        self.from_edit.setText(origin)
        self.to_edit.setText(destination)

        date = self.date_edit.date().toString(
            "yyyy-MM-dd"
        )

        departure_time = self.time_edit.time().toString(
            "HH:mm"
        )

        if not origin:
            QMessageBox.warning(
                self,
                "Missing Origin",
                "Please enter your departure station."
            )
            self.from_edit.setFocus()
            return

        if not destination:
            QMessageBox.warning(
                self,
                "Missing Destination",
                "Please enter your destination station."
            )
            self.to_edit.setFocus()
            return

        self.find_button.setEnabled(False)
        self.find_button.setText("☀  ANALYZING JOURNEY...")

        try:
            result = run_sunseat(
                origin,
                destination,
                date,
                departure_time
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "SunSeat Error",
                "Something went wrong while finding your SunSeat."
            )
            print("SunSeat error:", error)

            self.find_button.setEnabled(True)
            self.find_button.setText("☀  FIND MY SUNSEAT")
            return

        self.find_button.setEnabled(True)
        self.find_button.setText("☀  FIND MY SUNSEAT")

        if not result["success"]:

            # Clear the result so an older journey can never remain visible.
            self.clear_result()

            self.show_error_result(
                result["message"]
            )

            return

        self.show_result(result)

    # -----------------------------------------------------
    # RESULT
    # -----------------------------------------------------

    def clear_result(self):

        self.hero_route.setText("Your journey")
        self.route_label.setText("No journey selected")
        self.departure_label.setText("")
        self.bottom_origin.setText("—")
        self.bottom_destination.setText("—")
        self.bottom_middle.setText(
            "Your journey will appear here"
        )

        for label in self.exposure_labels.values():
            label.setText("—")

        self.recommendation.setText("YOUR SUNSEAT")
        self.confidence.setText(
            "Enter a journey to calculate the sunny side."
        )
        self.confidence_badge.setText(
            "Waiting for journey"
        )

    def show_error_result(self, message):

        self.hero_route.setText("Journey unavailable")
        self.route_label.setText("No matching journey")
        self.departure_label.setText("")

        self.hero_sun.setText("!")
        self.hero_sun.setStyleSheet(
            f"color: {SUN}; font-size: 52px;"
        )

        self.recommendation.setText("NO JOURNEY FOUND")
        self.recommendation.setStyleSheet(
            f"color: {SUN}; font-size: 26px; font-weight: 900;"
        )

        self.confidence.setText(message)

        self.confidence_badge.setText("No match")

        self.bottom_origin.setText(
            self.from_edit.text().strip() or "—"
        )

        self.bottom_destination.setText(
            self.to_edit.text().strip() or "—"
        )

        self.bottom_middle.setText(
            "Try another departure time or route."
        )

        for side in ("FRONT", "RIGHT", "LEFT", "BACK"):
            self.exposure_labels[side].setText("—")
            self.exposure_cards[side].setObjectName("InnerCard")
            self.exposure_cards[side].style().unpolish(
                self.exposure_cards[side]
            )
            self.exposure_cards[side].style().polish(
                self.exposure_cards[side]
            )

    def show_result(self, result):

        self.hero_sun.setText("☀")
        self.hero_sun.setStyleSheet(
            f"color: {SUN}; font-size: 52px;"
        )

        analysis = result["result"]
        counts = analysis["counts"]

        self.hero_route.setText(
            f"{result['origin']}  →  {result['destination']}"
        )

        self.route_label.setText(
            f"{result['origin']}  →  {result['destination']}"
        )

        self.departure_label.setText(
            f"Scheduled departure · {result['scheduled_departure']}"
        )

        self.bottom_origin.setText(
            result["origin"]
        )

        self.bottom_destination.setText(
            result["destination"]
        )

        self.bottom_middle.setText(
            f"Departure {result['scheduled_departure']}"
        )

        for side in ("FRONT", "RIGHT", "LEFT", "BACK"):
            self.exposure_labels[side].setText(
                str(counts[side.lower()])
            )

        for side, item in self.exposure_cards.items():
            item.setObjectName("InnerCard")
            item.style().unpolish(item)
            item.style().polish(item)

        recommendation = analysis["recommendation"]

        if recommendation["side"] is None:
            self.recommendation.setText(
                "NO CLEAR SIDE"
            )
            self.recommendation.setStyleSheet(
                f"color: {SUN}; font-size: 30px; font-weight: 900;"
            )

            self.confidence.setText(
                "Sun exposure is too balanced for a confident recommendation."
            )

            self.confidence_badge.setText(
                "Balanced sunlight"
            )

        else:
            side = recommendation["side"].upper()
            confidence = recommendation["confidence"] * 100

            self.recommendation.setText(
                f"{side} SIDE"
            )

            self.recommendation.setStyleSheet(
                f"color: {SUCCESS}; font-size: 30px; font-weight: 900;"
            )

            self.confidence.setText(
                f"{confidence:.0f}% confidence"
            )

            self.confidence_badge.setText(
                "High confidence"
                if confidence >= 80
                else "Good confidence"
            )

            if side in self.exposure_cards:
                self.exposure_cards[side].setObjectName("ExposureBest")
                self.exposure_cards[side].style().unpolish(
                    self.exposure_cards[side]
                )
                self.exposure_cards[side].style().polish(
                    self.exposure_cards[side]
                )


# =========================================================
# MAIN
# =========================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName("SunSeat")
    app.setApplicationDisplayName("SunSeat")

    window = SunSeatWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
