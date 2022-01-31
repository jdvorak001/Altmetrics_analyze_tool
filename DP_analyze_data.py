from logging import captureWarnings
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy.stats.stats import pearsonr
"""
FUNKCE POUŽÍVANÉ PRO STATISTICKOU ANALÝZU, VOLANÉ UŽIVATELEM:

zjisti_korelaci(data, sloupec_A, sloupec_B, vizualizace=False, typ_korelace="spearman", group_by=False)
    --->zjištuje korelaci mezi dvěma sloupci v určeném datasetu

disciplinary_and_time_differences(data, indikator, groupby, priprava_dat_vice_hodnoty = True)
    ---> zjišťuje jak se v čase vyvíjel indikátor - rozkategorizováno podle vstupu "groupby"

TODO - DOPLNIT!!
"""



# popis jednotlivých sloupců je dostupný v souboru "DP_process_data.py"
# column_names = ["pocet_autoru", "list_DT", "list_WC", "list_SC", "research_categories", 
#                     "interdistiplinarita", "list_TC", "open_access", "list_OA", "list_PG", 
#                     "list_Flesch", "pocet_slov_AB", "mezinarodni_spoluprace", "list_C1", "list_TI", "pocet_slov_TI", 
#                     "list_FU", "funding", "doi", "list_LA","list_PY", "available_altmetrics", "tweetovani_altmetrics", "fb_altmetrics", 
#                     "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetric", "mendeley_altmetrics", 
#                     "score_altmetrics", "available_plumx", "capture", "citation", "mentions", "socialMedia", "usage"]

column_names = ["pocet_autoru", "typ_dokumentu", "kategorie_WC", "kategorie_SC", "research_areas", 
                    "interdisciplinarita", "pole_TC", "open_access", "pole_OA", "pocet_str", "flesch",
                    "pocet_slov_AB", "mezinarodni_spoluprace", "pole_C1", "title", "pocet_slov_TI", "pole_FU",
                    "funding", "doi", "pole_LA", "list_PY", "available_altmetrics", "tweetovani_altmetrics", "fb_altmetrics",
                    "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics",
                    "mendeley_altmetrics", "score_altmetrics", "available_plumx","capture_plumx", "citation_plumx",
                    "mentions_plumx", "socialMedia_plumx", "usage_plumx"]



