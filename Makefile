VENV = venv
ifeq ($(OS),Windows_NT)
	VENV_BIN = Scripts
else
	VENV_BIN = bin
endif

.PHONY: all
all: mypy test lint sphinx

$(VENV)/$(VENV_BIN)/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/$(VENV_BIN)/pip install -r requirements.txt

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf docs-build
	find . -type d -name ".pytest_cache" -prune -exec rm -rf "{}" \;
	find . -type d -name ".mypy_cache" -prune -exec rm -rf "{}" \;
	find . -type d -name "__pycache__" -prune -exec rm -rf "{}" \;

.PHONY: mypy
mypy: $(VENV)/$(VENV_BIN)/activate
	./$(VENV)/$(VENV_BIN)/mypy rsx

.PHONY: test
test: $(VENV)/$(VENV_BIN)/activate
	./$(VENV)/$(VENV_BIN)/pytest rsx

.PHONY: lint
lint: $(VENV)/$(VENV_BIN)/activate
	./$(VENV)/$(VENV_BIN)/pylint rsx

.PHONY: sphinx
sphinx: $(VENV)/$(VENV_BIN)/activate
	./$(VENV)/$(VENV_BIN)/sphinx-build -b html docs docs-build
