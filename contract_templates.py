def get_templates():
    """
    Retourneert een lijst van beschikbare contractsjablonen voor gebruik in de applicatie.
    
    Returns:
        list: Een lijst van dictionaries met sjabloongegevens
    """
    templates = [
        {
            'id': 'algemene_voorwaarden',
            'name': 'Algemene Voorwaarden',
            'description': 'Standaard algemene voorwaarden voor uw dienstverlening.',
            'content': """
<h2>ALGEMENE VOORWAARDEN</h2>

<h3>Artikel 1. Definities</h3>
<p>In deze algemene voorwaarden worden de hiernavolgende termen in de navolgende betekenis gebruikt, tenzij uitdrukkelijk anders is aangegeven:</p>
<ol>
    <li><strong>Bedrijf:</strong> [BEDRIJFSNAAM], gevestigd te [VESTIGINGSPLAATS].</li>
    <li><strong>Klant:</strong> De wederpartij van Bedrijf, handelend in de uitoefening van beroep of bedrijf.</li>
    <li><strong>Overeenkomst:</strong> De overeenkomst tussen Bedrijf en Klant.</li>
</ol>

<h3>Artikel 2. Toepasselijkheid</h3>
<p>1. Deze voorwaarden zijn van toepassing op alle aanbiedingen, offertes en overeenkomsten tussen Bedrijf en Klant.</p>
<p>2. Afwijkingen van deze voorwaarden zijn slechts geldig indien deze uitdrukkelijk schriftelijk zijn overeengekomen.</p>

<h3>Artikel 3. Offertes en aanbiedingen</h3>
<p>1. Alle offertes en aanbiedingen van Bedrijf zijn vrijblijvend, tenzij in de offerte een termijn voor aanvaarding is gesteld.</p>
<p>2. Offertes van Bedrijf zijn gebaseerd op de informatie die door de Klant is verstrekt. De Klant staat ervoor in dat hij naar beste weten alle relevante informatie heeft verstrekt.</p>

<h3>Artikel 4. Uitvoering van de overeenkomst</h3>
<p>1. Bedrijf zal de overeenkomst naar beste inzicht en vermogen en overeenkomstig de eisen van goed vakmanschap uitvoeren.</p>
<p>2. Indien en voor zover een goede uitvoering van de overeenkomst dit vereist, heeft Bedrijf het recht bepaalde werkzaamheden te laten verrichten door derden.</p>

<h3>Artikel 5. Wijziging van de overeenkomst</h3>
<p>1. Indien tijdens de uitvoering van de overeenkomst blijkt dat het voor een behoorlijke uitvoering daarvan noodzakelijk is om deze te wijzigen of aan te vullen, dan zullen partijen tijdig en in onderling overleg tot aanpassing van de overeenkomst overgaan.</p>

<h3>Artikel 6. Betaling en incassokosten</h3>
<p>1. Betaling dient te geschieden binnen 30 dagen na factuurdatum, op een door Bedrijf aan te geven wijze in de valuta waarin is gefactureerd.</p>
<p>2. Indien de Klant in gebreke blijft in de tijdige betaling van een factuur, dan is de Klant van rechtswege in verzuim.</p>

<h3>Artikel 7. Aansprakelijkheid</h3>
<p>1. Bedrijf is niet aansprakelijk voor schade, van welke aard ook, ontstaan doordat Bedrijf is uitgegaan van door of namens de Klant verstrekte onjuiste en/of onvolledige gegevens.</p>

<h3>Artikel 8. Vrijwaring</h3>
<p>1. De Klant vrijwaart Bedrijf voor eventuele aanspraken van derden, die in verband met de uitvoering van de overeenkomst schade lijden en waarvan de oorzaak aan andere dan aan Bedrijf toerekenbaar is.</p>

<h3>Artikel 9. Toepasselijk recht en geschillen</h3>
<p>1. Op alle rechtsbetrekkingen waarbij Bedrijf partij is, is uitsluitend het Nederlands recht van toepassing.</p>
<p>2. De rechter in de vestigingsplaats van Bedrijf is bij uitsluiting bevoegd van geschillen kennis te nemen, tenzij de wet dwingend anders voorschrijft.</p>
            """
        },
        {
            'id': 'dienstverleningsovereenkomst',
            'name': 'Dienstverleningsovereenkomst',
            'description': 'Sjabloon voor een overeenkomst voor het leveren van diensten.',
            'content': """
<h2>DIENSTVERLENINGSOVEREENKOMST</h2>

<p>Deze dienstverleningsovereenkomst (de "Overeenkomst") is gesloten op [DATUM] tussen:</p>

<p><strong>1. [BEDRIJFSNAAM]</strong>, gevestigd te [ADRES], ingeschreven bij de Kamer van Koophandel onder nummer [KVK NUMMER], hierna te noemen: "Dienstverlener",</p>

<p>en</p>

<p><strong>2. [KLANTNAAM]</strong>, gevestigd te [ADRES], ingeschreven bij de Kamer van Koophandel onder nummer [KVK NUMMER], hierna te noemen: "Klant",</p>

<p>gezamenlijk te noemen: "Partijen"</p>

<h3>Artikel 1. Diensten</h3>
<p>1.1 Dienstverlener zal de volgende diensten aan Klant leveren:</p>
<p>[BESCHRIJVING VAN DE DIENSTEN]</p>

<h3>Artikel 2. Duur en beëindiging</h3>
<p>2.1 Deze Overeenkomst wordt aangegaan voor de periode van [PERIODE] ingaande op [STARTDATUM] en eindigend op [EINDDATUM].</p>
<p>2.2 Na afloop van de in artikel 2.1 genoemde periode wordt deze Overeenkomst automatisch verlengd met perioden van [PERIODE], tenzij een van de Partijen de Overeenkomst schriftelijk opzegt met inachtneming van een opzegtermijn van [OPZEGTERMIJN].</p>

<h3>Artikel 3. Vergoeding en betaling</h3>
<p>3.1 Voor de in artikel 1 genoemde diensten betaalt Klant aan Dienstverlener een vergoeding van [BEDRAG] exclusief BTW.</p>
<p>3.2 Dienstverlener zal voor de vergoeding [PER PERIODE] een factuur sturen aan Klant.</p>
<p>3.3 Klant zal de facturen van Dienstverlener binnen [BETALINGSTERMIJN] na factuurdatum betalen.</p>

<h3>Artikel 4. Verplichtingen Dienstverlener</h3>
<p>4.1 Dienstverlener zal de diensten naar beste kunnen uitvoeren en daarbij de zorgvuldigheid in acht nemen die van een professionele dienstverlener mag worden verwacht.</p>
<p>4.2 Dienstverlener zal Klant op de hoogte houden van de uitvoering van de diensten en onverwijld informeren over feiten en omstandigheden die tot vertraging of problemen kunnen leiden.</p>

<h3>Artikel 5. Verplichtingen Klant</h3>
<p>5.1 Klant zal Dienstverlener tijdig alle informatie verschaffen die nodig is voor een correcte uitvoering van de diensten.</p>
<p>5.2 Klant zal alle medewerking verlenen die redelijkerwijs van hem kan worden verwacht voor een correcte uitvoering van de diensten.</p>

<h3>Artikel 6. Vertrouwelijkheid</h3>
<p>6.1 Partijen zullen alle vertrouwelijke informatie die zij in het kader van deze Overeenkomst van elkaar ontvangen, vertrouwelijk behandelen en niet aan derden verstrekken zonder voorafgaande schriftelijke toestemming van de andere Partij.</p>

<h3>Artikel 7. Aansprakelijkheid</h3>
<p>7.1 De aansprakelijkheid van Dienstverlener is beperkt tot directe schade en tot maximaal het bedrag dat door Klant aan Dienstverlener is betaald in de zes maanden voorafgaand aan het schadetoebrengende feit.</p>
<p>7.2 Dienstverlener is niet aansprakelijk voor indirecte schade, waaronder gevolgschade, gederfde winst, gemiste besparingen en schade door bedrijfsstagnatie.</p>

<h3>Artikel 8. Toepasselijk recht en geschillen</h3>
<p>8.1 Op deze Overeenkomst is Nederlands recht van toepassing.</p>
<p>8.2 Alle geschillen die voortvloeien uit of verband houden met deze Overeenkomst zullen worden voorgelegd aan de bevoegde rechter in [PLAATS].</p>

<p>Aldus overeengekomen en in tweevoud opgemaakt en ondertekend te [PLAATS] op [DATUM].</p>

<table width="100%">
<tr>
<td width="50%">
<p>Namens Dienstverlener:</p>
<p>Naam: _______________________</p>
<p>Functie: _____________________</p>
<p>Handtekening: ________________</p>
</td>
<td width="50%">
<p>Namens Klant:</p>
<p>Naam: _______________________</p>
<p>Functie: _____________________</p>
<p>Handtekening: ________________</p>
</td>
</tr>
</table>
            """
        },
        {
            'id': 'offerte',
            'name': 'Offerte',
            'description': 'Sjabloon voor een professionele offerte.',
            'content': """
<h2>OFFERTE</h2>

<p>Datum: [DATUM]</p>
<p>Offertenummer: [NUMMER]</p>

<h3>Van:</h3>
<p>[BEDRIJFSNAAM]<br>
[ADRES]<br>
[POSTCODE + PLAATS]<br>
KVK: [KVK NUMMER]<br>
BTW: [BTW NUMMER]</p>

<h3>Aan:</h3>
<p>[KLANTNAAM]<br>
[ADRES]<br>
[POSTCODE + PLAATS]</p>

<h3>Betreft: [ONDERWERP]</h3>

<p>Geachte [AANHEF],</p>

<p>Hierbij doe ik u met genoegen een offerte toekomen voor [OMSCHRIJVING].</p>

<h3>Omschrijving van de werkzaamheden</h3>
<p>[GEDETAILLEERDE BESCHRIJVING VAN DE WERKZAAMHEDEN]</p>

<h3>Specificatie</h3>
<table width="100%" border="1" cellpadding="5" cellspacing="0">
<tr>
  <th>Omschrijving</th>
  <th>Aantal</th>
  <th>Eenheidsprijs (excl. BTW)</th>
  <th>Totaal (excl. BTW)</th>
</tr>
<tr>
  <td>[PRODUCT/DIENST 1]</td>
  <td>[AANTAL 1]</td>
  <td>&euro; [PRIJS 1]</td>
  <td>&euro; [TOTAAL 1]</td>
</tr>
<tr>
  <td>[PRODUCT/DIENST 2]</td>
  <td>[AANTAL 2]</td>
  <td>&euro; [PRIJS 2]</td>
  <td>&euro; [TOTAAL 2]</td>
</tr>
<tr>
  <td colspan="3" align="right"><strong>Subtotaal</strong></td>
  <td>&euro; [SUBTOTAAL]</td>
</tr>
<tr>
  <td colspan="3" align="right"><strong>BTW (21%)</strong></td>
  <td>&euro; [BTW BEDRAG]</td>
</tr>
<tr>
  <td colspan="3" align="right"><strong>Totaalbedrag (incl. BTW)</strong></td>
  <td>&euro; [TOTAALBEDRAG]</td>
</tr>
</table>

<h3>Planning</h3>
<p>Aanvang werkzaamheden: [STARTDATUM]<br>
Verwachte opleverdatum: [EINDDATUM]</p>

<h3>Betalingsvoorwaarden</h3>
<p>Betaling dient te geschieden binnen 30 dagen na factuurdatum op rekeningnummer [REKENINGNUMMER] t.n.v. [REKENINGHOUDER] onder vermelding van het offertenummer.</p>

<h3>Geldigheid offerte</h3>
<p>Deze offerte is geldig tot [GELDIGHEID], 30 dagen na dagtekening.</p>

<h3>Acceptatie</h3>
<p>Voor akkoord:</p>
<p>Naam: _______________________</p>
<p>Functie: _____________________</p>
<p>Datum: ______________________</p>
<p>Handtekening: ________________</p>

<p>Wij hopen u hiermee een passende aanbieding te hebben gedaan. Mocht u nog vragen hebben over deze offerte, dan kunt u contact opnemen via [CONTACTGEGEVENS].</p>

<p>Met vriendelijke groet,</p>
<p>[NAAM]<br>
[FUNCTIE]<br>
[BEDRIJFSNAAM]</p>
            """
        },
        {
            'id': 'verwerkersovereenkomst',
            'name': 'Verwerkersovereenkomst (AVG)',
            'description': 'Sjabloon voor een verwerkersovereenkomst conform de AVG.',
            'content': """
<h2>VERWERKERSOVEREENKOMST</h2>

<p>De ondergetekenden:</p>

<p><strong>1. [KLANTNAAM]</strong>, gevestigd te [ADRES], ingeschreven bij de Kamer van Koophandel onder nummer [KVK NUMMER], hierna te noemen: "Verwerkingsverantwoordelijke",</p>

<p>en</p>

<p><strong>2. [BEDRIJFSNAAM]</strong>, gevestigd te [ADRES], ingeschreven bij de Kamer van Koophandel onder nummer [KVK NUMMER], hierna te noemen: "Verwerker",</p>

<p>gezamenlijk te noemen: "Partijen"</p>

<p><strong>Overwegende dat:</strong></p>

<ul>
    <li>Partijen een overeenkomst hebben gesloten met betrekking tot [OMSCHRIJVING DIENSTEN], hierna te noemen: "Hoofdovereenkomst";</li>
    <li>Verwerker bij de uitvoering van de Hoofdovereenkomst persoonsgegevens in de zin van artikel 4 lid 1 van de Algemene Verordening Gegevensbescherming (hierna: "AVG") verwerkt;</li>
    <li>Verwerkingsverantwoordelijke voor deze verwerkingen als verwerkingsverantwoordelijke in de zin van artikel 4 lid 7 AVG is aan te merken;</li>
    <li>Partijen in overeenstemming met artikel 28 lid 3 AVG hun rechten en plichten met betrekking tot de verwerkingen van persoonsgegevens willen vastleggen in deze verwerkersovereenkomst (hierna: "Verwerkersovereenkomst").</li>
</ul>

<p><strong>Komen overeen als volgt:</strong></p>

<h3>Artikel 1. Definities</h3>
<p>In deze Verwerkersovereenkomst wordt verstaan onder:</p>
<ol>
    <li>AVG: de Algemene Verordening Gegevensbescherming;</li>
    <li>Betrokkene: degene op wie een Persoonsgegeven betrekking heeft;</li>
    <li>Persoonsgegevens: alle informatie over een geïdentificeerde of identificeerbare natuurlijke persoon (de Betrokkene); als identificeerbaar wordt beschouwd een natuurlijke persoon die direct of indirect kan worden geïdentificeerd;</li>
    <li>Verwerking: een bewerking of een geheel van bewerkingen met betrekking tot Persoonsgegevens of een geheel van Persoonsgegevens, al dan niet uitgevoerd via geautomatiseerde procedés, zoals het verzamelen, vastleggen, ordenen, structureren, opslaan, bijwerken of wijzigen, opvragen, raadplegen, gebruiken, verstrekken door middel van doorzending, verspreiden of op andere wijze ter beschikking stellen, aligneren of combineren, afschermen, wissen of vernietigen van gegevens.</li>
</ol>

<h3>Artikel 2. Voorwerp van de Verwerkersovereenkomst</h3>
<p>2.1 Verwerker verwerkt in opdracht van Verwerkingsverantwoordelijke Persoonsgegevens van Betrokkenen ten behoeve van de uitvoering van de Hoofdovereenkomst.</p>
<p>2.2 De categorieën Betrokkenen, het soort Persoonsgegevens en de aard en het doel van de Verwerking zijn nader omschreven in Bijlage 1 bij deze Verwerkersovereenkomst.</p>

<h3>Artikel 3. Verplichtingen Verwerker</h3>
<p>3.1 Verwerker verwerkt de Persoonsgegevens uitsluitend op basis van gedocumenteerde instructies van Verwerkingsverantwoordelijke, tenzij Verwerker op grond van Unierecht of lidstatelijk recht tot de Verwerking gehouden is.</p>
<p>3.2 Verwerker waarborgt dat de tot het verwerken van de Persoonsgegevens gemachtigde personen zich ertoe hebben verbonden vertrouwelijkheid in acht te nemen of door een passende wettelijke verplichting aan vertrouwelijkheid zijn gebonden.</p>
<p>3.3 Verwerker neemt alle passende technische en organisatorische maatregelen om een op het risico afgestemd beveiligingsniveau te waarborgen, zoals beschreven in Bijlage 2 bij deze Verwerkersovereenkomst.</p>
<p>3.4 Verwerker helpt Verwerkingsverantwoordelijke bij het vervullen van diens plicht om verzoeken van Betrokkenen, die hun rechten uitoefenen onder de AVG, te beantwoorden.</p>
<p>3.5 Verwerker helpt Verwerkingsverantwoordelijke bij het doen nakomen van de verplichtingen uit hoofde van artikelen 32 tot en met 36 AVG, rekening houdend met de aard van de verwerking en de hem ter beschikking staande informatie.</p>

<h3>Artikel 4. Subverwerkers</h3>
<p>4.1 Verwerker schakelt geen andere verwerker (subverwerker) in zonder voorafgaande specifieke of algemene schriftelijke toestemming van Verwerkingsverantwoordelijke.</p>
<p>4.2 In geval van algemene schriftelijke toestemming, zal Verwerker Verwerkingsverantwoordelijke informeren over beoogde veranderingen inzake de toevoeging of vervanging van subverwerkers.</p>
<p>4.3 Wanneer Verwerker een subverwerker inschakelt, legt hij aan deze subverwerker bij een overeenkomst dezelfde verplichtingen inzake gegevensbescherming op als die welke in deze Verwerkersovereenkomst zijn opgenomen.</p>

<h3>Artikel 5. Datalekken</h3>
<p>5.1 In geval van een inbreuk in verband met persoonsgegevens (datalek) informeert Verwerker Verwerkingsverantwoordelijke hierover zonder onredelijke vertraging, doch uiterlijk binnen 24 uur na kennisname van het datalek.</p>
<p>5.2 De melding bevat ten minste de informatie als beschreven in artikel 33 lid 3 AVG, voor zover deze informatie aan Verwerker bekend is.</p>

<h3>Artikel 6. Audit</h3>
<p>6.1 Verwerker stelt alle informatie ter beschikking die nodig is om de nakoming van de in artikel 28 AVG neergelegde verplichtingen aan te tonen en audits, waaronder inspecties, door Verwerkingsverantwoordelijke of een door Verwerkingsverantwoordelijke gemachtigde controleur mogelijk maakt en eraan bijdraagt.</p>

<h3>Artikel 7. Beëindiging</h3>
<p>7.1 Na afloop van de verwerkingsdiensten, wist of retourneert Verwerker, naargelang de keuze van Verwerkingsverantwoordelijke, alle Persoonsgegevens en verwijdert bestaande kopieën, tenzij opslag van de Persoonsgegevens Unierechtelijk of lidstaatrechtelijk is verplicht.</p>

<h3>Artikel 8. Slotbepalingen</h3>
<p>8.1 Deze Verwerkersovereenkomst maakt integraal onderdeel uit van de Hoofdovereenkomst.</p>
<p>8.2 In geval van strijdigheid tussen de bepalingen uit deze Verwerkersovereenkomst en de bepalingen uit de Hoofdovereenkomst, prevaleren de bepalingen uit deze Verwerkersovereenkomst.</p>
<p>8.3 Op deze Verwerkersovereenkomst is Nederlands recht van toepassing.</p>
<p>8.4 Geschillen die voortvloeien uit of verband houden met deze Verwerkersovereenkomst worden voorgelegd aan de bevoegde rechter in [PLAATS].</p>

<p>Aldus overeengekomen en in tweevoud opgemaakt en ondertekend te [PLAATS] op [DATUM].</p>

<table width="100%">
<tr>
<td width="50%">
<p>Namens Verwerkingsverantwoordelijke:</p>
<p>Naam: _______________________</p>
<p>Functie: _____________________</p>
<p>Handtekening: ________________</p>
</td>
<td width="50%">
<p>Namens Verwerker:</p>
<p>Naam: _______________________</p>
<p>Functie: _____________________</p>
<p>Handtekening: ________________</p>
</td>
</tr>
</table>

<h3>BIJLAGE 1: SPECIFICATIE PERSOONSGEGEVENS EN BETROKKENEN</h3>
<p>Categorieën Betrokkenen:</p>
<ul>
    <li>[BIJVOORBEELD: Klanten, medewerkers, bezoekers website]</li>
</ul>

<p>Soort Persoonsgegevens:</p>
<ul>
    <li>[BIJVOORBEELD: Naam, adres, e-mailadres, telefoonnummer]</li>
</ul>

<p>Aard en doel van de Verwerking:</p>
<ul>
    <li>[BIJVOORBEELD: Administratie van klantgegevens, facturering, klantenservice]</li>
</ul>

<h3>BIJLAGE 2: BESCHRIJVING BEVEILIGINGSMAATREGELEN</h3>
<p>Verwerker heeft in ieder geval de volgende technische en organisatorische beveiligingsmaatregelen getroffen:</p>
<ul>
    <li>[BIJVOORBEELD: Versleuteling van gegevens, toegangsbeveiliging, pseudonimisering van gegevens, regelmatige backups]</li>
</ul>
            """
        }
    ]
    
    return templates