#df = pd.read_csv(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_test_9.csv", sep=";", header=None, names=column_names)
df = pd.read_csv(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_real_data.csv", sep=";", header=None, names=column_names)
df.replace(to_replace=["None"], value=np.nan, inplace=True)  # tento řádek se stará o prázdné hodnoty, které převádí z Pythonovské syntaxe do Pandas syntaxe
df = df[df["list_PY"] != 2022] #z nějakého důvodu se mi stáhly i články za roky 2022, proto je odstraňuji
df = df[df["list_PY"].notnull()] #některé články nemají žádnou informaci o roku. Proto je odstraňuji, protože si nemohu být jistý, že se tam nevtrousili ještě nějaké další např z roku 2022



def zjisti_korelaci(data, sloupec_A, sloupec_B, typ_korelace, vizualizace=False, group_by=False, minimum_clanku=False):
    """
       *data => vlož dataframe z pandas*
       *sloupec_A a sloupec_B => sloupce z dataframu, kde se hledá závislost*
       *typ korelace => 'spearman' 'pearson' 'kendall'* 
       *vizualizace => True False #generuje graf*
       -vizualizace se zobrazí pouze u spearmanové korelace. Ostatní negenerují graf.
       *group_by = které hodnoty má seskupovat - vypočítá korelaci pro každou kategorii - pokud je vizualizace zapnuta, vytvoří graf pro každou kategorii
    """
    data = data[data[sloupec_A].notna()]
    data = data[data[sloupec_B].notna()]
    data[sloupec_A] = pd.to_numeric(data[sloupec_A])
    data[sloupec_B] = pd.to_numeric(data[sloupec_B]) #, errors='coerce'

    if typ_korelace == "pearson":
        print("Pro pearsonovu korelaci převádím data do logaritmického měřítka...")
        data[sloupec_A] = np.log(1 + data[sloupec_A])
        data[sloupec_B] = np.log(1 + data[sloupec_B])
    
    if group_by is False:
        korelace = data[sloupec_A].corr(data[sloupec_B], method=typ_korelace)
        k = pearsonr(data[sloupec_A], data[sloupec_B])
        print(k, "scipi")
    if group_by is not False:
        
        data = prepare_dataframe_for_multivalues(data, group_by)
        
        if minimum_clanku is not False:
            data = redukuj_kategorie_pri_nizkych_poctech(data, minimum_clanku, group_by)

        grouped = data[sloupec_A].groupby(data[group_by])
        
        
        korelace = grouped.corr(data[sloupec_B], method=typ_korelace)

        # korelace = data.filter(items=[sloupec_A, sloupec_B]).corr(method=typ_korelace)
        # sns.heatmap(korelace)
        # plt.show()
    print("Typ korelace:", typ_korelace)
    print(korelace)

    if vizualizace is True and typ_korelace == "spearman": #grafy fungují jen na Spearmanovu korelaci, Pearsonova není naprogramována
        if group_by is False:
            data["Rank_A"] = data[sloupec_A].rank(method="first")
            data["Rank_B"] = data[sloupec_B].rank(method="first")
            data.sort_values("list_TC", inplace = True)
            sns.set_theme(style="darkgrid")

            sns.lmplot(data=data, x="Rank_A", y="Rank_B")
            plt.show()


        if group_by is not False:
            data["Rank_A"] = data[sloupec_A].rank(method="first") # zde u té metody si nejsem jistý - zeptat se vedoucího co si o tom myslí #TODO
            data["Rank_B"] = data[sloupec_B].rank(method="first") # |_> jde o to, že metoda určuje co dělat s hodnotama, které jsou stejné a do jakého ranku je poté zařadit -> když použiju "Avarage" (ten by se podle Spearmena měl používat), tak graf vypadá divně
            data.sort_values("list_TC", inplace = True)
            sns.set_theme(style="darkgrid")

            g = sns.FacetGrid(data, col=group_by, col_wrap=4) #, xlim=(0,800), ylim=(0,800))  # toto dělá čtverec z grafu
            g.map(sns.regplot, "Rank_A", "Rank_B")
            col_order = grouped.groups.keys() #toto zjištuje jaké typy z group_by existují; důležité je pořadí, jinak jsou grafy špatně vykresleny :-) (nepoužívat. unique()) 
            print(type(col_order), col_order)
            for txt, title in zip(g.axes.flat, col_order):
                txt.set_title(title)   
                # add text
                txt.text(10, 120, "ρ = " + str(korelace[title]), fontsize = 12)

    
            #sns.lmplot(data=data, x="Rank_A", y="Rank_B", col=group_by, col_wrap=2)
            plt.show()

    if vizualizace is True and typ_korelace == "pearson":
        if group_by is False:
            sns.set_theme(style="darkgrid")

            sns.lmplot(data=data, x=sloupec_A, y=sloupec_B, scatter_kws={'s':1}, line_kws={'color': 'coral'})
            plt.show()
        if group_by is not False:
               
            g = sns.FacetGrid(data, col=group_by, col_wrap=4)
            g.map(sns.regplot, sloupec_A, sloupec_B, scatter_kws={'s':1}, line_kws={"color": "coral"})
            col_order = data[group_by].unique() #toto zjištuje jaké typy z group_by existují 
            print(type(col_order), col_order)
            for txt, title in zip(g.axes.flat, col_order):
                txt.set_title(title)   
                # add text
                txt.text(0.5, 0.5, "ρ = " + str(korelace[title]), fontsize = 12)
                #txt.text(1,2,"trololo", fontsize = 12)
            #sns.lmplot(data=data, x=sloupec_A, y=sloupec_B, col=group_by, col_wrap=2)
            plt.show()



# def zjisti_altmetricke_pokryti(group_by):
#     """
#     Cílem je výstup, který mi dá hodnotu/poměr mezi články spadající do zkoumané kategorie a počet těch, které v dané kategorii nemají záznam v Altmetric.com nebo PlumX
#     př.: Medical Science = ze 180 článku jich má záznam 54 .. (54/180)
#     Jde o to zjistit, co má největší počet záznamů 
#     """

def prepare_dataframe_for_multivalues(data, column_to_check, proportion=False):
    """
    NEVOLÁ SE RUČNĚ, JE VYUŽÍVANÁ DALŠÍMI FUNKCEMI
    Tato funkce řeší problém toho, že některé sloupce mají více hodnot v jedné buňce, z pravidla oddělené středníkem.
    Pokud je proportion False, tak každému novému řádku přidělí sledovaný indikátor 100%. Pokud je v proportion uvedený sledovaný indikátor, tento indikátor podělí mezi ostatní nově vzniklý řádky tzn. férovým podílem každé kategorii 1/n 
    """
    
    print("prepare_dataframe_for_multivalues(): PROBÍHÁ PŘÍPRAVA DAT")
    #---------------------------------------------------------------------
    #STARÝ KOD, UŽ SE NEMUSÍ POUŽÍVAT
    #----
    # data = data.reset_index(drop=True)
    # df_list = [] #NEW

    
    # for row in data.itertuples(): #itertuples je mnohem rychlejší než iterrow(), nicméně nevrací to hodnotu v dataframu
    #     cell = getattr(row, column_to_check) # toto vrátí obsah buňky na daném řádku a v daném sloupci
    #     poradi_radku = getattr(row, "Index")
    #     print(poradi_radku, len(data))
    #     cell = str(cell).replace("; ", ";")
    #     hodnoty_radku = str(cell).split(";") #vrací to list s hodnotami z WC | #TODO některá pole mají mezeru mezi hodnotami některá nemají př: list_DT s mezerou, list_WC bez mezery
        
    #     if len(hodnoty_radku) == 1: #pokud je jen jedna hodnota, tak překopíruj celý řádek rovnou do nového dataframu

    #         df_list.append(data.iloc[poradi_radku].values.tolist()) #NEW
        
    #     if len(hodnoty_radku) > 1: #pokud je více hodnot (článek spadá do více kategorií), tak vytvoří nový řádek/záznam pro celý článek (zduplikuje ho) ale pokaždý s jinou kategorií WC
    #         for h in hodnoty_radku:
    #             df_list.append(data.iloc[poradi_radku].values.tolist())  #NEW
    #             poradi_sloupce = column_names.index(column_to_check)  #NEW
    #             df_list[-1][poradi_sloupce] = h  #NEW

    #     df3 = pd.DataFrame(df_list, columns = column_names)
 
    # df3 = df3.reset_index(drop=True)


#-----------------------------------------------------------------------------------------------

    data[column_to_check] = data[column_to_check].astype(str) 
    data[column_to_check] = data[column_to_check].str.replace("; ", ";")# my mistake - some columns have different separator - extra space - this can deal with that mistake
    asn_lists = data[column_to_check].str.split(';')         # split strings into list
    
    data[column_to_check] = asn_lists                        # replace strings with lists in the dataframe


    df2 = data.explode(column_to_check)                      # explode based on the particular column
    if proportion is not False:
        df2[proportion] /= df2[proportion].groupby(level=0).transform('count') # hodnotu zkoumaného indikátoru rozdělí pro každou kategorii ve férovém podílu


    print(len(data), "delka originálního dataframu")
    print(len(df2), "delka dataframu po vyřešení multivalues")
    print("------------------------")

    df2 = df2[df2[column_to_check] != "None"]  #především u "research_categories" se mi objevuje None hodnota. Tímhle jí mažu
    
    return df2

    # out2 = data.explode(column_to_check).assign(capture=lambda d: d.groupby(level=0)['capture'].apply(lambda s:s/len(s)))

    # out = data.explode(column_to_check)
    # out['capture'] /= out['capture'].groupby(level=0).transform('count')

    # # edf = data.explode(column_to_check)
    # # edf.capture = edf.groupby(edf.index).capture.transform("size").rdiv(1)


    # # print(out2)
    # # print(out)
    # print(out)
    # return out
            


def disciplinary_and_time_differences(data, indikator, groupby, median_or_mean, priprava_dat_vice_hodnoty=True, minimum_clanku=False):
    """
    zjištuje průměr indikátorů za jednotlivé roky, vykresluje graf. Zároveň zjišťuje o kolik % jednotlivé indikátory klesly. 
    """
    
    data = data[data[indikator].notna()]
    data = data[data[groupby].notna()]
    
    data[indikator] = pd.to_numeric(data[indikator])
    
    
    if priprava_dat_vice_hodnoty == True:
        
        adapted_data = prepare_dataframe_for_multivalues(data, groupby, proportion=indikator)
    
    if priprava_dat_vice_hodnoty == False:
        adapted_data = data
    #--příprava dat--
    if minimum_clanku is not False:

        adapted_data = redukuj_kategorie_pri_nizkych_poctech(adapted_data, minimum_clanku, groupby)
    prepared_dataset = adapted_data[['list_PY', indikator, groupby]]

    if median_or_mean == "mean":
        tabulka = prepared_dataset.groupby([groupby, "list_PY"]).mean().unstack(level=-1)
    if median_or_mean == "median":
        tabulka = prepared_dataset.groupby([groupby, "list_PY"]).median().unstack(level=-1)
    #tabulka.columns = ['2017', '2018', '2019', '2020', '2021']
    print("tabulka")
    
    data = tabulka.reset_index()
    data.set_index(groupby, inplace=True)
    data.columns = ['2017', '2018', '2019', '2020', '2021']
    df = data.T
    
    
    #--vizualizace--

    fig, ax = plt.subplots(1,1, figsize = (8,5), dpi = 150)
    ax.set_ylabel(str(indikator))
    df.plot(ax=ax)

    percentage_df = data.pct_change(axis='columns')

    for i, column in enumerate(data):
        if not column == '2017': #no point plotting NANs
            for val1, val2 in zip(data[column], percentage_df[column]):
                ax.annotate(
                    text = round(val2, 2), 
                    xy = (i, val1), #must use counter as data is plotted as categorical
                    fontsize = 5
                    )
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 6})
    plt.grid(linestyle='-', linewidth=0.23)
    plt.title(str(median_or_mean) + " indikátoru za sledované roky - podle " + str(groupby))
    plt.show()

        
   

