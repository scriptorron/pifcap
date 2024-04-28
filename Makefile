.DEFAULT_GOAL := guipy

SRC_DIR = ./src/pifcap
PYUIC5 = pyuic5


$(SRC_DIR)/pifcap_ui.py: $(SRC_DIR)/pifcap_ui.ui
	$(PYUIC5) -x $< -o $@

$(SRC_DIR)/settings_ui.py: $(SRC_DIR)/settings_ui.ui
	$(PYUIC5) -x $< -o $@

guipy: $(SRC_DIR)/pifcap_ui.py $(SRC_DIR)/settings_ui.py

build: guipy $(SRC_DIR)/*.py setup.cfg
	-rm -rf dist
	python3 -m build
	twine check dist/*

upload_testpypi: build
	python3 -m twine upload --repository testpypi dist/*

upload_pypi: build
	python3 -m twine upload dist/*

