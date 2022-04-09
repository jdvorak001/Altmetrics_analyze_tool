# Altmetrics_analyze_tool
Tool for collecting and analyzing altmetric data
Tento program vznikl pro potřeby diplomové práce s názvem "Altmetrie a její využití při hodnocení vědeckého výzkumu". 

Program se skládá celkem ze dvou skriptů. Skript s názvem DP_process_data.py v první řadě prochází všechny dodané soubory ve formátu Endnote (.ciw) na jeho vstupní složce. Z těchto souborů extrahuje všechny potřebná data, pokud hledaná informace chybí, program místo ní doplní hodnotu „None“. V druhé řadě tento skript využívá přístupné API rozhraní služby PlumX a Altmetrics.com, na které vznáší požadavky obsahující DOI identifikátor získaný z předtím extrahovaného Endnote souboru. Při pozitivní odpovědi, která je vždy ve fromátu JSON, extrahuje hledaná data. V případě negativní odpovědi je vrácena hodnota „None“. Takto zpracované informace jsou zapsány do CSV souboru, který je výstupem tohoto skriptu (zároveň je výstupem i logfile, který zaznamenává informace o stavu zpracování záznamů). 
Druhým skriptem je DP_analyze_data.py. Vstup tohoto skriptu je zmíněný CSV soubor, jehož řádky jsou jednotlivé dokumenty a jehož sloupce jsou potřebná metadata dokumentu a současně také jednotlivé sledované identifikátory. Tyto data skript zpracovává a jeho výstupem jsou propočtené tabulky a vykreslené grafy, na jejichž základě byly zodpovězeny výzkumné otázky definované na předchozích stránkách této práce. 

## Vytvořený program používá následující knihovny:
### Pro automatizaci sběru dat:
•	request
•	os
•	json
•	time
•	datetime
•	textstat
### Pro statistickou analýzu dat:
•	pandas
•	numpy
•	sklearn
•	statsmodels.api
•	scipy
### K vizualizaci byly použity nástroje:
•	seaborn 
•	matplotlib

Používání programu
------------------
# DP_process_data.py

V případě prvního skriptu, tedy "DP_process_data.py", se volá funkce zpracuj_složku() pro vygenerování indikátorů a metadat všech souborů umístěných do vstupního adresáře.
Také je možné využít funkci zpracuj_soubor(), která vygeneruje data pouze pro jeden konkrétní soubor ve vstupním adresáři, jehož cesta se musí uvést jako argument funkce.

## funkce "zpracuj_složku()" a i "zpracuj_soubor()" disponuje následujícími argumenty:
* cesta_ke_slozce  --> cesta ke složce, kde jsou uložená data ve formátu Endnote
* altmetrics_on	--> vypínač a zapínač Altmetrics.com api. Pokud je True, stahuje to z tohoto api data
* plumX_on	--> vypínač a zapínač PlumX api. Pokud je True, stahuje to z tohoto api data
* nazev_generovaneho_souboru --> název csv souboru, který bude vygenerován
* start_from = 0 --> v případě že je potřeba začít procesovat data až od určitého záznamu (vhodné, pokud se v půlce zpracování přeruší a je nutné skript spustit znovu, nastaví se přímo záznam ve kterém to může rovnou začít a přeskočit to k němu)

Výstupem tohoto skriptu je log soubor a csv soubor. 

### CSV soubor má následující sloupce

