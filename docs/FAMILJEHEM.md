# Lokal fork

Serverns produktionsdata får aldrig vara åtkomliga för byggmiljön.
Bygg mot den syntetiska testservern. Inga konton, nycklar eller .env i Git.

`bash build-signed-local.sh` använder en signernyckel och lösenordsfil utanför Git
(default `../.private`). Skapa inte en ny nyckel vid varje release: Android
kräver samma nyckel för uppgraderingar. En kopia på samma disk är ingen säker
backup mot diskhaveri. Flytta en krypterad kopia till separat skyddad lagring.

Appens identitet: se.familj.hem / Familjehem, version 0.1.0 (1).
Uppdateringsformat: JSON-lista i `/updates/manifest.json` på samma HTTPS-origin
som inloggningsservern. Exempel (ersätt digest med verklig checksumma):

```json
[{"tag_name":"v0.1.0","assets":[{"name":"yuvomi-android-0.1.0.apk","browser_download_url":"https://familjehem.example/updates/yuvomi-android-0.1.0.apk","size":123,"digest":"sha256:64_HEXTECKEN"}]}]
```

Ingen GitHub-kontroll görs av uppdateraren. Signaturen kontrolleras av Androids
paketinstallerare; nedladdningen kräver SHA256. Installationen kräver användarens
aktiva godkännande. Testa uppgradering mellan två versioner med samma nyckel på
en riktig telefon innan skarp användning.

Projects och Us ska implementeras som separata tjänster med egna native skärmar
först när första leveransens samtliga acceptanskriterier är uppfyllda.
