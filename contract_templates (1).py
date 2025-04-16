def get_templates():
    """
    Retourneert een lijst van beschikbare contractsjablonen voor gebruik in de applicatie.
    
    Returns:
        list: Een lijst van dictionaries met sjabloongegevens
    """
    templates = [
        {
            'id': 'algemene_voorwaarden',
            'name': 'Algemene voorwaarden',
            'content': """<h1>Algemene voorwaarden</h1>
            
<p>Deze algemene voorwaarden zijn van toepassing op alle aanbiedingen en overeenkomsten waarbij {{ customer.company or customer.name }} diensten van welke aard dan ook aan {{ customer.name }} levert, ook indien deze diensten niet (nader) in deze voorwaarden zijn omschreven.</p>

<h2>1. Definities</h2>
<p>1.1 Aanbieder: {{ customer.company or customer.name }}, gevestigd te {{ customer.city }}, ingeschreven bij de Kamer van Koophandel onder nummer {{ customer.kvk_number or '[KVK-nummer]' }}.</p>
<p>1.2 Klant: de natuurlijke of rechtspersoon die met Aanbieder een overeenkomst heeft gesloten.</p>
<p>1.3 Diensten: alle door Aanbieder aan Klant geleverde producten en diensten, alsmede alle andere door Aanbieder ten behoeve van Klant verrichte werkzaamheden, van welke aard dan ook, verricht in het kader van een opdracht, waaronder begrepen werkzaamheden die niet op uitdrukkelijk verzoek van Klant worden verricht.</p>

<h2>2. Toepasselijkheid</h2>
<p>2.1 Deze algemene voorwaarden zijn van toepassing op alle aanbiedingen en overeenkomsten waarbij Aanbieder Diensten aanbiedt of levert.</p>
<p>2.2 Afwijkingen en aanvullingen van deze algemene voorwaarden zijn slechts geldig indien deze schriftelijk tussen partijen zijn overeengekomen.</p>
<p>2.3 De toepasselijkheid van eventuele inkoop- of andere voorwaarden van Klant wordt uitdrukkelijk van de hand gewezen.</p>

<h2>3. Prijzen en betaling</h2>
<p>3.1 Alle prijzen zijn exclusief omzetbelasting (BTW) en andere heffingen welke van overheidswege worden opgelegd.</p>
<p>3.2 Betalingen dienen te geschieden binnen veertien (14) dagen na factuurdatum, tenzij schriftelijk anders is overeengekomen.</p>
<p>3.3 Indien de Klant de verschuldigde bedragen niet binnen de overeengekomen termijn betaalt, is Klant, zonder dat enige ingebrekestelling nodig is, over het openstaande bedrag wettelijke rente verschuldigd.</p>

<h2>4. Vertrouwelijkheid</h2>
<p>4.1 Partijen dragen er zorg voor dat alle van de andere partij ontvangen gegevens waarvan men weet of redelijkerwijs behoort te weten dat deze van vertrouwelijke aard zijn, geheim blijven.</p>

<h2>5. Aansprakelijkheid</h2>
<p>5.1 De aansprakelijkheid van Aanbieder wegens toerekenbare tekortkoming in de nakoming van de overeenkomst is beperkt tot vergoeding van directe schade tot maximaal het bedrag van de voor die overeenkomst bedongen prijs (exclusief BTW).</p>

<h2>6. Toepasselijk recht en geschillen</h2>
<p>6.1 De overeenkomsten tussen Aanbieder en Klant worden beheerst door Nederlands recht.</p>
<p>6.2 Geschillen welke tussen Aanbieder en Klant mochten ontstaan naar aanleiding van een tussen Aanbieder en Klant gesloten overeenkomst dan wel naar aanleiding van nadere overeenkomsten die daarvan het gevolg zijn, worden beslecht door middel van arbitrage volgens het Arbitragereglement van de Stichting Geschillenoplossing Automatisering, één en ander onverminderd het recht van partijen een voorziening in arbitraal kort geding te vragen.</p>

<h2>7. Slotbepaling</h2>
<p>7.1 Deze voorwaarden treden in werking op {{ current_date }} en zijn gedeponeerd bij de Kamer van Koophandel.</p>
"""
        },
        {
            'id': 'dienstverleningsovereenkomst',
            'name': 'Dienstverleningsovereenkomst',
            'content': """<h1>Dienstverleningsovereenkomst</h1>

<p>De ondergetekenden:</p>

<p>{{ customer.company or customer.name }}, gevestigd te {{ customer.city }}, {{ customer.address }} {{ customer.postal_code }}, ingeschreven bij de Kamer van Koophandel onder nummer {{ customer.kvk_number or '[KVK-nummer]' }}, hierna te noemen: "Opdrachtnemer",</p>

<p>en</p>

<p>Onze Onderneming B.V., gevestigd te Amsterdam, Keizersgracht 123, 1015 CW, ingeschreven bij de Kamer van Koophandel onder nummer 12345678, hierna te noemen: "Opdrachtgever",</p>

<p>Gezamenlijk te noemen: "Partijen"</p>

<p>In aanmerking nemende dat:</p>
<ul>
    <li>Opdrachtgever werkzaam is op het gebied van consultancy en ICT-dienstverlening;</li>
    <li>Opdrachtnemer als zelfstandig ondernemer diensten op het gebied van IT-consultancy aanbiedt;</li>
    <li>Opdrachtgever gebruik wenst te maken van de diensten van Opdrachtnemer;</li>
    <li>Partijen uitsluitend met elkaar wensen te contracteren op basis van een overeenkomst van opdracht in de zin van artikel 7:400 e.v. BW;</li>
</ul>

<p>Komen als volgt overeen:</p>

<h2>Artikel 1: Opdracht</h2>
<p>1.1 Opdrachtnemer verplicht zich voor de duur van de overeenkomst de navolgende werkzaamheden te verrichten: [beschrijving werkzaamheden].</p>

<h2>Artikel 2: Duur van de overeenkomst</h2>
<p>2.1 De opdracht vangt aan op [startdatum] en wordt aangegaan voor [bepaalde/onbepaalde] tijd.</p>
<p>2.2 Deze overeenkomst kan door beide partijen worden beëindigd met inachtneming van een opzegtermijn van [aantal] maanden.</p>

<h2>Artikel 3: Vergoeding</h2>
<p>3.1 Opdrachtgever betaalt Opdrachtnemer € [bedrag] exclusief BTW per [uur/dag/maand].</p>
<p>3.2 Opdrachtnemer zal voor de verrichte werkzaamheden aan Opdrachtgever een factuur zenden. De factuur zal voldoen aan de wettelijke vereisten.</p>
<p>3.3 Opdrachtgever betaalt het gefactureerde bedrag aan Opdrachtnemer binnen 30 dagen na ontvangst van de factuur.</p>

<h2>Artikel 4: Geheimhouding</h2>
<p>4.1 Opdrachtnemer is verplicht tot geheimhouding van alle vertrouwelijke informatie die hij in het kader van de overeenkomst van Opdrachtgever of uit andere bron heeft verkregen.</p>

<h2>Artikel 5: Toepasselijk recht en geschillen</h2>
<p>5.1 Op deze overeenkomst is Nederlands recht van toepassing.</p>
<p>5.2 Geschillen voortvloeiende uit of verband houdende met deze overeenkomst zullen worden voorgelegd aan de bevoegde rechter in het arrondissement waar Opdrachtgever gevestigd is.</p>

<p>Aldus overeengekomen en getekend in tweevoud:</p>

<p>Plaats: ____________________ Datum: ____________________</p>

<p>Opdrachtgever:                             Opdrachtnemer:</p>
<p>_____________________               _____________________</p>
<p>(handtekening)                              (handtekening)</p>
"""
        },
        {
            'id': 'geheimhoudingsverklaring',
            'name': 'Geheimhoudingsverklaring',
            'content': """<h1>Geheimhoudingsverklaring</h1>

<p>DE ONDERGETEKENDEN:</p>

<p>1. {{ customer.company or customer.name }}, gevestigd te {{ customer.city }}, {{ customer.address or '' }} {{ customer.postal_code or '' }}, {{ customer.country }}, ingeschreven bij de Kamer van Koophandel onder nummer {{ customer.kvk_number or '[KVK-nummer]' }}, rechtsgeldig vertegenwoordigd door de heer/mevrouw {{ customer.name }}, hierna te noemen 'Partij A',</p>

<p>en</p>

<p>2. Onze Onderneming B.V., gevestigd te Amsterdam, ingeschreven bij de Kamer van Koophandel onder nummer 12345678, rechtsgeldig vertegenwoordigd door de heer Jan Janssen, hierna te noemen 'Partij B',</p>

<p>gezamenlijk te noemen 'Partijen'</p>

<p>OVERWEGENDE DAT:</p>

<p>- Partijen met elkaar in gesprek zijn met het oog op het eventueel aangaan van een samenwerkingsovereenkomst, hierna te noemen de 'Samenwerking';</p>
<p>- Partijen in verband met deze Samenwerking vertrouwelijke informatie zullen uitwisselen;</p>
<p>- Partijen de vertrouwelijkheid van de vertrouwelijke informatie wensen te waarborgen;</p>

<p>KOMEN ALS VOLGT OVEREEN:</p>

<h2>Artikel 1 - Definities</h2>
<p>In deze Geheimhoudingsverklaring wordt verstaan onder:</p>
<p>a) 'Vertrouwelijke Informatie': alle informatie die door een Partij schriftelijk als vertrouwelijk is aangemerkt dan wel mondeling als vertrouwelijk is aangemerkt en vervolgens binnen 14 dagen schriftelijk als vertrouwelijk is bevestigd, alsmede alle informatie waarvan de ontvangende Partij redelijkerwijs moet begrijpen dat deze van vertrouwelijke aard is.</p>

<h2>Artikel 2 - Geheimhouding</h2>
<p>2.1 Partijen verbinden zich jegens elkaar tot strikte geheimhouding van alle Vertrouwelijke Informatie die zij van de andere Partij hebben ontvangen of zullen ontvangen.</p>
<p>2.2 Partijen zullen de Vertrouwelijke Informatie uitsluitend gebruiken voor de Samenwerking en niet voor andere doeleinden.</p>
<p>2.3 Partijen zullen passende maatregelen nemen om de Vertrouwelijke Informatie te beschermen tegen ongeautoriseerde toegang of gebruik.</p>

<h2>Artikel 3 - Uitzonderingen</h2>
<p>De verplichtingen tot geheimhouding zijn niet van toepassing op Vertrouwelijke Informatie waarvan de ontvangende Partij kan aantonen dat deze:</p>
<p>a) reeds in het bezit was van de ontvangende Partij voordat deze van de andere Partij werd ontvangen;</p>
<p>b) onafhankelijk is ontwikkeld door de ontvangende Partij zonder gebruik te maken van de Vertrouwelijke Informatie van de andere Partij;</p>
<p>c) algemeen bekend is of wordt, anders dan door toedoen van de ontvangende Partij;</p>
<p>d) van een derde is ontvangen zonder dat daarbij een verplichting tot geheimhouding is opgelegd.</p>

<h2>Artikel 4 - Duur</h2>
<p>4.1 De verplichtingen uit deze Geheimhoudingsverklaring blijven van kracht voor een periode van 3 (drie) jaar na ondertekening, ook indien de gesprekken over de Samenwerking worden beëindigd of de Samenwerking niet tot stand komt.</p>

<h2>Artikel 5 - Toepasselijk recht en geschillen</h2>
<p>5.1 Op deze Geheimhoudingsverklaring is Nederlands recht van toepassing.</p>
<p>5.2 Alle geschillen die voortvloeien uit of verband houden met deze Geheimhoudingsverklaring zullen worden voorgelegd aan de bevoegde rechter te Amsterdam.</p>

<p>ALDUS OVEREENGEKOMEN EN ONDERTEKEND:</p>

<p>Partij A:                                        Partij B:</p>
<p>Naam: {{ customer.name }}                         Naam: Jan Janssen</p>
<p>Functie:                                          Functie: Directeur</p>
<p>Datum:                                            Datum:</p>
<p>Handtekening:                                     Handtekening:</p>
"""
        }
    ]
    
    return templates