def zjisti_podil_dokumentu_v_agregatorech(data, groupby=False, vizualizace=False, minimum_clanku=False):
    """
    Zjištuje dostupnost v jednotlivých agregátorech a následně i počet nulových hodnot indikátoru pro daný agregator
    Umí to i GroupBy (pokud se do argumentu pro groupby vloží dvě kategorie oddělené čárkou, pak se data seskupí podle obou kategorií. př.: groupby="research_categories, list_DT")
    
    """
    if groupby is not False:
        if "," in groupby:
            multi_groupby = groupby.split(", ")
            data2 = prepare_dataframe_for_multivalues(data, multi_groupby[0])
            data2 = prepare_dataframe_for_multivalues(data2, multi_groupby[1])
        if "," not in groupby:
            data2 = prepare_dataframe_for_multivalues(data, groupby)
        
        df_group_by = DataFrame()
        if minimum_clanku is not False:
            data2 = redukuj_kategorie_pri_nizkych_poctech(data2, minimum_clanku, groupby)
            print(data2)

    celkovy_pocet_zaznamu = len(data)

    pocet_hledane_hodnoty_plumX, pocet_nenulovych_plumX, procentuelne_k_dispozici_plumX, procentuelne_chybi_plumX = vypocti_pomer_zaznamu(data, celkovy_pocet_zaznamu, "available_plumx", False)
    pocet_hledane_hodnoty_Altmetric, pocet_nenulovych_Altmetric, procentuelne_k_dispozici_Altmetric, procentuelne_chybi_Altmetric = vypocti_pomer_zaznamu(data, celkovy_pocet_zaznamu, "available_altmetrics", False)
    if groupby is not False:
        if "," in groupby:
            multi_groupby = groupby.split(", ")
            multi = True
            counter_of_occurences = data2.groupby([multi_groupby[0], multi_groupby[1]]).size().to_frame('counts').reset_index()
            
            

            df11=data2.groupby([multi_groupby[0], multi_groupby[1]])["available_plumx"].apply(lambda x: (x==True).sum()).reset_index(name=str("available_plumx") + '_celkem')
            df_group_by[str("available_plumx") + '_celkem'] = df11[str("available_plumx") + '_celkem']
            #df_group_by[str(multi_groupby[1])] = df11[multi_groupby[1]]
            df_group_by.insert(0, "next_group_by", df11[multi_groupby[1]])

            df11=data2.groupby([multi_groupby[0], multi_groupby[1]])["available_altmetrics"].apply(lambda x: (x==True).sum()).reset_index(name=str("available_altmetrics") + '_celkem')
            
            
            df_group_by[str("available_altmetrics") + '_celkem'] = df11[str("available_altmetrics") + '_celkem']
            df_group_by[str(multi_groupby[1])] = df11[str(multi_groupby[1])]
            df_group_by.columns = df_group_by.columns.str.lstrip()

            
            df_group_by.insert(0, "main_group_by_category", df11[str(multi_groupby[0])])
            df_group_by.set_index("main_group_by_category", inplace=True)

            a = counter_of_occurences["counts"].to_frame("counts")
            print(a)
            #b = data2[multi_groupby[1]].value_counts().rename_axis('unique_values' + str(multi_groupby[0])).to_frame('counts')
            
        
        if "," not in groupby:
            multi = False
            df11=data2.groupby(groupby)["available_plumx"].apply(lambda x: (x==True).sum()).reset_index(name=str("available_plumx") + '_celkem')
            df_group_by[str("available_plumx") + '_celkem'] = df11[str("available_plumx") + '_celkem']
            
            df11=data2.groupby(groupby)["available_altmetrics"].apply(lambda x: (x==True).sum()).reset_index(name=str("available_altmetrics") + '_celkem')
            df_group_by[str("available_altmetrics") + '_celkem'] = df11[str("available_altmetrics") + '_celkem']

            df_group_by.columns = df_group_by.columns.str.lstrip()

            df_group_by.insert(0, "group_by_kategorie", df11[groupby])
            df_group_by.set_index("group_by_kategorie", inplace=True)

            a = data2[groupby].value_counts().rename_axis('unique_values').to_frame('counts')
            #a.reset_index(inplace=True)
            print(a)


        df_group_by.reset_index(inplace=True)
        
        #--toto funguje pro single groupby, je otázkou jestli to bude fungovat i pro multiple groupby, pokud ne, odkomentuj řádek níž--
        if multi is False:
            df_group_by = pd.merge(df_group_by, a, left_on='group_by_kategorie', right_on='unique_values')
            df_group_by.rename(columns={'counts': 'celkovy_pocet_vyskytu'}, inplace=True)
        
        if multi is True:
            df_group_by["celkovy_pocet_vyskytu"] = a["counts"] #TOHLE BY MĚLO FUNGOVAT I PRO MULTI GROUPBY .. ODKOMENTUJ (nefunguje to ale pro single)
           # df_group_by.insert(1, "next_group_by", a["counts"]) #tohle je asi nepotřebné..

        df_group_by["Procentualně_k_dispozici_PlumX"] = 100-((df_group_by.celkovy_pocet_vyskytu - df_group_by.available_plumx_celkem) / df_group_by.celkovy_pocet_vyskytu * 100)
        df_group_by["Procentualně_k_dispozici_Altmetrics"] = 100-((df_group_by.celkovy_pocet_vyskytu - df_group_by.available_altmetrics_celkem) / df_group_by.celkovy_pocet_vyskytu * 100)
        

    """THE THING BELLOW IS THE REAL THING - odkomentuj v případě, že chceš zjistit počty i pro další indikátory"""
    """
    TODO asi bych potřeboval spíš nějakou funkci, která mi pro každý obor řekne, který indikátor a agregátor je pro ten obor nejvyužívanější - tzn. ne nulový poměr
    ale spíš nějakej něco jiného, - jestli průměr? nebo nějaký procentuální přepočet? 
    """
    # indikatory_plumX_dostupne = ["capture", "citation", "mentions", "socialMedia", "usage"]
    # for indikator in indikatory_plumX_dostupne:
    #     vypocti_pomer_zaznamu(data, pocet_nenulovych_plumX, indikator, 0)
    #     if groupby is not False:
    #         df11=data2.groupby(groupby)[indikator].apply(lambda x: (x==0).sum()).reset_index(name=str(indikator) + '_count_0')
    #         df_group_by[str(indikator) + '_count_0'] = df11[str(indikator) + '_count_0']

    # indikatory_altmetric_dostupne = ["tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetric", "mendeley_altmetrics", "score_altmetrics"]
    # for indikator in indikatory_altmetric_dostupne:
    #     vypocti_pomer_zaznamu(data, pocet_nenulovych_Altmetric, indikator, 0)
    #     if groupby is not False:
    #         df11=data2.groupby(groupby)[indikator].apply(lambda x: (x=="0").sum()).reset_index(name=str(indikator) + '_count_0')
    #         df_group_by[str(indikator) + '_count_0'] = df11[str(indikator) + '_count_0']
    
    if groupby is not False:


        print(df_group_by)

        # vypíše dataframe do file
        # tfile = open('dfgroupby_podily2.txt', 'a')
        # tfile.write(df_group_by.to_string())
        # tfile.close()


    #vizualizace - jen v případě že není multiple groupby
    if vizualizace is True and groupby is not False:

        df_group_by = df_group_by.set_index('group_by_kategorie')
        sns.set()
       
        fig = plt.figure(figsize=(7,7)) # Create matplotlib figure

        ax = fig.add_subplot(111) # Create matplotlib axes

        #ax.invert_yaxis() 
        width = .3

        df_group_by["Procentualně_k_dispozici_PlumX"].plot(kind='barh',color='green',ax=ax,width=width, position=0)
        df_group_by["Procentualně_k_dispozici_Altmetrics"].plot(kind='barh',color='red', ax=ax,width = width,position=1)

        ax.set_ylabel(groupby)
        ax.set_xlabel('Procentuelně k dispozici')
        ax.bar_label(ax.containers[0], label_type='edge', fmt='%.1f', fontsize=11)
        ax.bar_label(ax.containers[1], label_type='edge', fmt='%.1f', fontsize=11)

        l = plt.legend()
        l.get_texts()[0].set_text('PlumX')
        l.get_texts()[1].set_text('Altmetrics')
        
        # rects = ax.patches
        # for bar in rects:
        #     plt.annotate(format(bar.get_height(), '.2f'), (bar.get_x() + bar.get_width() / 2, bar.get_height()), ha='center', va='center', size=15, xytext=(0, 8), textcoords='offset points')
        plt.title("Pokrytí dokumentů v agregátorech dle " + str(groupby) + " (v %)")
        plt.show()
    
    if vizualizace is True and groupby is False:
        fig = plt.figure()

        langs = ["PlumX", "Altmetrics.com"]
        students = [procentuelne_k_dispozici_plumX, procentuelne_k_dispozici_Altmetric]
        plt.bar(langs, students, width = 0.4)
        plt.title("Poměr dostupných dokumentů v agregátorech (vyjádřeno v %)")
        plt.grid(axis='y', linewidth=0.3)
        plt.ylim(0,100)
        plt.show()