* #list_AF                ->  seznam autorů, získané z pole AF (nepoužívá se)
* pocet_autoru            ->  počet autorů; zjištěn počet položek v poli "list_AF"
* list_DT                 ->  Typ dokumentu
* list_WC                 ->  kategorie WoS: https://images.webofknowledge.com/images/help/WOS/hp_subject_category_terms_tasca.html
* list_SC,                ->  kategorie oblasti výzkumu - "Research Areas": https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html
* research_categories,    ->  subkategorie z "list_SC" byly namapované na nadřazené kategorie, kterých je celkem jen 5
* interdistiplinarita,    ->  pokud článek disponuje více nadřazenýma kategoriema v listu "research_categories", tak je brán za mezioborový
* list_TC,                ->  počet citací z WoS (ačkoliv se jedna o klasický int, z nějakého důvodu ho mám v listu)
* open_access             ->  True nebo False -> indikuje jestli je článek OA
* list_OA,                ->  pokud je článek OA zde je informace o tom v jakém modu 
* list_PG,                ->  počet stránek článku
* #list_AB,               ->  abstrakt (z nějkého důvodu je v listu i když by asi být nemusel)(nepoužívá se)
* list_Flesch             ->  čitelnost abstraktu (Flesh koeficient https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
* pocet_slov_AB           ->  délka abstraktu
* mezinarodni_spoluprace  ->  True nebo False -> Pokud alespoň jeden z autorů pracuje pod institucí mimo ČR, tak True
* list_C1,                ->  seznam zemí autorů: z kompletní hodnoty je vyfiltrovaná pouze země samotná (bez města, atd..)
* list_TI,                ->  název článku (dohromady i s podnázvem)
* pocet_slov_TI           ->  délka názvu článku
* list_FU,                ->  seznam grantů
* funding                 ->  indikátor, jestli byl výzkum financován z grantu; True/False ; vychází z listu "list_FU"- pokud je prázdný tak False, jinak True
* doi                     ->  DOI článku - slouží hlavně pro vstup k API
* list_LA                 ->  jazyk dokumentu
* available_altmetrics    ->  TRUE nebo FALSE - říká, jestli je článek k dispozici ve službě Altmetrics.com
* tweetovani_altmetrics   ->  Altmetric.com | počet účtů na twitteru, které citovali článek
* fb_altmetrics           ->  Altmetric.com | počet stránek na FB, které sdílely článek
* blogy_altmetrics        ->  Altmetric.com | počet blogů ve kterých se objevil článek
* zpravy_altmetrics
* reddit_altmetrics
* video_altmetric         ->  Altmetric.com | Youtube a Vimeo
* mendeley_altmetrics
* score_altmetrics        ->  Altmetric.com | indikátor, který agreguje a váží všechna data
* available_plumx         ->  PlumX | TRUE nebo FALSE - říká, jestli je článek k dispozici ve službě PlumX
* capture                 ->  PlumX | Indicates that someone wants to come back to the work. Captures can be an leading indicator of future citations.
* citation                ->  PlumX |  This is a category that contains both traditional citation indexes such as Scopus, as well as citations that help indicate societal impact such as Clinical or Policy Citations.
* mentions                ->  PlumX | Measurement of activities such as news articles or blog posts about research. Mentions is a way to tell that people are truly engaging with the research.
* socialMedia             ->  PlumX | This category includes the tweets, Facebook likes, etc. that reference the research. Social Media can help measure “buzz” and attention.  Social media can also be a good measure of how well a particular piece of research has been promoted.
* usage                   ->  PlumX | A way to signal if anyone is reading the articles or otherwise using the research. Usage is the number one statistic researchers want to know after citations

V souboru log je možné vyčíst datum a čas zpracování každého jednotlivého záznamu; název zdrojového souboru, ze kterého daný záznam pochází; pořadí záznamu; DOI záznamu; a počet, kolik záznamů zatím nemělo k dispozici DOI a nemohly být tak zpracovány

# DP_analyze_data.py

V případě skriptu druhého, s názvem "DP_analyze_data.py" se pro jeho správné fungování volají následující funkce:

## zjisti_korelaci() - výstupem je vytisklá tabulka a graf

* data => naimportované data, csv soubor vygenerovaný z předchozího scriptu
* sloupec_A a sloupec_B => sloupce z dataframu, kde se hledají závislost - musí se jednat o indikátory
* typ korelace => 'spearman' 'pearson' 'kendall' (pro kendall typ není naprogramovaná vizualizace)
* vizualizace => True False #generuje graf*
* group_by = které hodnoty má seskupovat - vypočítá korelaci pro každou kategorii - pokud je vizualizace zapnuta, vytvoří graf pro každou kategorii
* minimum_clanku => používá se pouze v případě kdy group_by argument je využívaný. Říká, jaké procento dokumentů musí obsahovat kategorie, aby byla brána v potaz (například nemá cenu vykreslovat ty kategorie, do kterých spadájí jen 4 články, nemají pak výpovědní hodnotu)

př: zjisti_korelaci(df, "pole_TC", "mendeley_altmetrics",  typ_korelace="pearson", vizualizace=True, minimum_clanku=1, group_by="typ_dokumentu")



## zjisti_podil_dokumentu_v_agregatorech() - výstupem je vytisklá tabulka a graf

Zjištuje dostupnost v jednotlivých agregátorech
Umí to i GroupBy (pokud se do argumentu pro groupby vloží dvě kategorie oddělené čárkou, pak se data seskupí podle obou kategorií. př.: groupby="research_categories, list_DT")

* data => naimportované data, csv soubor vygenerovaný z předchozího scriptu
* groupby => které hodnoty má seskupovat (pokud se do argumentu pro groupby vloží dvě kategorie oddělené čárkou, pak se data seskupí podle obou kategorií. př.: groupby="research_categories, list_DT") /pro tento pokročilý případ to však neumí vizualizaci
* vizualizace => vykreslit graf - True, False
* minimum_clanku => používá se pouze v případě kdy group_by argument je využívaný. Říká, jaké procento dokumentů musí obsahovat kategorie, aby byla brána v potaz

př: zjisti_podil_dokumentu_v_agregatorech(df, groupby="funding", vizualizace=True, minimum_clanku=1)



## disciplinary_and_time_differences() - výstupem je vytislká tabulka a graf

zjištuje průměr nebo median indikátorů za jednotlivé roky, vykresluje graf. Zároveň zjišťuje o kolik % jednotlivé indikátory klesly. 
* data => naimportované data, csv soubor vygenerovaný z předchozího scriptu
* indikator => určuje, pro který indikátor se má vypočítat průměr nebo median a ten následně vykreslit
* groupby => podle čeho seskupovat do kategorií (povinný argument, v předchozích případech funkcí je totiž dobrovolný)
* median_or_mean => jestli má vypočítat průměr nebo median
* priprava_dat_vice_hodnoty => vždy True a neřešit :-)
* minimum_clanku => Říká, jaké procento dokumentů musí obsahovat kategorie, aby byla brána v potaz

