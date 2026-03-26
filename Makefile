NAME = Gomoku
PYTHON = python3
VENV = venv
ACTIVATE = . $(VENV)/bin/activate
MODE = vs

MAIN = main.py

all: $(NAME)

$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

$(NAME): $(VENV)/bin/activate
	$(ACTIVATE) && $(PYTHON) $(MAIN)



clean:
	rm -rf $(VENV)

fclean:
	rm -rf $(VENV) __pycache__

re: clean run

..PHONY: all run clean re fclean