def vypocti_pomer_zaznamu(data, celkem, zkoumany_indikator, jednotka):
    """
    Tato funkce slouží pouze jako součást své nadřazené funkce *zjisti_podil_nulovych_hodnot()*
    Tato funkce vypočítá poměr zastoupení pro zkoumaný indikátor vzhledem k celkovému počtu záznamů
    Celkový počet záznamů se můžu pro agregátory lišit (proto musí být na vstupu "celkem", protože to nejde snadno automatizovat)
    vstup "jednotka" - určuje hledanou hodnotu (zpravidla se řeší jestli tam bude False nebo 0)
    """

    pocet_hledane_hodnoty = data[zkoumany_indikator].value_counts()[jednotka]

    nenulove = celkem - pocet_hledane_hodnoty
    procentuelne_k_dispozici = (nenulove / celkem) * 100
    procentuelne_chybi = 100 - procentuelne_k_dispozici

    print("-------" + zkoumany_indikator + "---------")
    print("Celkový počet záznamů:", celkem)
    print("Počet nulových záznamů:", pocet_hledane_hodnoty)
    print("Počet nenulových záznamů:", nenulove)
    print("Procentuálně chybí:", procentuelne_chybi)
    print("Procentuálně k dispozici:", procentuelne_k_dispozici)
    print()


    return pocet_hledane_hodnoty, nenulove, procentuelne_k_dispozici, procentuelne_chybi


