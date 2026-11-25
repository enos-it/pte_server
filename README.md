# pte_server

## Meritve in šifranti

Nova shema vsebuje šifrante `sites`, `meter_groups`, `subgroups`, `units` in
`meter_names`. Vsak zapis ima celoštevilski `id` in enolični `name`. Nastavite
aplikacijo na novo prazno bazo; tabele se ustvarijo ob prvem dostopu do baze.
Za začetne vrednosti po ustvaritvi tabel enkrat izvedite `reference_data.sql`
kot UTF-8.
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