př: disciplinary_and_time_differences(data, indikator, groupby, median_or_mean, priprava_dat_vice_hodnoty=True, minimum_clanku=False):



## get_different_rows(source_df, new_df, sledovany_indikator)
Vrací řádky ve kterých proběhla změna a současně vypočítá kolik řádků se změnilo
Na vstupu je původní dataset, nově naměřený dataset po určitém časovém období a určí se sledovaný indikátor, pro který se má sledovat změna.
(tzn. sledují se pouze změny pro jeden indikátor)
* Vylepšená verze této funkce je: plot_clustered_stacked(), která umí i grafy.

## zjisti_vlivne_faktory(data, indikator, faktor, vizualizace)
CÍLEM TÉTO FUNKCE JE ZJISTIT ZDALI ZKOUMANÝ FAKTOR NĚJAK OVLIVŇUJE HODNOTU INDIKÁTORU
př: zda-li počet stránek článku může mít vliv na hodnotu altmetric_score
* indikátor je závislá proměnná -> indikátor závisí na faktoru
* faktor je nezávislá proměnná
FUNKCE NEBYLA NIKDY POUŽITA. ČÁSTEČNĚ FUNGUJE ALE NENÍ DODĚLANÁ

## porovnej_faktory(data, faktor, indikator, test)
Funkce vypočítá průměry pro indikátor v množině dokumentu kde je zastoupený faktor a zároveň v množině dokumentu, kde faktor není zastoupený.
Současně počítá i test významnosti. Metoda testu může být buď studentův t-test nebo mann-withney test, případně wilcoxon test.
Funkce neumí vizualizaci. Funkce funguje na zavolání pouze pro jeden faktor a jeden indikátor. Pro analýzu všech indikátoru, využij funkci "vizualizace_vliv_faktoru_na_hodnotu_indikatoru", která umí i vizualizovat výsledek