def zjisti_vlivne_faktory(data, indikator, faktor, vizualizace):
    """
    CÍLEM TÉTO FUNKCE JE ZJISTIT ZDALI ZKOUMANÝ FAKTOR NĚJAK OVLIVŇUJE HODNOTU INDIKÁTORU
    př: zda-li počet stránek článku může mít vliv na hodnotu altmetric_score
    -indikátor je závislá proměnná -> indikátor závisí na faktoru
    -faktor je nezávislá proměnná
    The dependent features are called the dependent variables, outputs, or responses.
    The independent features are called the independent variables, inputs, or predictors
    """
    #zahatuji řádky, ve kterých se vyskytne NaN pro zkoumaný sloupec
    df = data[data[indikator].notna()] 
    data = df[df[faktor].notna()]
    data = prepare_dataframe_for_multivalues(data, faktor)#, indikator) #TODO indikátor nefunguje v tomhle případě 

    if str(data[faktor].dtype) == "object" or str(data[faktor].dtype) == "str":
        vizualizace = False

        X_regressors = data[[indikator]].to_numpy().reshape((-1, 1))
        X_regressors = X_regressors.astype(float)
        Y_predictor = pd.get_dummies(data=data[faktor], drop_first=False) #https://stackoverflow.com/questions/34007308/linear-regression-analysis-with-string-categorical-features-variables
        #print(Y_predictor)
        X_regressors = np.log(1 + X_regressors)
        
    if str(data[faktor].dtype) == "int64" or str(data[faktor].dtype) == "bool" or str(data[faktor].dtype) == "float":

        X_regressors = data[[indikator]].to_numpy().reshape((-1, 1))
        X_regressors = X_regressors.astype(float)
        Y_predictor = data[[faktor]].to_numpy()
        Y_predictor = Y_predictor.flatten() #pro model je potřeba 1D pole, o to se stará "flatten()"
        
        X_regressors = np.log(1 + X_regressors) #https://sci-hub.se/10.2200/S00733ED1V01Y201609ICR052 for skewed data
    #Y_predictor = np.log(1 + Y_predictor)

    # print("Počet článku ze kterého lineární regrese vychází:")
    # print("Regresor: " + str(len(X_regressors)), "Prediktor: " + str(len(Y_predictor))) #TODO - zjistit co vše se započítává, jestli i nulové hodnoty? 
  


