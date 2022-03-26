import os
import textstat  #https://pypi.org/project/textstat/#description --> knihovna pro test čitelnosti
import requests
import json
import time
from datetime import datetime


#nazev_generovaneho_souboru = "test_all_data"

id_zaznamu = 0 
pocet_clanku_bez_doi = 0

def zpracuj_soubor(cesta_k_souboru, altmetrics_on, plumX_on, nazev_generovaneho_souboru, start_from = 0):
    list_AF = []
    list_WC = []
    list_SC = []
    list_TC = []
    list_OA = []
    list_PG = []
    list_AB = []
    list_C1 = []
    list_TI = []
    list_FU = []
    list_DT = []
    list_LA = []
    list_PY = []
    list_oblasti = []
    doi = ""
    id_radku = 0
    
    naposledy_zpracovany_radek_AF = 0
    naposledy_zpracovany_radek_WC = 0
    naposledy_zpracovany_radek_SC = 0
    naposledy_zpracovany_radek_TC = 0
    naposledy_zpracovany_radek_OA = 0
    naposledy_zpracovany_radek_PG = 0
    naposledy_zpracovany_radek_AB = 0
    naposledy_zpracovany_radek_C1 = 0
    naposledy_zpracovany_radek_TI = 0
    naposledy_zpracovany_radek_FU = 0
    naposledy_zpracovany_radek_DI = 0
    naposledy_zpracovany_radek_DT = 0
    naposledy_zpracovany_radek_LA = 0
    naposledy_zpracovany_radek_PY = 0
    
  

    with open(cesta_k_souboru, 'r', encoding='utf-8') as reader:
        for line in reader.readlines():
            if line == "\n":   #tohle tady slouží k argumentu "start_from" - přeskočí to určitej počet záznamu pokud je třeba
                global id_zaznamu
                id_zaznamu += 1
            
                if id_zaznamu <= start_from - 1:
                    continue
            



            try: #___Digital Object Identifier (DOI)___
                naposledy_zpracovany_radek_DI, hodnota_radku = nacist_pole("DI", line, id_radku, naposledy_zpracovany_radek_DI)
                #list_DI.append(hodnota_radku.rstrip())
                doi = hodnota_radku.rstrip().replace('"', ' ')                    

            except TypeError:
                pass


            try: #___Author Full Name___
                naposledy_zpracovany_radek_AF, hodnota_radku = nacist_pole("AF", line, id_radku, naposledy_zpracovany_radek_AF)
                list_AF.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass


            try: #___Document Type___
                naposledy_zpracovany_radek_AF, hodnota_radku = nacist_pole("DT", line, id_radku, naposledy_zpracovany_radek_DT)
                list_DT.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            
            try: #___Web of Science Categories___  - pro korelaci
                naposledy_zpracovany_radek_WC, hodnota_radku = nacist_pole("WC", line, id_radku, naposledy_zpracovany_radek_WC) 
                # list_WC.append(hodnota_radku.rstrip())
                c = hodnota_radku.rstrip().replace('"', ' ')
                list_WC.append(c)
                # split1 = c.split("; ")
                # print("split1", split1)
                # for s in split1:
                #     print("s:", s)
                #     list_WC.append(s)
                # print("list_WC:", list_WC)
            except TypeError:
                pass

            try: #___Research Areas___  - pro interdisciplinaritu
                naposledy_zpracovany_radek_SC, hodnota_radku = nacist_pole("SC", line, id_radku, naposledy_zpracovany_radek_SC)
                b = hodnota_radku.rstrip().replace('"', ' ')
                list_SC.append(b)
                
                # split2 = b.split("; ")
                # for s in split2:
                #     list_SC.append(s)

            except TypeError:
                pass
            
            try: #___Web of Science Core Collection Times Cited Count___
                naposledy_zpracovany_radek_TC, hodnota_radku = nacist_pole("TC", line, id_radku, naposledy_zpracovany_radek_TC)
                list_TC.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Open Access Indicator___
                naposledy_zpracovany_radek_OA, hodnota_radku = nacist_pole("OA", line, id_radku, naposledy_zpracovany_radek_OA)
                list_OA.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Page Count___
                naposledy_zpracovany_radek_PG, hodnota_radku = nacist_pole("PG", line, id_radku, naposledy_zpracovany_radek_PG)
                list_PG.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Abstract___ - https://arxiv.org/ftp/arxiv/papers/1710/1710.08594.pdf - readibility test  // number of words 
                naposledy_zpracovany_radek_AB, hodnota_radku = nacist_pole("AB", line, id_radku, naposledy_zpracovany_radek_AB)
                list_AB.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Title___
                naposledy_zpracovany_radek_TI, hodnota_radku = nacist_pole("TI", line, id_radku, naposledy_zpracovany_radek_TI)
                list_TI.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Funding Agency and Grant Number___
                naposledy_zpracovany_radek_FU, hodnota_radku = nacist_pole("FU", line, id_radku, naposledy_zpracovany_radek_FU)
                list_FU.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Author Address___
                naposledy_zpracovany_radek_C1, hodnota_radku = nacist_pole("C1", line, id_radku, naposledy_zpracovany_radek_C1)
                r = hodnota_radku.rstrip().replace('"', ' ')
                r_splitted = r.split(", ")
                zeme_autora_1 = r_splitted[-1]
                zeme_autora = zeme_autora_1[:-1]
                list_C1.append(zeme_autora.rstrip())
            except TypeError:
                pass

            try: #___Language___
                naposledy_zpracovany_radek_LA, hodnota_radku = nacist_pole("LA", line, id_radku, naposledy_zpracovany_radek_LA)
                list_LA.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            try: #___Publication Year___
                naposledy_zpracovany_radek_PY, hodnota_radku = nacist_pole("PY", line, id_radku, naposledy_zpracovany_radek_PY)
                list_PY.append(hodnota_radku.rstrip().replace('"', ' '))
            except TypeError:
                pass

            

            
            if line == "\n":
                
                print("ID_záznamu:", id_zaznamu)

                if doi == "":
                    global pocet_clanku_bez_doi
                    pocet_clanku_bez_doi += 1
                    print("pocet_clanku_bez_doi:", pocet_clanku_bez_doi)
                    doi = "missing"

                
                mezinarodni_spoluprace = False
                for zeme in list_C1:
                    if zeme != "Czech Republic":
                        mezinarodni_spoluprace = True
                

                open_access = None

                if not list_OA:
                    open_access = False
                else:
                    open_access = True


                funding = None 

                if not list_FU:
                    funding = False
                else:
                    funding = True
                    
                _ti = ' '.join(list_TI) #občas se stane, že title je na dvou řádcích, tak zde je spojuju do jednoho stringu
                list_TI = [_ti]
                _ab = ' '.join(list_AB) #občas se stane, že abstrakt je na dvou řádcích, tak zde je spojuju do jednoho stringu
                list_AB = [_ab]
                _sc = ' '.join(list_SC)
                #print("_sc:", _sc)
                #print("before:", list_SC)
                list_SC_o = _sc.split("; ") #Tady musí být "; " jinak se to rozsype --> mapování nebude fungovat protože nedokáže matchnout pojem s mezerou před ním 
                #print("after:", list_SC)
                
                _wc = ' '.join(list_WC)
                list_WC_o = _wc.split("; ")
                
                if _ab != "":
                    readability = textstat.flesch_reading_ease(_ab)
                else:
                    readability = "None"
                list_Flesch = [str(readability)]
                pocet_slov_prep = _ab.split(" ")
                pocet_slov_AB = len(pocet_slov_prep)
                pocet_slov_TI_prep = _ti.split(" ")
                pocet_slov_TI = len(pocet_slov_TI_prep)
                pocet_autoru = len(list_AF)
                
                for field in list_SC_o:
                    
                    oblast = mapovani_vyzkumnych_oblasti(str(field))
                    list_oblasti.append(oblast)
                
                research_categories = list(set(list_oblasti))
                if len(research_categories) > 1:
                    interdistiplinarita = "True"
                else:
                    interdistiplinarita = "False"


                #----------API Altmetric.com a PlumX------------
                
                if altmetrics_on is True: #VYPÍNAČ/ZAPÍNAČ při volání metody
                    if doi == "missing": #Pokud chybí DOI, nemá cenu se doptávat na něj přes API. 
                        pass
                    else:
                        #Altmetric.com
                        available_altmetrics, answer_altmetrics = api_altmetrics_call(doi)
                        if available_altmetrics is True:
                            tweetovani_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_tweeters_count")
                            fb_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_fbwalls_count")
                            blogy_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_feeds_count")
                            zpravy_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_msm_count")
                            reddit_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_rdts_count")
                            video_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "cited_by_videos_count")
                            mendeley_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "readers","mendeley")
                            score_altmetrics = zpracovani_api_odpovedi(answer_altmetrics, "score")
                        if available_altmetrics is False:
                            print("Článek není k dispozici ve službě Altmetric.com -> STAV: ", str(answer_altmetrics))
                            tweetovani_altmetrics = fb_altmetrics = blogy_altmetrics = zpravy_altmetrics = reddit_altmetrics = video_altmetrics = mendeley_altmetrics = score_altmetrics = "None"
                else:
                    available_altmetrics = "offline"
                    tweetovani_altmetrics = fb_altmetrics = blogy_altmetrics = zpravy_altmetrics = reddit_altmetrics = video_altmetrics = mendeley_altmetrics = score_altmetrics = "offline"

                if plumX_on is True: #VYPÍNAČ/ZAPÍNAČ při volání metody
                    if doi == "missing":
                        pass
                    else:    
                        #PlumX
                        available_plumx, answer_plumx = api_plumx_call(doi)
                        if available_plumx is True:
                            
                            delka_kategorie = len(zpracovani_api_odpovedi(answer_plumx, "count_categories")) #, 0, "total"
                            capture = citation = socialMedia = usage = mentions = "0" #zde musí být deklarovány proměnné - plumx nemá nulové hodnoty -> proměná u něj chybí -> proto musí bát deklarovány aby mohly bát zapsány do csv
                            for kategorie in range(0, delka_kategorie):
                                jaka_kategorie = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "name")

                                if jaka_kategorie == "capture":
                                    capture = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "total")
                                if jaka_kategorie == "citation":
                                    citation = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "total")
                                if jaka_kategorie == "socialMedia":
                                    socialMedia = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "total")
                                if jaka_kategorie == "usage":
                                    usage = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "total")
                                if jaka_kategorie == "mention":
                                    mentions = zpracovani_api_odpovedi(answer_plumx, "count_categories", kategorie, "total")


                        if available_plumx is False:
                            print("Článek není k dispozici ve službě PlumX -> STAV:", str(answer_plumx))
                            capture = citation = socialMedia = usage = mentions = "None"
                else:
                    capture = citation = socialMedia = usage = mentions = "offline"
                    available_plumx = "offline"        

                        #print(tweetovani_altmetrics, fb_altmetrics, blogy_altmetrics, zpravy_altmetrics, reddit_altmetrics, video_altmetrics, mendeley_altmetrics, score_altmetrics)

                #POPIS POLÍ CSV
                """
                list_AF                 ->  seznam autorů, získané z pole AF
                pocet_autoru            ->  počet autorů; zjištěn počet položek v poli "list_AF"
                list_DT                 ->  Typ dokumentu
                list_WC                 ->  kategorie WoS: https://images.webofknowledge.com/images/help/WOS/hp_subject_category_terms_tasca.html
                list_SC,                ->  kategorie oblasti výzkumu - "Research Areas": https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html
                research_categories,    ->  subkategorie z "list_SC" byly namapované na nadřazené kategorie, kterých je celkem jen 5
                interdistiplinarita,    ->  pokud článek disponuje více nadřazenýma kategoriema v listu "research_categories", tak je brán za mezioborový
                list_TC,                ->  počet citací z WoS (ačkoliv se jedna o klasický int, z nějakého důvodu ho mám v listu)
                open_access             ->  True nebo False -> indikuje jestli je článek OA
                list_OA,                ->  pokud je článek OA zde je informace o tom v jakém modu 
                list_PG,                ->  počet stránek článku
                list_AB,                ->  abstrakt (z nějkého důvodu je v listu i když by asi být nemusel)
                list_Flesch             ->  čitelnost abstraktu (Flesh koeficient https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests)
                pocet_slov_AB           ->  délka abstraktu
                mezinarodni_spoluprace  ->  True nebo False -> Pokud alespoň jeden z autorů pracuje pod institucí mimo ČR, tak True
                list_C1,                ->  seznam zemí autorů: z kompletní hodnoty je vyfiltrovaná pouze země samotná (bez města, atd..)
                list_TI,                ->  název článku (dohromady i s podnázvem)
                pocet_slov_TI           ->  délka názvu článku
                list_FU,                ->  seznam grantů
                funding                 ->  indikátor, jestli byl výzkum financován z grantu; True/False ; vychází z listu "list_FU"- pokud je prázdný tak False, jinak True
                doi                     ->  DOI článku - slouží hlavně pro vstup k API
                list_LA                 ->  jazyk dokumentu
                available_altmetrics    ->  TRUE nebo FALSE - říká, jestli je článek k dispozici ve službě Altmetrics.com
                tweetovani_altmetrics   ->  Altmetric.com | počet účtů na twitteru, které citovali článek
                fb_altmetrics           ->  Altmetric.com | počet stránek na FB, které sdílely článek
                blogy_altmetrics        ->  Altmetric.com | počet blogů ve kterých se objevil článek
                zpravy_altmetrics
                reddit_altmetrics
                video_altmetric         ->  Altmetric.com | Youtube a Vimeo
                mendeley_altmetrics
                score_altmetrics        ->  Altmetric.com | indikátor, který agreguje a váží všechna data
                available_plumx         ->  PlumX | TRUE nebo FALSE - říká, jestli je článek k dispozici ve službě PlumX
                capture                 ->  PlumX | Indicates that someone wants to come back to the work. Captures can be an leading indicator of future citations.
                citation                ->  PlumX |  This is a category that contains both traditional citation indexes such as Scopus, as well as citations that help indicate societal impact such as Clinical or Policy Citations.
                mentions                ->  PlumX | Measurement of activities such as news articles or blog posts about research. Mentions is a way to tell that people are truly engaging with the research.
                socialMedia             ->  PlumX | This category includes the tweets, Facebook likes, etc. that reference the research. Social Media can help measure “buzz” and attention.  Social media can also be a good measure of how well a particular piece of research has been promoted.
                usage                   ->  PlumX | A way to signal if anyone is reading the articles or otherwise using the research. Usage is the number one statistic researchers want to know after citations.
                """
                if doi == "missing": #Pokud chybí DOI, nemá cenu se doptávat na něj přes API. 
                    pass
                else:
                    # nakonec nepoužito: list_AF, list_AB
                    csv_row_data = priprav_csv_radek(
                        pocet_autoru, list_DT, list_WC_o, list_SC_o, research_categories, 
                        interdistiplinarita, list_TC, open_access, list_OA, list_PG, 
                        list_Flesch, pocet_slov_AB, mezinarodni_spoluprace, list_C1, list_TI, pocet_slov_TI, 
                        list_FU, funding, doi, list_LA, list_PY, available_altmetrics, tweetovani_altmetrics, fb_altmetrics, 
                        blogy_altmetrics, zpravy_altmetrics, reddit_altmetrics, video_altmetrics, mendeley_altmetrics, 
                        score_altmetrics, available_plumx, capture, citation, mentions, socialMedia, usage
                        ) #do této funkce musí jít seznamy dat ve standardizovaném pořadí 
                    #print(csv_row)


                    with open(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_" + nazev_generovaneho_souboru + ".csv", "a", encoding='utf-8') as f:
                        f.write(csv_row_data + "\n")


            #--------logování---------

                now = datetime.now()
                dt = now.strftime("%d/%m/%Y %H:%M:%S")

                soubor = cesta_k_souboru.split("Data_WoS\\\\")
                csv_row_log = priprav_csv_radek(dt, soubor[1], id_zaznamu, doi, pocet_clanku_bez_doi)
                with open(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\logfile_" + nazev_generovaneho_souboru + ".txt", "a", encoding='utf-8') as f:
                    f.write(csv_row_log + "\n")



                print("----------NOVÝ ČLÁNEK------------")
                #list_AF = list_WC = list_SC = list_TC = list_OA = list_PG = list_AB = list_C1 = list_TI = list_FU = list_oblasti = []
                list_AF = []
                list_WC = []
                list_SC = []
                list_TC = []
                list_OA = []
                list_PG = []
                list_AB = []
                list_C1 = []
                list_TI = []
                list_FU = []
                list_DT = []
                list_LA = []
                list_PY = []
                doi = ""
                list_oblasti = []
                id_radku = 0
                naposledy_zpracovany_radek_AF = 0
                naposledy_zpracovany_radek_WC = 0
                naposledy_zpracovany_radek_SC = 0
                naposledy_zpracovany_radek_TC = 0
                naposledy_zpracovany_radek_OA = 0
                naposledy_zpracovany_radek_PG = 0
                naposledy_zpracovany_radek_AB = 0
                naposledy_zpracovany_radek_C1 = 0
                naposledy_zpracovany_radek_TI = 0
                naposledy_zpracovany_radek_FU = 0
                naposledy_zpracovany_radek_DI = 0
                naposledy_zpracovany_radek_DT = 0
                naposledy_zpracovany_radek_LA = 0
                naposledy_zpracovany_radek_PY = 0
                #tweetovani_altmetrics = fb_altmetrics = blogy_altmetrics = zpravy_altmetrics = reddit_altmetrics = video_altmetrics = mendeley_altmetrics = score_altmetrics = 0

            id_radku += 1 
        # print(list_aut)
        # print(list_WC)

def nacist_pole(oznaceni, radek, cislo_aktualniho_radku, cislo_naposledy_zpracovaneho_radku):
    
    if oznaceni != "AB" or oznaceni != "TI": 
        radek_definice = radek[:2]
        if radek_definice == oznaceni:
            return (cislo_aktualniho_radku, radek[3:])
            
        if radek_definice == "  " and cislo_aktualniho_radku - 1 == cislo_naposledy_zpracovaneho_radku:
            return (cislo_aktualniho_radku, radek[3:])
    
    else: # výjimka ve zpracování pro abstrakt a title, protože mohou mít jiné formátování
        radek_definice = radek[:2]
        if radek_definice == oznaceni:
            return (cislo_aktualniho_radku, radek[3:])
            
        if radek_definice == "  " and cislo_aktualniho_radku - 1 == cislo_naposledy_zpracovaneho_radku:
            return (cislo_aktualniho_radku, radek[3:])
        
        if str(radek_definice).islower() and cislo_aktualniho_radku - 1 == cislo_naposledy_zpracovaneho_radku:
            return (cislo_aktualniho_radku, radek)
        

def zpracuj_slozku(cesta_ke_slozce, altmetrics_on, plumX_on, nazev_generovaneho_souboru, start_from = 0):
    files_with_data = os.listdir(cesta_ke_slozce)
    for soubor in files_with_data:
        zpracuj_soubor(cesta_ke_slozce + soubor, altmetrics_on, plumX_on, nazev_generovaneho_souboru, start_from)
    

#funkce, která příjmá na vstupu listy a vytváří z nich formát CSV - vrací řádek ve formě CSV.. je nutné standardizovat pořadí listů na vstupu
def priprav_csv_radek(*args):
    csv_radek = ""
    a = 0
    for seznam in args:
        if type(seznam) == list:
            list_to_string = ";".join(seznam)
            list_to_string = '"' + list_to_string + '"'
            if a == len(args)-1:
                csv_radek += list_to_string
            else:
                csv_radek += list_to_string + ";"
            a += 1
        else:
            list_to_string = '"' + str(seznam) + '"'
            if a == len(args)-1:
                csv_radek += list_to_string
            else:
                csv_radek += list_to_string + ";"
            a += 1

    #print(csv_radek)
    return csv_radek

def mapovani_vyzkumnych_oblasti(field):
    #print(field)
    #Arts & Humanities
    arts_hum = [
        "Architecture", "Art", "Arts & Humanities - Other Topics", "Asian Studies", "Classics", 
        "Dance", "Film, Radio & Television", "History", "History & Philosophy of Science", "Literature", 
        "Music", "Philosophy", "Religion", "Theater"]

    #Life Sciences & Biomedicine
    life_and_biomedicine = [
        "Agriculture", "Agriculture", "Anatomy & Morphology", "Anesthesiology", "Anthropology", 
        "Audiology & Speech-Language Pathology", "Behavioral Sciences", "Biochemistry & Molecular Biology", "Biodiversity & Conservation", "Biophysics", 
        "Biotechnology & Applied Microbiology", "Cardiovascular System & Cardiology", "Cardiovascular System & Cardiology", "Cell Biology", "Critical Care Medicine", "Dentistry, Oral Surgery & Medicine", 
        "Dermatology", "Developmental Biology", "Emergency Medicine", "Endocrinology & Metabolism", "Entomology", 
        "Environmental Sciences & Ecology", "Evolutionary Biology", "Fisheries", "Food Science & Technology", "Forestry",
        "Gastroenterology & Hepatology", "General & Internal Medicine", "Genetics & Heredity", "Geriatrics & Gerontology", "Health Care Sciences & Services",
        "Hematology", "Immunology", "Infectious Diseases", "Integrative & Complementary Medicine", "Legal Medicine",
        "Life Sciences Biomedicine - Other Topics", "Marine & Freshwater Biology", "Mathematical & Computational Biology", "Medical Ethics", "Medical Informatics",
        "Medical Laboratory Technology", "Microbiology", "Mycology", "Neurosciences & Neurology", "Nursing",
        "Nutrition & Dietetics", "Obstetrics & Gynecology", "Oncology", "Ophthalmology", "Orthopedics",
        "Otorhinolaryngology", "Paleontology", "Parasitology", "Pathology", "Pediatrics", "Pharmacology & Pharmacy",
        "Physiology", "Plant Sciences", "Psychiatry", "Public, Environmental & Occupational Health", "Radiology, Nuclear Medicine & Medical Imaging",
        "Rehabilitation", "Reproductive Biology", "Research & Experimental Medicine", "Respiratory System", "Rheumatology",
        "Sport Sciences", "Substance Abuse", "Surgery", "Toxicology", "Transplantation", "Tropical Medicine",
        "Urology & Nephrology", "Veterinary Sciences", "Virology", "Zoology"]

    #Physical Sciences
    physical_sciences = [
        "Astronomy & Astrophysics", "Chemistry", "Crystallography", "Electrochemistry", "Geochemistry & Geophysics",
        "Geology", "Mathematics", "Meteorology & Atmospheric Sciences", "Mineralogy", "Mining & Mineral Processing",
        "Oceanography", "Optics", "Physical Geography", "Physics", "Polymer Science", 
        "Thermodynamics", "Water Resources"]

    #Social Sciences
    soc_sciences = [
        "Archaeology", "Area Studies", "Biomedical Social Sciences", "Business & Economics", "Communication",
        "Criminology & Penology", "Cultural Studies", "Demography", "Development Studies", "Education & Educational Research",
        "Ethnic Studies", "Family Studies", "Geography", "Government & Law", "International Relations",
        "Linguistics", "Mathematical Methods In Social Sciences", "Psychology", "Public Administration", "Social Issues",
        "Social Sciences - Other Topics", "Social Work", "Sociology", "Urban Studies", "Women's Studies"]

    #Technology
    technology = [
        "Acoustics", "Automation & Control Systems", "Computer Science", "Construction & Building Technology", "Energy & Fuels",
        "Engineering", "Imaging Science & Photographic Technology", "Information Science & Library Science", "Instruments & Instrumentation", "Materials Science",
        "Mechanics", "Metallurgy & Metallurgical Engineering", "Microscopy", "Nuclear Science & Technology", "Operations Research & Management Science",
        "Remote Sensing", "Robotics", "Science & Technology - Other Topics", "Spectroscopy", "Telecommunications",
        "Transportation"]

    if field in arts_hum:
        print("oblast:", "Arts & Humanities")
        return "Arts & Humanities"
    elif field in life_and_biomedicine:
        print("oblast:", "Life Sciences & Biomedicine")
        return "Life Sciences & Biomedicine"
    elif field in physical_sciences:
        print("oblast:", "Physical Sciences")
        return "Physical Sciences"
    elif field in soc_sciences:
        print("oblast:", "Social Sciences")
        return "Social Sciences"
    elif field in technology:
        print("oblast:", "Technology")
        return "Technology"
    else:
        print("obast", "none")
        return "None"

#výstup z této funkce je string odpověď z API. Tento výstup slouží jako vstup pro funkci "zpracovani_api_odpovedi"
def api_altmetrics_call(doi):
    api_key="6aef862ef76c485d84f256d75150f486"

    api_url_clanku = "https://api.altmetric.com/v1/doi/" + str(doi) + "?key=" + api_key
    response = requests.get(api_url_clanku)

    header_data = response.headers
    json_header = json.loads(json.dumps(dict(header_data))) #api vrací data ve formátu se 'single quoute' ale JSON standard říká že musí být pouze s "double quoute" -> proto dict

    print("Hourly Rate Limit Remaining:", str(json_header["X-HourlyRateLimit-Remaining"]) + "/" + str(json_header["X-HourlyRateLimit-Limit"]))
    print("Daily Rate Limit Remaining:", str(json_header["X-DailyRateLimit-Remaining"]) + "/" + str(json_header["X-DailyRateLimit-Limit"]))
    print()

    if json_header["X-HourlyRateLimit-Remaining"] == 1:
        print("Dosažen hodinový limit API dotazů pro Altmetric.com - čeká se na obnovení")
        time.sleep(3610)  #program si dá na jednu hodinu pauzu
    if json_header["X-DailyRateLimit-Remaining"] == 1:
        print("Dosažen denní limit API dotazů pro Altmetric.com - čeká se na obnovení")
        time.sleep(86410) #program si dá pauzu na jeden den 

    odpoved = response.text
    print(doi)
    #print("API odpoved:", odpoved)
    if odpoved == "Not Found":
        available = False
        return available, "Not Found"
    else:
        available = True
        return available, odpoved
    
    


def api_plumx_call(doi):
    api_key = "76033570136eefe7414630f354bff245"

    api_url_clanku = "https://api.elsevier.com/analytics/plumx/doi/" + str(doi) + "?apiKey=" + api_key

    response = requests.get(api_url_clanku)

    odpoved = response.text
    print("api_plumx_call:")
    print(odpoved)
    if "NOT_FOUND" in odpoved and "404" in odpoved or "count_categories" not in odpoved:
        available = False
        
        return available, "Not Found"
    else:
        available = True
        return available, odpoved



#funkce, která je univerzální - umí se doptat na jakoukoliv hodnotu ve stromové struktuře JSONU
def zpracovani_api_odpovedi(odpoved, *args):
    
    try:
        json_altmetric = json.loads(odpoved)
    except:
        print("Nedostal jsem správně odpověď z API ke zpracování...")
        return "Error with JSON"
    
    try:
        value = json_altmetric
        for arg in args:
            value = value[arg]
        return value
    except: 
        return "0"
   

zpracuj_slozku(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\Data_WoS\\", altmetrics_on=True, plumX_on=True, nazev_generovaneho_souboru="real_data_druhe_stazeni", start_from=0) #dvě lomítka jsou ve skutečnosti jedno lomítko
#zpracuj_soubor(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\Data_WoS\test_SC.txt")

