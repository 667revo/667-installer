from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QHBoxLayout
from PySide6.QtCore import QThread, Slot, Signal

class InstallerView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("InstallerView")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        title_label = QLabel("Install Apps")
        title_label.setObjectName("PageTitle")
        subtitle_label = QLabel("Install apps with winget module")
        subtitle_label.setObjectName("PageSubtitle")
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search packages (e.g. 7zip, chrome)")
        self.search_button = QPushButton("Search")
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_button)
        layout.addLayout(search_row)
        self.app_combo = QComboBox()
        self.app_combo.addItems(["Microsoft.VisualStudioCode", "Google.Chrome", "7zip.7zip"])
        self.install_button = QPushButton("Install")
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(self.app_combo)
        layout.addWidget(self.install_button)
        layout.addWidget(self.status_label)
        self.install_button.clicked.connect(self.handle_install)
        self.search_button.clicked.connect(self.handle_search)
        self.search_worker = None
        self.worker = None

    @Slot()
    def handle_install(self):
        selected_app = self.app_combo.currentText()
        if not selected_app:
            return
        self.install_button.setEnabled(False)
        self.status_label.setText(f"Installing: {selected_app}...")
        self.worker = InstallitionWorker(selected_app)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_installation_finished)
        self.worker.start()

    @Slot()
    def handle_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.search_button.setEnabled(False)
        self.status_label.setText(f"Searching for {query}...")
        self.search_worker = SearchWorker(query)
        self.search_worker.result.connect(self.on_search_finished)
        self.search_worker.start()

    @Slot(str)
    def update_status(self, message):
        self.status_label.setText(message)

    @Slot(bool, str)
    def on_installation_finished(self, success, message):
        self.install_button.setEnabled(True)
        if success:
            self.status_label.setText("Installation completed")
        else:
            self.status_label.setText(f"Failed: {message[:50]}...")

    @Slot(bool, str)
    def on_search_finished(self, ok, result):
        self.search_button.setEnabled(True)
        if ok:
            package_id = result
            index = -1
            for i in range(self.app_combo.count()):
                item = self.app_combo.itemText(i)
                if item.lower().endswith(package_id.lower()) or item.lower() == package_id.lower():
                    index = i
                    break
            if index >= 0:
                self.app_combo.setCurrentIndex(index)
                self.status_label.setText(f"Found: {package_id}")
            else:
                self.app_combo.addItem(package_id)
                self.app_combo.setCurrentIndex(self.app_combo.count() - 1)
                self.status_label.setText(f"Added and selected: {package_id}")
        else:
            self.status_label.setText("Not found")

class InstallitionWorker(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)
    def __init__(self, winget_id):
        super().__init__()
        self.winget_id = winget_id
    def run(self):
        try:
            from core.installer import install_by_winget_id
            exit_code, output = install_by_winget_id(self.winget_id)
            self.finished.emit(exit_code == 0, output)
        except Exception as e:
            self.finished.emit(False, str(e))

class SearchWorker(QThread):
    result = Signal(bool, str)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        try:
            from core.search import search_first_package_id
            ok, res = search_first_package_id(self.query)
            self.result.emit(ok, res)
        except Exception as e:
            self.result.emit(False, str(e))