#---------------------real thing-----------------------------  
    model = LinearRegression()

    model.fit(X_regressors, Y_predictor)


    score = model.score(X_regressors, Y_predictor)
    intercept = model.intercept_
    coef = model.coef_
    prediction = model.predict(X_regressors)
    #print("intercept_", intercept)
    score = '{0:.10f}'.format(score) #formátuji score abych nedostával výsledek jako exponenciální číslo (například: 2.364e-5)
    
    print("Score -> " + str(score) + "  " + str(indikator) +" / "+ str(faktor))
    #print("coef", coef)
    #print("predict", prediction)

#--------NEGATIVE BINOMINAL REG----------------
    
    # model_NB = sm.NegativeBinomial(X_regressors, Y_predictor).fit()
    # print(model_NB.summary())




   
   
    # #-----------------------------------
    #---JINÁ KNIHOVNA, ALE DĚLÁ TO SAMÉ---
    # #-----------------------------------

    # data[indikator] = data[indikator].astype(float)
    # data[faktor] = data[faktor].astype(float)

    # x = data[indikator].tolist()
    # y = data[faktor].tolist()


    # x = sm.add_constant(x)
    # result = sm.OLS(y, x).fit()
    # print(result.summary())



    # if vizualizace is True:
        
    #     plt.scatter(X_regressors, Y_predictor, color = 'red')
    #     plt.plot(X_regressors, model.predict(X_regressors), color = 'blue')
    #     plt.title(str(indikator) +" vs. "+ str(faktor))
    #     plt.xlabel(indikator)
    #     plt.ylabel(faktor)
    #     plt.show()

        # X_regressors = X_regressors.flatten()
        # plt.plot(X_regressors, Y_predictor, 'o')
        # m, b = np.polyfit(X_regressors, Y_predictor, 1)
        # plt.plot(X_regressors, m*X_regressors + b)
        # plt.show()

    #return score


