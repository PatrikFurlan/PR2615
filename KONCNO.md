# Analiza podatkov o prometnih nesrečah v Sloveniji (2014 - 2024)

### 1. Opis problema

Cilj projektne naloge je analiziranje prometne varnosti na slovenskih cestah s pomočjo podatkov zadnjega desetletja (2014 - 2024). Z analizo raziskujemo pogoste vzroke za nastanek prometnih nesreč in možne korelacije, ki pripomorejo k verjetnosti za nastanek. V sklopu analize smo odgovarjali na naslednja vprašanja:
- Na katere dneve v tednu se najpogosteje dogajajo nesreče?
- Ob katerih urah se zgodi največji delež nesreč?
- Kakšna je verjetnost nastanka nesreče s poškodbo glede na vremenske okoliščine?
- Kakšen je trend vožnje pod vplivom alkohola pri mlajših voznikih (populacija mlajša od 30)?
- So nesreče zunaj mest resnejše?
- So nesreče ponoči resnejše?
- Analiza žarišč prometnih nesreč glede na koordinate

### 2. Podatki in čiščenje

Podatke smo prenesli iz odprte baze evidenc, ki jih zbira policija na spletni strani ([policija.si](https://www.policija.si/o-slovenski-policiji/statistika/prometna-varnost)). Letna poročila so shranjena v posameznih .csv datotekah, ki jih je bilo pred analizo potrebno združiti v data frame, počistiti neveljavne vnose in premisliti o manjkajočih vrednostih.

Ključni koraki čiščenja podatkov:
1. **Združevanje:** Vsaka nesreča ima unikaten ID, ki se znotraj letnega poročila pojavi tolikokrat, kolikor je bilo udeležencev v tisti nesreči. Ker je ID nesreče samo inkrementalno število se lahko isti ID pojavi v vseh poročilih, zato smo vsaki nesreči dodelili unikaten ID v obliki **\<leto\>\_\<št\_nesreče\>**.

3. **Manjkajoče vrednost**: Vzrok manjkajočih vrednosti je bila pogosto napaka pri vnosu, ki se jo je dalo iz konteksta hitro ugotoviti.
    - Udeleženci s praznim atributom "UEStalnegaPrebivalisca" so bili večinoma državljani tujih držav, zato smo takim vnosom vnesli "TUJINA"
    - Pri manjkajočih vrednostih atributa "Starost" je bilo potrebno malo premisliti, saj bi imputacija lahko pomenila popačene podatke pri nadaljnjih analizah (npr. imputacija 0 bi pomenila, da so vsi taki udeleženci novorojenčki). Začasno smo te vrednosti pustili pri miru (možne rešitve bi bile naprimer imputacija mediane).

4. **Čiščenje podatkov:** Pri nekaterih atributih je bilo potrebno poenotiti zapise , saj so se za enako stanje pojavili različni zapisi. Navadno je bila razlika v velikih začetnicah ali obrnjenih besadah naprimer pri državi (Slovenija -> SLOVENIJA) ali pri stanju prometa (NORMALEN -> TEKOČ (NORMALEN))

5. **Normalizacija:** Nekateri vnosi so bili nesmiselni in jih je zato bilo potrebno omejiti. Primer takih vnosov so naprimer izredno visoki vozniški staži (nad 85 let), stopnja alkoholiziranosti nad 3 mg/l (kar se smatra kot smrtna doza) ... Take vnose smo smiselno omejili in višje vnose izbrisali.

Po korakih obdelave podatkov smo dobili povsem prečiščeno in enotno podatkovno zbirko, ki smo jo za potrebe nadaljne analize shranili v svojo .csv datoteko. 

### 3. Analiza

Tukaj so povzete samo glavne ugotovitve analiz in pomembnejše slike. Dodatni grafi, opisi in izvorna koda je opisana v sklopu Jupyter notebook zvezka.
<br>
- Jupyter notebook: https://github.com/PatrikFurlan/PR2615/blob/main/notebook.ipynb
- Interaktiven streamlit model: https://pr2615.streamlit.app/

#### 3.1. Porazdelitev glede na dan v tednu in uro

Pogledali smo si porazdelitev po dnevih v tednu in po urah, kjer smo za risanje grafa uporabili deleže prometnih nesreč, namesto dejanskih pojavov nesreč. Tako smo pri nesrečah po dnevih v tednu stolpce izračunali kot *(Število nesreč na posamezen dan / vse nesreče)*. Podobno smo računali tudi pri analizi po urah.
Prišli smo do večinoma pričakovanih rezultatov. Iz analize deležev nesreč glede na dan lahko razberemo, da se največ nesreč v podatkih pojavi ob petkih. Na splošno je med delavnikom več nesreč kot med vikendom, kjer so deleži veliko nižji. Kot pričakovano se največji delež nesreč zgodi popoldan med 15.00 in 16.00. 
Pridobljena grafa analize po dnevih in po urah smno združili v enoten vpogled v podatke z toplotno karto.

<img width="1621" height="690" alt="image" src="https://github.com/user-attachments/assets/60eec8c6-051c-4998-b0ba-c15997cb0d8a" />

#### 3.2. Verjetnost nastanka nesreče s poškodbo glede na vremenske okoliščine

<img width="1489" height="689" alt="image" src="https://github.com/user-attachments/assets/ef99213d-9c7f-4a1c-a38a-af756403a1b8" />

Pri analizi smo želeli ugotoviti korelacijo med prometnimi nesrečami, kjer je vsaj en udeleženec poškodovan in vremenskimi okoliščinami. Ker se velika večina vseh nesreč zgodi ob idealnih pogojih, smo podatke normalizirali. Verjetnost smo izračunali kot razmerje - **število nesreč s poškodbami v nekem vremenu / vse nesreče v nekem vremenu**. Ampak z rezultatom nismo povsem zadovoljni, saj vremenske okoliščine ne nujno vplivajo na cestišče. V podatkih je lahko prisotna nesreča, ki se je zgodila v jasnem vremenu, vendar je bil takrat na cesti prisoten sneg, kar bi našo analizo pokvarilo.

<img width="1489" height="690" alt="image" src="https://github.com/user-attachments/assets/60a7f1be-55a2-43da-8e1d-dbec8cb3773e" />

Zgornji graf nakazuje bolj realističen vpogled v podatke. Iz grafa je razvidno, da se več kot 40 procentov vseh nesreč na spolzkih cestah konča s poškodbo. Opazimo lahko tudi očitno razliko med neposipanim in posipanim cestiščem, ter razliko med pluženim in nepluženim.

Opazimo lahko tudi, da so vremenske okoliščine in stanja vozišč, ki ji navadno smatramo kot nevarnejša, nižje na lestvicah kot okoliščine, ki jih imamo za idealne. Sklepamo lahko, da so vozniki v zahtevnejših razmerah precej bolj previdni in bistveno počasnejši, kar zmanjšuje silovitost trčenj, čeprav je število manjših nesreč (npr. zdrsov) pri takih okoliščinah morda večje.

<img width="1175" height="590" alt="image" src="https://github.com/user-attachments/assets/5047bfc2-b87c-45a8-9a7b-0443a10eaa43" />

Predpostavko lahko podkrepimo z zgornjim grafom strukture resnosti nesreč. Opazimo lahko, da pri snežnem in mokrem vozišču prevladujejo nesreče z materialno škodo. 

Zanimiv je tudi podatek, da je verjetnost nastanka nesreče s hujšimi poškodbami ali smrtjo najvišja na blatnih cestah. Velja omeniti, da gre tukaj najpogosteje za makadamske ceste izven naselja, na katere povprečen voznik ne zahaja pogosto.

#### 3.3. Trend vožnje pod vplivom alkohola pri mlajših voznikih (<30)

Tukaj lahko opazujemo trend vožnje pod vplivom alkohola pri mladih (osebe stare < 30). Tudi tukaj smo točke na grafu predstavili kot deleže. Trend vožnje pod vplivom je kljub izjemam padajoč.
Velja opomniti tudi, da tej podatki prikazujejo vse voznike, ki so na alkotestu pokazali vrednosti večje od nič in ne samo tiste, ki so prekoračili zakonsko določeno mejo.

<img width="989" height="490" alt="image" src="https://github.com/user-attachments/assets/67f9c72a-fc97-4274-8b6e-d5c34323d75b" />

#### 3.4. Interaktivni model za napoved verjetnosti nastanka nesreče s hudimi poškodbami

Želeli smo izdelati model, ki bi na podlagi nekaj zanimivih atributov lahko podal verjetnost za nastanek nesreče s hudimi telesnimi poškodbami. Prvi prototip modela smo realizirali s pomočjo algoritma Naivni Bayes, za vizualizacijo pa smo uporabili nomogram v programu Orange. 

Rezultati so sicer izgledali obetavni, ampak nam način vizualizacije ni ustrezal, saj ne omogoča uporabnikom prijazne interakcije. Vizualizacijo in model smo preselili v streamlit kjer uporabnik lahko natančno določi vrednosti atributov, ki ga zanimajo. Aplikacija je dostopna na povezavi https://pr2615.streamlit.app/

#### 3.5 Model za identifikacijo žarišč

V podatkovni zbirki so poleg nesreč zabeležene tudi koordinate nesreče, kar nam omogoča izris posameznih nesreč na zemljevid, kot smo to storili v fazi preverjanja in čiščenja podatkov. 
Za izdelavo modela smo se odločili uporabiti algoritem HDBSCAN, ki je primeren za iskanje gruč v prostorskih podatkih. 

<img width="1182" height="1206" alt="image" src="https://github.com/user-attachments/assets/3aeb7655-335b-497e-b2b3-2d8a49b54def" />

Tukaj se osredotočimo na ranljivejše udeležence v prometu - pešče. Na podalagi koordinat v podatkih lahko z algoritmom HDBSCAN na zgornjem zemljevidu Ljubljane prikažemo vroče točke, kjer so v prometne nesreče najpogosteje udeleženi tudi pešči. Vidimo, da se te gruče nahajajo na conah z večjim številom pešcev, kot je naprimer center, glavne vpadnice in okolica univerzitetnega kliničnega centra.

Model deluje dobro ampak ni interaktiven in omejen na prikaz samo enega mesta. Želimo izdelati model, ki bo uporabniku omogočal interaktivno vnašanje zanimivih vrednosti atributov in parametrov algoritma HDBSCAN. To smo realizirali s streamlit aplikacijo, dostopno na naslovu https://pr2615.streamlit.app/

Napotki za nastavljanje parametrov algortima HDBSCAN:
- **Minimalna velikost gruče**: Parameter nastavimo na približno 1-2% vseh prikazanih nesreč
- **Minimalno število sosedov**: Če je število prikazanih nesreč visoko lahko parameter nastavimo na največ polovico vrednosti parametra *Minimalna velikost gruče*, boljše pa če je manj.

#### 3.6 So nesreče zunaj mest resnejše?

Pri tej analizi želimo pokazati, da so nesreče, ki se dogajajo izven naselji v povprečju hujše (njihov izzid je huda telesna poškodba ali smrt). 

<img width="790" height="590" alt="image" src="https://github.com/user-attachments/assets/d22236df-e383-4a2b-bd2f-bb8a3f7851c5" />

Iz grafa je razvidno, da se hude nesreče izven naselja pojavijo 1.5-krat pogosteje kot v naseljih.
Preveriti želimo, če je zgornji rezultat naključen ali dejansko statistično značilen, zato smo ga preverili z chi-square testom. Test je pokazal, da je verjetnost da so naši rezultati naključni tako majhna da je praktično nič, kar potrdi, da so nesreče izven naselji tipično hujše. Sklepamo, da temu pripomorajo višje hitrosti izven naselja in daljši odzivni času reševalnih služb.

#### 3.7 So nesreče ponoči resnejše?

Na podoben način želimo pokazati, da so nesreče, ki se zgodijo ponoči (23.00 - 4.59) hujše.

<img width="1389" height="490" alt="image" src="https://github.com/user-attachments/assets/f22117aa-d478-413f-9e2a-d0eb52536706" />

<img width="790" height="590" alt="image" src="https://github.com/user-attachments/assets/a0c1d3e7-942b-49f3-8449-96ecd4675e95" />

Na prvem grafu lahko vidimo da najbolj izstopa polnoč (~6.3%). Na drugem grafu vidimo, da je procentualno ponoči nekoliko več takih nesreč, ampak ali je to samo naključje? Poskusimo ponovno s chi-square testom. Chi-square test pokaže p = 0,13, kar pomeni, da razlika ni statistično značilna. Zaključimo lahko, da imajo nesreče med 0.00 in 2.00 v povprečju višji delež hudih posledic, vendar binarna primerjava dan/noč ne pokaže statistično značilne razlike.

