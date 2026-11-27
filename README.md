# pte_server

## Meritve in šifranti

Nova shema vsebuje šifrante `sites`, `meter_groups`, `subgroups`, `units` in
`meter_names`. Vsak zapis ima celoštevilski `id` in `name`; imena so enolična
razen v `meter_names`, kjer se lahko razlikujejo le po velikosti črk. Nastavite
aplikacijo na novo prazno bazo. Ustavite aplikacijo in za inicializacijo zaženite:

```powershell
python init_db.py
```

Skripta uporablja nastavitve baze iz `app.py`, ustvari manjkajoče tabele in
enkrat izvede `reference_data.sql` kot UTF-8. Baza mora že obstajati in biti
prazna; skripta zavrne bazo, ki vsebuje podatke. Tabele se sicer ustvarijo tudi
ob prvem dostopu aplikacije do baze, vendar brez začetnih vrednosti šifrantov.
ID-ji `meter_names` v tej datoteki so določeni skladno z mobilnim šifrantom.
Skripta je namenjena praznim tabelam in ni migracija obstoječih podatkov.
V obstoječi bazi je treba pred dodajanjem novih imen odstraniti omejitev
enoličnosti stolpca `meter_names.name`; `create_all` je ne odstrani.
Šifrante lahko nato urejate v bazi; zapisov, na katere se meritve sklicujejo,
ni mogoče izbrisati, dokler obstajajo njihove meritve.

`POST /api/measures` sprejme neprazno polje meritev. Namesto `meterId` morajo
vse meritve vsebovati `siteId`, `groupId`, `subGroupId`, `unitId` in
`meterNameId`: pozitivne celoštevilske primarne ključe obstoječih zapisov
ustreznih šifrantov. ID-je lahko preverite v teh tabelah. Ostala polja ostanejo
`id` (OID), `value`, `timestampMs` in `enteredBy`. Tudi odgovor
`GET /api/measures/<user_id>` vsebuje pet novih ID-jev namesto `meterId`.

Ta shema je namenjena novi bazi. `create_all` obstoječe tabele `measures` ne
spremeni; za prenos obstoječih meritev je potrebna ločena migracija s pravili
za preslikavo njihovih vrednosti `meterId`.