def cyklus_vlivne_faktory(funkce, dataset, vizualizace=False):
    """
    Tato funkce volá ve forcyklu funkci "zjisti_vlivne_faktory()". Jejím cílem je zavolat zmíněnou funkci pro všechny potřebné vstupy.
    """
    faktory = ["list_DT","list_LA","pocet_autoru", "interdistiplinarita", "open_access", "list_PG", "list_Flesch", "pocet_slov_AB", "pocet_slov_TI", "funding", ] #"mezinarodni_spoluprace"
    indikatory = ["list_TC","tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetric", "mendeley_altmetrics", "score_altmetrics", "capture", "citation", "mentions", "socialMedia", "usage"]
    for indikator in indikatory:
        for faktor in faktory:
            r = funkce(dataset, indikator, faktor, vizualizace)
        print("---------------")  





def redukuj_kategorie_pri_nizkych_poctech(data, hodnota, hlidany_sloupec):
    """
    Tato funkce zařídí to, že se neberou v potaz kategorie u Groupby, které mají malý počet článku.
    "hodnota" určuje, co je zač ten malý počet. "hlidany_sloupec" je sloupec který se groupuje.
    TATO FUNKCE SE NEVOLÁ RUČNĚ, VYUŽÍVAJÍ JÍ OSTATNÍ FUNKCE
    
    """
    procento_nebo_pocet = "procento" #"pocet"


    print("redukuj_kategorie_pri_nizkych_poctech(): PROBÍHÁ PŘÍPRAVA DAT...")
    if procento_nebo_pocet == "procento":
        pocet_clanku = len(data)
        minimalni_potrebny_pocet = (pocet_clanku / 100) * hodnota
        print("minimalni_potrebny_pocet_článků:", minimalni_potrebny_pocet)
    elif procento_nebo_pocet == "pocet":
        minimalni_potrebny_pocet = hodnota
    else:
        print('CHYBA -> funkce: redukuj_kategorie_pri_nizkych_poctech() --> vyberte buď "procento" nebo "pocet"')
    
    #data = data[data[hlidany_sloupec].notna()]
    data[hlidany_sloupec].replace('', np.nan, inplace=True)
    data = data[data[hlidany_sloupec].notna()]
    #print(data[hlidany_sloupec])
    

    #data[hlidany_sloupec] = data[hlidany_sloupec].apply(str)


    list_unikatnich_hodnot = data[hlidany_sloupec].unique()

    list_unikatnich_hodnot = list(list_unikatnich_hodnot)

    for hodnota in list_unikatnich_hodnot:
        #pocet = data[hlidany_sloupec].value_counts()[str(hodnota)]
        if hodnota == "Correction" or hodnota == "Proceedings Paper" or hodnota == "Review" or hodnota =="Letter" or hodnota == "Retraction":
            continue
        else:
            pocet = len(data[data[hlidany_sloupec] == str(hodnota)])
            if pocet < minimalni_potrebny_pocet:
                data.drop(data[data[hlidany_sloupec] == str(hodnota)].index, inplace=True)

    
    return data






