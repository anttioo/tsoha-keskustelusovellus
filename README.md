# tsoha-keskustelusovellus

Sovellus löytyy täältä: [tsoha-keskustelusovellus-ao](https://tsoha-keskustelusovellus-ao.herokuapp.com)


Admin tunnukset: 
   -  Käyttäjätunnus: admin
   -  Salasana: admin 

Toteutetaan esimerkin mukainen keskustelusovellus, eli toteutettavat ominaisuudet ovat:
 - [X] Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
 - [X] Käyttäjä näkee sovelluksen etusivulla listan alueista sekä jokaisen alueen ketjujen ja viestien määrän ja viimeksi lähetetyn viestin ajankohdan.
 - [X] Käyttäjä voi luoda alueelle uuden ketjun antamalla ketjun otsikon ja aloitusviestin sisällön.
 - [X] Käyttäjä voi kirjoittaa uuden viestin olemassa olevaan ketjuun.
 - [X] Kuka tahansa voi muokata ketjun otsikkoa sekä  viestien sisältöä. Käyttäjä voi myös poistaa ketjun tai viestin.
    - [X] Käyttäjä voi muokata luomansa ketjun otsikkoa sekä lähettämänsä viestin sisältöä. Käyttäjä voi myös poistaa ketjun tai viestin.
 - [X] Käyttäjä voi etsiä kaikki viestit, joiden osana on annettu sana.
 - [X] Kuka tahansa voi lisätä keskustelualueita
 - [X] Ylläpitäjä voi luoda salaisen alueen ja määrittää, keillä käyttäjillä on pääsy alueelle.
 - [x] Oikeuksen tarkistaminen kaikkialle minne se tarvitaan
 - [X] Templatet käyttöön fiksummin
 - [X] Käyttäjille roolit
 - [X] Refaktoroidaan db jutut ja routet erilleen


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