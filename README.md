# tsoha-keskustelusovellus

Toteutetaan esimerkin mukainen keskustelusovellus, eli toteutettavat ominaisuudet ovat:
 - [X] Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
 - [X] Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen ketjujen ja viestien määrän ja viimeksi lähetetyn viestin ajankohdan.
 - [X] Käyttäjä voi luoda alueelle uuden ketjun antamalla ketjun otsikon ja aloitusviestin sisällön.
 - [X] Käyttäjä voi kirjoittaa uuden viestin olemassa olevaan ketjuun.
 - [ ] Käyttäjä voi muokata luomansa ketjun otsikkoa sekä lähettämänsä viestin sisältöä. Käyttäjä voi myös poistaa ketjun tai viestin.
    - **Poistonappi on näkyvissä mutta ei toimi**
 - [ ] Käyttäjä voi etsiä kaikki viestit, joiden osana on annettu sana.
 - [X] Kuka tahansa voi lisätä ja poistaa keskustelualueita.
    - [ ] Vain ylläpitäjä voi lisätä ja poistaa keskustelualueita.
 - [ ] Ylläpitäjä voi luoda salaisen alueen ja määrittää, keillä käyttäjillä on pääsy alueelle.
 - [ ] Oikeuksen tarkistaminen kaikkialle minne se tarvitaan
 - [ ] Templatet käyttöön fiksummin
 - [ ] Käyttäjätunnuksen lisäksi käyttäjälle nimi, joka näkyy ylävalikossa
 - [ ] Käyttäjille roolit
 - [ ] Refaktoroidaan db jutut ja routet erilleen

## Heroku
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/
```

#### Rekisteröityminen
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/register
```

#### Kirjautuminen
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/login
```

#### Alueet
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/boards
```
Tänne voi luoda keskustelualueen, johon taas voi luoda threadeja

#### Alueet
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/boards/:board_id/threads
```
Listus alueen threadeista

#### Alueet
``` http
GET https://tsoha-keskustelusovellus-ao.herokuapp.com/threads/:thread_id
```
Threadin keskustelut