## vizualizace_vliv_faktoru_na_hodnotu_indikatoru(df, faktor, typ_grafu, research_area = "")
Funkce vypočítává průměry pro množinu dokumentu ve kterých je zastoupen sledovaný faktor a pro množinu dokumentu ve kterých faktor chybí. Dál ke každému faktoru vypočte test významnosti, a spočítá počet výskytů a procentuelní nárust/pokles průměrné hodnoty
Funkce současně umí vykreslit graf - vykresluje dva typy grafu - typ_1 a typ_2
* typ_1 = jeden barplot, všechno se vešlo do jednoho grafu
* typ_2 = samostatný barplot pro každý indikátor -> toto je preferovaná verze
- df => poskytnutá data
- faktor => pro který faktor se budou grafy vypočítávat a vykreslovat
- typ_grafu => typ_1 nebo typ_2
- research_area => slouží pouze pro název grafu, jinak není nijak významný

## vizualizace_zmena_hodnot_indikatoru_po_druhem_mereni(data1, data2)
Vykresluje graf, ze kterého jsou patrné poklesy a nárůsty hodnot indikátorů pro všechny dokumenty.
Funguje to tak, že se vezme hodnota po druhém měření a odečte se od ní hodnot po prvním měření. Pokud je výsledk 0, tak dokument nezaznamenal změnu, pokud je výsledek >0 tak dokument zaznamenal nárůst, pokud je výsledek <0 tak dokument zaznamenal pokles
Vykreslují se rozdíly všech dokumentu a jsou seřazené od mínusových rozdílů do nejvíce plusových.
Na vstupu jsou datasety při prvním a druhém měření. Pro specifickou vědní oblast je nejdříve potřeba datasety vyfiltrovat zvlášť


## plot_clustered_stacked(dfall, labels=None, title="",  H="/", **kwargs)

Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
labels is a list of the names of the dataframe, used for the legend
title is a string for the title of the plot
H is the hatch used for identification of the different dataframe  
Převzato a upraveno: https://stackoverflow.com/questions/22787209/how-to-have-clusters-of-stacked-bars-with-python-pandas
* Funkce vykresluje graf, který vypovídá o změně hodnot jednotlivých dokumentů pro všechny indikátory. Zaznamenává pokles i nárůst. Celková velikost sloupce znamená kolik % dokumentu zaznamenalo nějakou změnu. 

### příklad použití:
#připrav si datasety
df_social = priprav_df_pro_prirustku_a_ubytku(df_social_sciences, df02_social_sciences)
df_tech = priprav_df_pro_prirustku_a_ubytku(df_technology, df02_technology)
df_physic = priprav_df_pro_prirustku_a_ubytku(df_Physical_sciencese, df02_Physical_sciencese)
df_life = priprav_df_pro_prirustku_a_ubytku(df_Life_biomedicine, df02_Life_biomedicine)
#pak zavolej toto:
plot_clustered_stacked([df_social, df_tech, df_physic, df_life],["Social Sciences", "Technology", "Physical Sciences", "Life Sciences & Biomedicine"],title="Podíl dokumentů u kterých byla zaznamenána změna ve sledovaných indikátorech (v %)", H="///")






