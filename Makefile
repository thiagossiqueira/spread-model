# Makefile

run:
	python main.py && python app.py

test:
	pytest

clean:
	rm -f data/skipped_yields.csv
	rm -f static/*.html

install:
	pip install -e .
	pip install -r requirements.txt