#========================================================================================
#faktory = ["typ_dokumentu","pole_LA","pocet_autoru", "interdisciplinarita", "open_access", "pole_PG", "Flesch", "pocet_slov_AB", "pocet_slov_TI", "funding", ] #"mezinarodni_spoluprace"
#indikatory = ["pole_TC","tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", "score_altmetrics", "capture_plumx", "citation_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"]


###r = zjisti_vlivne_faktory(df, "tweetovani_altmetrics", "list_LA", False)

#zjisti_vlivne_faktory(df, "mendeley_altmetrics", "open_access", False)

#cyklus_vlivne_faktory(zjisti_vlivne_faktory, df, False)

#-------------------------------------------------------------



#zjisti_podil_dokumentu_v_agregatorech(df, groupby="funding", vizualizace=True)#, minimum_clanku=1) #"research_categories, list_DT") 


#disciplinary_and_time_differences(data=df, indikator="pole_TC", groupby="funding", median_or_mean="mean", minimum_clanku=1)

#zjisti_korelaci(df, "pole_TC", "mendeley_altmetrics",  typ_korelace="pearson", vizualizace=True, minimum_clanku=1, group_by="typ_dokumentu")


#faktory = ["typ_dokumentu","pole_LA", "interdisciplinarita", "open_access", "funding", "mezinarodni_spoluprace", "kategorie_WC"]



#zjisti_korelaci(df, "pole_TC", "usage_plumx",  typ_korelace="pearson", vizualizace=False, minimum_clanku=1, group_by=faktor)