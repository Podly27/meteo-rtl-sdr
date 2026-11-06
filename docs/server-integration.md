# Meteostanice a WU – kritický sběr

Stav ověřen 6. 11. 2026. Jde o popis serverového nasazení, nikoli živý stavový endpoint.

Na serveru běží RTL433 se společným SDR příjmem a oddělený pětiminutový server-wu-upload.timer. Starý upload cron byl nahrazen, nezdvojen. Řídicí centrum umožňuje samostatný Start/Stop přijímače a uploadu, kritický stop vyžaduje dvě potvrzení. Host Aplikace kontroluje běh, čerstvost měření a skutečně potvrzené přijetí uploadu čerstvých dat na WU, závažnost Disaster. Limit je 15 minut. Konkrétní sanitizované serverové skripty a unit soubory jsou v Home-ZBX-server/services/meteo; tento repozitář zachovává obecnou podobu projektu. Hesla, CSV a čítače srážek jsou mimo Git.

Centrální provozní dokumentace a obnova: [Home-ZBX-server](https://github.com/Podly27/Home-ZBX-server). Jednotná tabulka, ovládání a monitorovací definice jsou spravované tam; citlivé údaje a provozní data se do zdrojových repozitářů neukládají.
