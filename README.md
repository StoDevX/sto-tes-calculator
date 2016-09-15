# sto-tes-calculator
A "hours/week" calculator for St. Olaf's Time Entry System (TES)

```console
pip3 install -r requirements.txt
python3 fetch-tes-data.py USERNAME PASSWORD > tes.json
python3 process-tes-data.py < tes.json
```

`process-tes-data.py` takes a single optional argument to set your work award, which defaults to 2300. `python3 process-tes-data.py 1500 < tes.json` would set the work award to 1500, instead.
