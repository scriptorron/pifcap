.DEFAULT_GOAL := all

SRC_DIR = ./src/pifcap
PYUIC5 = pyuic5


$(SRC_DIR)/pifcap_ui.py: $(SRC_DIR)/pifcap_ui.ui
	$(PYUIC5) -x $< -o $@

$(SRC_DIR)/settings_ui.py: $(SRC_DIR)/settings_ui.ui
	$(PYUIC5) -x $< -o $@

all: $(SRC_DIR)/pifcap_ui.py $(SRC_DIR)/settings_ui.py

