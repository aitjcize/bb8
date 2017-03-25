CONV="./conv_csv.py"
INPUT="input_csv"
OUTPUT="../appengine"
all: csv2py

csv2py:
	$(CONV) --input $(INPUT)/*"Fund List.csv" --output $(OUTPUT)/fund.py
	$(CONV) --input $(INPUT)/*"Celebrity List.csv" --output $(OUTPUT)/people.py
	$(CONV) --input $(INPUT)/*"Associate Table.csv" --output $(OUTPUT)/alliance_bernstein.py
