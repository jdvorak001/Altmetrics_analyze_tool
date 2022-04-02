from logging import captureWarnings
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from scipy.stats.stats import pearsonr
import scipy.stats as stats
from scipy.stats import wilcoxon
from scipy.stats import mannwhitneyu
from scipy.stats import gmean
from test_for_corr import independent_corr
import warnings
warnings.filterwarnings("ignore")
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

                    #ODSTRANĚNO PRO ZENODO KVŮLI ANONYMIZACI:
                    #pocet_slov_AB
                    # pole_C1
                    # title
                    # pocet_slov_TI
                    # pole_FU
                    # doi



#df = pd.read_csv(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_test_9.csv", sep=";", header=None, names=column_names)
df = pd.read_csv(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_real_data.csv", sep=";", header=None, names=column_names)
df.replace(to_replace=["None"], value=np.nan, inplace=True)  # tento řádek se stará o prázdné hodnoty, které převádí z Pythonovské syntaxe do Pandas syntaxe
df = df[df["list_PY"] != 2022] #z nějakého důvodu se mi stáhly i články za roky 2022, proto je odstraňuji
df = df[df["list_PY"].notnull()] #některé články nemají žádnou informaci o roku. Proto je odstraňuji, protože si nemohu být jistý, že se tam nevtrousili ještě nějaké další např z roku 2022

df02 = pd.read_csv(r"C:\Users\UKUK\Desktop\DP Altmetrie\Script\csv_data_real_data_druhe_stazeni.csv", sep=";", header=None, names=column_names)
df02.replace(to_replace=["None"], value=np.nan, inplace=True)  # tento řádek se stará o prázdné hodnoty, které převádí z Pythonovské syntaxe do Pandas syntaxe
df02 = df02[df02["list_PY"] != 2022] #z nějakého důvodu se mi stáhly i články za roky 2022, proto je odstraňuji
df02 = df02[df02["list_PY"].notnull()]

def zjisti_korelaci(data, sloupec_A, sloupec_B, typ_korelace, vizualizace=False, group_by=False, minimum_clanku=False, top_hodnoty=False, zjisti_p_value=False):
    """
       *data => vlož dataframe z pandas*
       *sloupec_A a sloupec_B => sloupce z dataframu, kde se hledá závislost*
       *typ korelace => 'spearman' 'pearson' 'kendall'* 
       *vizualizace => True False #generuje graf*
       -vizualizace se zobrazí pouze u spearmanové korelace. Ostatní negenerují graf.
       *group_by = které hodnoty má seskupovat - vypočítá korelaci pro každou kategorii - pokud je vizualizace zapnuta, vytvoří graf pro každou kategorii
       *minimum_clanku ==> určuje, kolik musí být v dané kategorii článku aby byla vykreslena a spočítána a brána v úvahu
       *top_hodnoty => pokud uživatel chce vykresilit pouze top n hodnot, které nejvíce korelují./// TODO zatím to nefunguje u Spearmana.. je potřeba opravit .. teď funguje jen u pearsona
    """
    data = data[data[sloupec_A].notna()]
    data = data[data[sloupec_B].notna()]
    data[sloupec_A] = pd.to_numeric(data[sloupec_A])
    data[sloupec_B] = pd.to_numeric(data[sloupec_B]) #, errors='coerce'

    if typ_korelace == "pearson":
        #print("Pro pearsonovu korelaci převádím data do logaritmického měřítka...")
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
        stats_df = data.groupby([group_by]).size().reset_index(name='counts')
        
        stats_df.set_index(group_by, inplace=True)
        print(stats_df)
        print(stats_df.iloc[0]["counts"])
        print(stats_df.iloc[1]["counts"])
        
        
        korelace = grouped.corr(data[sloupec_B], method=typ_korelace)
        #merged_df = pd.merge(korelace, stats_df, on="kategorie_WC")

        # korelace = data.filter(items=[sloupec_A, sloupec_B]).corr(method=typ_korelace)
        # sns.heatmap(korelace)
        # plt.show()
    print("Typ korelace:", typ_korelace)
    print(korelace)
    
    if zjisti_p_value is True and group_by is not False:
    # print("zkouška lokace")
        corr1 = korelace.loc["False"]
        corr2 = korelace.loc["True"]
        count1 = stats_df.loc["False"]
        count2 = stats_df.loc["True"]
    # print("--------tady-----------")
    # print("count1 tady:",count1.item())
    # print("count2 tady:",count2.item())

        korelace = korelace.reset_index()

        #print("significance test:")
        print(independent_corr(corr1.item(), corr2.item(), count1.item(), count2.item(), method='fisher')[1]) #return Z and P-Value -> [1] je P-value
    
    korelace = korelace.reset_index()

    if top_hodnoty is not False and typ_korelace == "pearson":
        korelace = korelace.nlargest(top_hodnoty, 'pole_TC')
        #print("nlarge")
        #print(korelace)
 
    #print(merged_df) 
    
    #vypíše dataframe do file
    # with open("korelace_df_counts.txt", 'a') as f:
    #     dfAsString = merged_df.to_string(header=False, index=False)
    #     f.write(dfAsString)

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
            data.sort_values("pole_TC", inplace = True)
            sns.set_theme(style="darkgrid")

            g = sns.FacetGrid(data, col=group_by, col_wrap=4) #, xlim=(0,800), ylim=(0,800))  # toto dělá čtverec z grafu
            g.map(sns.regplot, "Rank_A", "Rank_B")
            col_order = grouped.groups.keys() #toto zjištuje jaké typy z group_by existují; důležité je pořadí, jinak jsou grafy špatně vykresleny :-) (nepoužívat. unique()) 
            print(type(col_order), col_order)
            for txt, title in zip(g.axes.flat, col_order):
                txt.set_title(title)   
                # add text
                txt.text(10, 120, "ρ = " + str(korelace[title]), fontsize = 12)
                # val = korelace.loc[korelace[group_by] == title, "pole_TC"].iloc[0]
                # txt.text(0.5, 0.5, "ρ = " + str(val), fontsize = 12)

    
            #sns.lmplot(data=data, x="Rank_A", y="Rank_B", col=group_by, col_wrap=2)
            plt.show()

    if vizualizace is True and typ_korelace == "pearson":
        if group_by is False:
            

            sns.set_theme(style="darkgrid")

            sns.lmplot(data=data, x=sloupec_A, y=sloupec_B, scatter_kws={'s':7, 'alpha': 0.03}, line_kws={'color': 'coral'}, height=3.4) #TODO - zde nastavit správnou průhlednost 
            plt.text(5.5, 0.5, "ρ = " + str("%.2f" % korelace), fontsize = 12)

            plt.show()
        if group_by is not False:
            list_pouzivanych_hodnot = korelace[group_by].to_list()
            #print(list_pouzivanych_hodnot)
            data = data.loc[data[group_by].isin(list_pouzivanych_hodnot)]


            data = make_order_in_top_plots(data, korelace)


            #print(data)

            g = sns.FacetGrid(data, col=group_by, col_wrap=5)
            if top_hodnoty is not False:
                g.map(sns.regplot, sloupec_A, sloupec_B, scatter_kws={'s':5, 'alpha': 0.5}, line_kws={"color": "coral"})
            if top_hodnoty is False:
                g.map(sns.regplot, sloupec_A, sloupec_B, scatter_kws={'s':5, 'alpha': 0.03}, line_kws={"color": "coral"})
            col_order = data[group_by].unique() #toto zjištuje jaké typy z group_by existují 
            #print(type(col_order), col_order)
            for txt, title in zip(g.axes.flat, col_order):
                txt.set_title(title, fontsize=10) #fontsize=9
                # add text
                #print(korelace[title])
                #txt.text(0.5, 0.5, "ρ = " + str(korelace[title]), fontsize = 12)
                val = korelace.loc[korelace[group_by] == title, "pole_TC"].iloc[0]
                txt.text(0.5, 0.5, "ρ = " + str(val), fontsize = 12)

            #sns.lmplot(data=data, x=sloupec_A, y=sloupec_B, col=group_by, col_wrap=2)
            plt.show()



# def zjisti_altmetricke_pokryti(group_by):
#     """
#     Cílem je výstup, který mi dá hodnotu/poměr mezi články spadající do zkoumané kategorie a počet těch, které v dané kategorii nemají záznam v Altmetric.com nebo PlumX
#     př.: Medical Science = ze 180 článku jich má záznam 54 .. (54/180)
#     Jde o to zjistit, co má největší počet záznamů 
#     """
def make_order_in_top_plots(data, korelace_df):
    """tato funkce slouží pouze pro vizualizaci korelace. Jejím cílem je zajistit, aby vizualizované grafy byly seřazeny od největší naměřené hodnoty po nejemenší.
       Seaborn totiž neumí grafy seřazovat tak jak bych potřeboval. Proto bylo využito vlastnosti knihovny seaborn, která řadí grafy podle titlu, na který narazí nejdříve. 
       Funkce "make_order_in_top_plots" pak mění pořadí řádku v dataframu aby seaborn narazil najdříve na ty titly, na který potřebuji, tím je pak zaručeno seřazení.    
    """
    korelace_df.reset_index(inplace = True)
    data.reset_index(inplace = True)
    print(korelace_df)
    korelace_df.sort_values(by=['pole_TC'], ascending=False, inplace=True)
    colname = korelace_df.columns[1]
    list_sort = korelace_df[colname].to_list()
    helpful_dataframe = DataFrame()
    helpful_dataframe = data[0:0]
    print(data)
    for l in list_sort:
        a_iter = 0
        for i in data[colname]:
            # print(a_iter)
            # print(i)
            # print(l)
            if l == i :


                helpful_dataframe.loc[data.index[a_iter]] = data.iloc[a_iter]
                radek = data.iloc[a_iter]
                doi_smazat = str(radek["doi"])
                data.drop(data[data['doi'] == doi_smazat].index, inplace = True)
                # data.reset_index(inplace = True)

                
                
                #data.loc[1], data.loc[a_iter] = data.loc[a_iter], data.loc[1]
                #data.loc[1] = data.loc[a_iter]
                #data.reset_index(inplace = True)
                a_iter += 1
                break
            a_iter += 1
    

    result = helpful_dataframe.append(data)

    print(list_sort)
    return result
    
#['Geography, Physical', 'Chemistry, Multidisciplinary', 'Polymer Science', 'Chemistry, Analytical', 'Electrochemistry']




def prepare_dataframe_for_multivalues(data, column_to_check, proportion=False):
    """
    NEVOLÁ SE RUČNĚ, JE VYUŽÍVANÁ DALŠÍMI FUNKCEMI
    Tato funkce řeší problém toho, že některé sloupce mají více hodnot v jedné buňce, z pravidla oddělené středníkem.
    Pokud je proportion False, tak každému novému řádku přidělí sledovaný indikátor 100%. Pokud je v proportion uvedený sledovaný indikátor, tento indikátor podělí mezi ostatní nově vzniklý řádky tzn. férovým podílem každé kategorii 1/n 
    """
    
    #print("prepare_dataframe_for_multivalues(): PROBÍHÁ PŘÍPRAVA DAT")
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
    #data[proportion] = data[proportion].astype(int) #TOHLE JSEM PŘIDAL NOVĚ, NEMĚLO BY TO DĚLAT NEPLECHU. ALE KDY NÁHODOU TAK KOUKNI SEM
    data[column_to_check] = data[column_to_check].astype(str) 
    data[column_to_check] = data[column_to_check].str.replace("; ", ";")# my mistake - some columns have different separator - extra space - this can deal with that mistake
    asn_lists = data[column_to_check].str.split(';')         # split strings into list
    
    data[column_to_check] = asn_lists                        # replace strings with lists in the dataframe

    
    df2 = data.explode(column_to_check)                      # explode based on the particular column


    if proportion is not False:
        try:
            df2[proportion] /= df2[proportion].groupby(level=0).transform('count') # hodnotu zkoumaného indikátoru rozdělí pro každou kategorii ve férovém podílu
        except TypeError:
            df2[proportion] = df2[proportion].astype(int)
            df2[proportion] /= df2[proportion].groupby(level=0).transform('count')
       #df2 = data.explode(column_to_check).assign(**{proportion: lambda d: d.groupby(level=0)[proportion].apply(lambda s:s/len(s))})

#------TOHLE PRINTĚNÍ JE DOBRÁ VĚC, ODKOMENTUJ V PŘÍPADĚ POTŘEBY----------
    # print(len(data), "delka originálního dataframu")
    # print(len(df2), "delka dataframu po vyřešení multivalues")
    # print("------------------------")

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

        #vypíše dataframe do file
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


#MUSÍ SE JEŠTĚ DODĚLAT TATO FUNKCE -> ZJISTIT PRŮMĚRY JAK SE ZMĚNILY
def get_different_rows(source_df, new_df, sledovany_indikator):
    """Vrací řádky ve kterých proběhla změna a současně vypočítá kolik řádků se změnilo
        Na vstupu je původní dataset, nově naměřený dataset po určitém časovém období a určí se sledovaný indikátor, pro který se má sledovat změna.
        (tzn. sledují se pouze změny pro jeden indikátor)    
    """
    
    prepared_source_df = source_df[["doi", sledovany_indikator]]
    prepared_new_df = new_df[["doi", sledovany_indikator]]
    
    merged_df = prepared_source_df.merge(prepared_new_df, indicator=True, how='outer')
    changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
    
    changed_rows_dataframe = changed_rows_df.drop('_merge', axis=1)
    
    delka_source_df = source_df.shape[0] #vrátí počet řádků původního dataframu
    pocet_zmenenych_radku = changed_rows_dataframe.shape[0]


    procentuelne_zmenenych = (pocet_zmenenych_radku / delka_source_df) * 100

    print(changed_rows_dataframe)
    print("Celková délka dataframu:", len(prepared_source_df))
    print("Počet řádků, kterým se změnila hodnota indikátoru:", pocet_zmenenych_radku)
    print("Změna vyjádřena procentuelně:", procentuelne_zmenenych)

    prepared_source_df[sledovany_indikator] = prepared_source_df[sledovany_indikator].astype('float')
    prepared_new_df[sledovany_indikator] = prepared_new_df[sledovany_indikator].astype('float')

    prepared_source_df = prepared_source_df[prepared_source_df[sledovany_indikator].notna()]
    prepared_new_df = prepared_new_df[prepared_new_df[sledovany_indikator].notna()]

    prumer_mereni_1 = prepared_source_df[sledovany_indikator].mean()
    prumer_mereni_2 = prepared_new_df[sledovany_indikator].mean()

    median_mereni_1 = prepared_source_df[sledovany_indikator].median()
    median_mereni_2 = prepared_new_df[sledovany_indikator].median()

    max_mereni_1 = prepared_source_df[sledovany_indikator].max()
    max_mereni_2 = prepared_new_df[sledovany_indikator].max()

    # prepared_source_df = prepared_source_df[prepared_source_df[sledovany_indikator].notna()]
    # prepared_new_df = prepared_new_df[prepared_new_df[sledovany_indikator].notna()]

    array_1 = prepared_source_df[sledovany_indikator].to_numpy()
    array_2 = prepared_new_df[sledovany_indikator].to_numpy()



    percentile99_1 = np.percentile(array_1, 99)
    percentile99_2 = np.percentile(array_2, 99)
    # print(array_1)

  


    #https://help.altmetric.com/support/solutions/articles/6000241983-faq-why-has-the-altmetric-attention-score-for-my-paper-gone-down-
    # radek_max1 = prepared_source_df[prepared_source_df[sledovany_indikator] == prepared_source_df[sledovany_indikator].max()] #vrátí celý řádek z dataframu pro hodnotu, která je v množině nejvyšší -- potřeboval jsem DOI
    # radek_max2 = prepared_new_df[prepared_new_df[sledovany_indikator] == prepared_new_df[sledovany_indikator].max()]

    # print(radek_max1)
    # print(radek_max2)

    # print(prumer_mereni_1)
    # print(median_mereni_1)
    # print(max_mereni_1)
    # print("-------druhe meření------")
    # print(prumer_mereni_2)
    # print(median_mereni_2)
    # print(max_mereni_2)
    # print(procentuelne_zmenenych)

    print("percentil 99:")
    print(percentile99_1)
    print(percentile99_2)
    
    return changed_rows_dataframe

#get_different_rows(df, df02, "mendeley_altmetrics")

def encoding_of_variable_for_regression(data, variable_to_encode):
    """funkce převádí kategorické data na matici s 1HOT ENCODING a numerická data zachovává, respektive je připravuje do vhodného formátu"""
    if str(data[variable_to_encode].dtype) == "object" or str(data[variable_to_encode].dtype) == "str" or str(data[variable_to_encode].dtype) == "bool":

        data[variable_to_encode] = data[variable_to_encode].str.replace("; ", ";")
        data[variable_to_encode] = data[variable_to_encode].astype(str) #převod do stringu především kvůli bool proměnným
        faktor = data[variable_to_encode].str.get_dummies(sep=';') #https://stackoverflow.com/questions/18889588/create-dummies-from-column-with-multiple-values-in-pandas


    if str(data[variable_to_encode].dtype) == "int64" or str(data[variable_to_encode].dtype) == "float":
        faktor = data[[variable_to_encode]].to_numpy()
        faktor = faktor.flatten() #pro model je potřeba 1D pole, o to se stará "flatten()"
    
    return faktor

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
    data = data[data[faktor] != "Art Exhibit Review"]
    data = data[data[faktor] != "Biographical-Item"]
    data = data[data[faktor] != "Hardware Review"]
    data = data[data[faktor] != "Software Review"]
    data = data[data[faktor] != "Book Review"]

    #data = prepare_dataframe_for_multivalues(data, faktor)#, indikator) #TODO indikátor nefunguje v tomhle případě 

    Y_predictor = data[[indikator]].to_numpy().reshape((-1, 1))
    Y_predictor = Y_predictor.astype(float)
    Y_predictor = np.log(1 + Y_predictor) #https://sci-hub.se/10.2200/S00733ED1V01Y201609ICR052 for skewed data
    X_regressors = encoding_of_variable_for_regression(data, faktor)

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


#---------------------------------------------------------------------
#--------------------pro stepwise metodu------------------------------
    
    results = sm.OLS(Y_predictor, X_regressors).fit()
    print(results.summary())
    print("AIC: ", results.aic)



    # if vizualizace is True:
        
    #     plt.scatter(X_regressors, Y_predictor, color = 'red')
    #     plt.plot(X_regressors, model.predict(X_regressors), color = 'blue')
    #     plt.title(str(indikator) +" vs. "+ str(faktor))
    #     plt.xlabel(indikator)
    #     plt.ylabel(faktor)
    #     plt.show()

    #     X_regressors = X_regressors.flatten()
    #     plt.plot(X_regressors, Y_predictor, 'o')
    #     m, b = np.polyfit(X_regressors, Y_predictor, 1)
    #     plt.plot(X_regressors, m*X_regressors + b)
    #     plt.show()

    #return score


def cyklus_vlivne_faktory(funkce, dataset, vizualizace=False):
    """
    Tato funkce volá ve forcyklu funkci "zjisti_vlivne_faktory()". Jejím cílem je zavolat zmíněnou funkci pro všechny potřebné vstupy.
    """
    faktory = ["typ_dokumentu","pole_LA","pocet_autoru", "interdisciplinarita", "open_access", "pocet_str", "flesch", "pocet_slov_AB", "pocet_slov_TI", "funding", "mezinarodni_spoluprace"]
    indikatory = ["pole_TC","tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", "score_altmetrics", "capture_plumx", "citation_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"]
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
    procento_nebo_pocet = "pocet"


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
        # if hodnota == "Correction" or hodnota == "Proceedings Paper" or hodnota == "Review" or hodnota =="Letter" or hodnota == "Retraction":
        #     continue
        # else:
        #     pocet = len(data[data[hlidany_sloupec] == str(hodnota)])
        #     if pocet < minimalni_potrebny_pocet:
        #         data.drop(data[data[hlidany_sloupec] == str(hodnota)].index, inplace=True)
        pocet = len(data[data[hlidany_sloupec] == str(hodnota)])
        if pocet < minimalni_potrebny_pocet:
            data.drop(data[data[hlidany_sloupec] == str(hodnota)].index, inplace=True)

    
    return data


def porovnej_faktory(data, faktor, indikator, test):
    """"Funkce vypočítá průměry pro indikátor jednak v případě, že je zastoupený faktor a zároveň v případě, že faktor není zastoupený v dokumentu.
        Současně počítá i test významnosti. Metoda testu může být buď studentův t-test nebo mann-withney test, případně wilcoxon test.
        Funkce neumí vizualizaci. Funkce funguje na zavolání pouze pro jeden faktor a jeden indikátor. Pro analýzu všech indikátoru, využij funkci "vizualizace_vliv_faktoru_na_hodnotu_indikatoru", která umí i vizualizovat výsledek
    """

    
    data[indikator] = data[indikator].astype(np.float64) 
    #data[indikator] = np.log(data[indikator] + 1)
    data.dropna(subset = [indikator], inplace=True)
    print("printuju data pro jonáše:")
    print(len(data))
    df_group1 = data.loc[data[faktor] == True]
    df_group2 = data.loc[data[faktor] == False]

    df_group_nula = data.loc[data[indikator] == 0]
    print(len(data))
    
    print("počet nul:", len(df_group_nula))
    
    # df_group1[indikator] = np.log(1 + df_group1[indikator])
    # df_group2[indikator] = np.log(1 + df_group2[indikator])

    group1 = df_group1[indikator].to_numpy()
    group2 = df_group2[indikator].to_numpy()
    
    #print("Délka:",len(group1), len(group2))

    p = spocti_test_vyznamnosti(group1=group1, group2=group2, test = test)

    #print(faktor, "-", indikator)
    print("P-value:", p)
    print("Průměr -> False:" , group2.mean()) #False
    print("Průměr -> True:" , group1.mean()) #True
    
    print("Počet -> False:", len(group2))
    print("Počet -> True:", len(group1))


    # # print(np.exp(group2.mean()))
    # # print(np.exp(group1.mean()))

    # print(gmean(1+group2))
    # print(gmean(1+group1))

    # plt.hist(data[indikator], bins=550, density=True, alpha=0.5, color='b')
    # plt.show()

def spocti_test_vyznamnosti(group1, group2, test):
    """
    Funkce je součástí ostatních funkcí, ručně se nevola. Funkce počítá test významnosti mezi dvěma průměry. Zjištuje tedy, zdali sledovaný faktor má významný vliv. 
    Na vstupu jsou dvě množiny dat - hodnot indikátoru (první kde je faktor přítomný, druhá, kde faktor není přítomný) a dále test což určuje metodu významnosti, která se má použít.
    """
    if test == "t-test":
        #print(np.var(group1), "/", np.var(group2), "=", np.var(group1)/np.var(group2))
        # print("-----------------------------------------")
        vetsi = max(np.var(group1), np.var(group2))
        mensi = min(np.var(group1), np.var(group2))
        if vetsi / mensi < 4:
            eq_var = True
        else:
            eq_var = False
        #https://www.statology.org/two-sample-t-test-python/
        a = stats.ttest_ind(a=group1, b=group2, equal_var=eq_var)
        p = a.pvalue

        return p


    if test == "wilcoxon":
        stat, p = wilcoxon(group1, group2)
        return p
    
    if test == "mannwhitneyu":
        stat, p = mannwhitneyu(group1, group2)
        #print("p-value:", p)
        return p


def vizualizace_vliv_faktoru_na_hodnotu_indikatoru(df, faktor, typ_grafu, research_area = ""):
    
    

    indikatory_list = [
        "tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics",
        "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", 
        "score_altmetrics", "capture_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"] #pole_TC
    
    # indikatory_list = [
    #     "fb_altmetrics", "blogy_altmetrics",
    #     "reddit_altmetrics", "video_altmetrics","mentions_plumx"]

    pracovni_df_pro_faktor = pd.DataFrame(columns = ['Ind', 'Prumer_True', 'Prumer_False', 'Pocet_True', 'Pocet_False'])


    for indikator in indikatory_list:

        data = df.copy(deep=True) #nechci sahat na originální dataframe, tak si ho radši zkopíruji

        data[indikator] = data[indikator].astype(np.float64)
        data.dropna(subset = [indikator], inplace=True) #odstraní všechny NaN hodnoty/řádky
        df_group1 = data.loc[data[faktor] == True] #vyfiltruji si do nového df řádky jen ty, kde má sledovaný faktor hodnotu true
        df_group2 = data.loc[data[faktor] == False]
        group1 = df_group1[indikator].to_numpy() #z celého dataframu si beru jen a pouze hodnoty indikátoru a převádím je na numpy pole
        group2 = df_group2[indikator].to_numpy()
        prumer_True_hodnot = group1.mean() #počítá průměr ze všech hodnot, pro které je faktor True
        prumer_False_hodnot = group2.mean() #počítá průměr ze všech hodnot, pro které je faktor False
        pocet_True_hodnot = len(group1)
        pocet_False_hodnot = len(group2)
        t_test = spocti_test_vyznamnosti(group1=group1, group2=group2, test ="t-test")

        pracovni_df_pro_faktor = pracovni_df_pro_faktor.append({'Ind' : indikator, 'Prumer_True' : prumer_True_hodnot, 'Prumer_False' : prumer_False_hodnot, 't-test': t_test, 'Pocet_True' : pocet_True_hodnot, 'Pocet_False': pocet_False_hodnot}, ignore_index = True)

        del data #po iteraci odstraním nový dataframe s tím, že při příští iteraci se zase vytvoří novější z originálního dataframu (kdybych ho neodstranil, tak ty změny si bude pamatovat)
    
    #print(pracovni_df_pro_faktor)

    # pracovni_df_pro_faktor.set_index('Ind', inplace=True)
    # pracovni_df_pro_faktor = pracovni_df_pro_faktor.T
    # pracovni_df_pro_faktor.reset_index(inplace=True)
    # #pracovni_df_pro_faktor.set_index('index', inplace=True)
    # pracovni_df_pro_faktor.drop([2,3], axis=0, inplace=True)
    # pracovni_df_pro_faktor.set_index('index', inplace=True)
    # pracovni_df_pro_faktor["Prumer_True"] = pracovni_df_pro_faktor["Prumer_True"].astype(np.float64)
    # pracovni_df_pro_faktor["Prumer_False"] = pracovni_df_pro_faktor["Prumer_False"].astype(np.float64)

    
    #vizualization part.. hooorayy!! (..sarcasm.. yeah.)
    if typ_grafu == "typ_1":    

        pracovni_df_pro_faktor["soucet_pracovni"] = pracovni_df_pro_faktor["Prumer_True"] + pracovni_df_pro_faktor["Prumer_False"]
        pracovni_df_pro_faktor.sort_values(by='soucet_pracovni', ascending=False, inplace=True)
        pracovni_df_pro_faktor.drop(['soucet_pracovni'], axis = 1, inplace=True)

        #xa = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        #xa = [9,18, 27 , 36 , 45, 54 ,63,72,81 , 90 , 99 ,108, 117]
        #xa = [8,16,24,32,40,48, 56, 64, 72, 80, 88, 96,104]
        xa = [10,20,30,40,50,60,70,80,90,100,110,120,130]

        #xa = [10,20,30,40,50]
        x = np.array(xa)
        x= x/3 #ZDE ZMĚN PRO PŘIZPŮSOBENÍ VELIKOSTI GRAFU
        y1 = pracovni_df_pro_faktor["Prumer_True"].to_numpy()
        y2 = pracovni_df_pro_faktor["Prumer_False"].to_numpy()

        
        n = pracovni_df_pro_faktor["Pocet_True"].to_numpy()
        n2 = pracovni_df_pro_faktor["Pocet_False"].to_numpy()
        n = np.append(n, n2)
        aa = (n - 0) / (np.max(n) - 0)
        #aa = (n - np.min(n)) / (np.max(n) - np.min(n))
        aa = aa

        counts_array = np.array_split(aa, 2)

        pocet1 = counts_array[0]
        pocet2 = counts_array[1]
        print(pocet1)
        print(pocet2)
        list_of_single_column_Ind = pracovni_df_pro_faktor['Ind'].tolist()
        print(list_of_single_column_Ind)


        # plot data in grouped manner of bar type
        plt.figure(figsize=(16.5,5))
        sloup1 = plt.bar(x-pocet1, y1, width=pocet1*2) #přidal jsem proměnnou sloup1 aby si to pamatovalo její pozici pro přidání anotace
        sloup2 = plt.bar(x+pocet2, y2, width=pocet2*2)
        plt.xticks(x, list_of_single_column_Ind, rotation=90, fontsize=9)
        plt.xlabel("Indikátory")
        plt.ylabel("Průměr")
        plt.legend(["True", "False"])
        plt.tight_layout()     # tohle zařídí aby byly vidět popisky osy x
        plt.subplots_adjust(left=None, bottom=None, right=None, top=0.909, wspace=None, hspace=None) #toto nastavuje výšku šířku (stejnak jako to tlačíko na vygenerovaném grafu)
        # plt.bar_label(plt.containers[0], label_type='edge')
        plt.bar_label(sloup1, label_type='edge', rotation=90, fontsize=10, fmt='%.3f', padding=3)
        plt.bar_label(sloup2, label_type='edge', rotation=90, fontsize=10, fmt='%.3f', padding=3)
        plt.title("Vliv faktoru " + '"' + faktor + '" ' + research_area )

        plt.show()


    if typ_grafu == "typ_2":

        pct_change_df = pd.DataFrame(columns = ["Ind","pct_change"])
        for index, row in pracovni_df_pro_faktor.iterrows():
            # print(row)
            # print(row["Prumer_True"], row["Prumer_False"])
            # max_num = max(row["Prumer_True"], row["Prumer_False"])
            # min_num = min(row["Prumer_True"], row["Prumer_False"])
            index = row["Ind"]
            # pct_change = ((max_num-min_num)/min_num)*100
            pct_change = ((row["Prumer_True"] - row["Prumer_False"])/row["Prumer_False"])*100
            pct_change_df = pct_change_df.append({'Ind' : index, 'pct_change' : pct_change}, ignore_index = True)


        #print(pct_change_df)


        pracovni_df_pro_faktor = pd.merge(pracovni_df_pro_faktor, pct_change_df, on='Ind')
        print(pracovni_df_pro_faktor)
        pracovni_df_pro_faktor.sort_values(by='pct_change', ascending=False, inplace=True)
        
        pracovni_df_legenda = pracovni_df_pro_faktor.copy(deep=True)
        pracovni_df_legenda.set_index("Ind", inplace=True)
        print("pracovni_df_legenda")
        print(pracovni_df_legenda)

        pracovni_df_pro_faktor.drop(['pct_change'], axis = 1, inplace=True)    

        list_of_single_column_Ind = pracovni_df_pro_faktor['Ind'].tolist()
        non_significatn_values = pracovni_df_pro_faktor[pracovni_df_pro_faktor['t-test']>=0.05]['Ind']
        
        list_non_significatn_values = non_significatn_values.tolist()
        

        pracovni_df_pro_faktor.drop(['t-test'], axis = 1, inplace=True)
        pracovni_df_pro_faktor.rename(columns = {'Prumer_True':'True', 'Prumer_False':'False'}, inplace = True)
        pracovni_df_pro_faktor.set_index('Ind', inplace=True)
        pracovni_df_pro_faktor = pracovni_df_pro_faktor.T
        pracovni_df_pro_faktor.reset_index(inplace=True)
        df_s_pocetem_hodnot = pracovni_df_pro_faktor.copy(deep=True)
        pracovni_df_pro_faktor.drop([2,3], axis=0, inplace=True)


        df_s_pocetem_hodnot.set_index('index', inplace=True)
        df_s_pocetem_hodnot = df_s_pocetem_hodnot.T





        # sns.set()
        custom_params = {"axes.spines.right": False, "axes.labelsize":8, 'legend.title_fontsize': 'xx-small', 'figure.figsize':(6,10)}
        sns.set_theme(style="white", rc=custom_params)
        

        x_radku = 6
        y_sloupcu = 2
        fig, axes = plt.subplots(nrows=x_radku, ncols=y_sloupcu, sharex=True) #define plotting region (x rows, y columns)
        
        #create boxplot in each subplot
        count_radek = 0
        count_sloupec = 0
        count = 0 #pro vykreslování do subplotů
        count2 = 0 #pro šířku sloupců
        for value in list_of_single_column_Ind:
            count_sloupec = count
            if count_sloupec == y_sloupcu: #když to narazí na poslední fig v řadě, začne to přidávat do figů v druhé řadě
                count_sloupec = 0
                count = 0
                count_radek += 1 

            if value in list_non_significatn_values:
                g1 = sns.barplot(x=pracovni_df_pro_faktor['index'], y=pracovni_df_pro_faktor[value], ax=axes[count_radek,count_sloupec], color="silver") #ZMĚNA BARVY V PŘÍPADĚ ŽE T-TEST JE VYŠŠÍ NEŽ 0.05
            else:
                g1 = sns.barplot(x=pracovni_df_pro_faktor['index'], y=pracovni_df_pro_faktor[value], ax=axes[count_radek,count_sloupec]) 
            #g1 = sns.barplot(x=pracovni_df_pro_faktor['index'], y=pracovni_df_pro_faktor[value], ax=axes[count_radek])

            #g1.set(xticklabels=[])
            g1.set(xlabel=None)
            
            g1.bar_label(g1.containers[0], label_type='edge', fontsize=10, fmt='%.3f', padding=-7)
            g1.set_yticklabels(g1.get_yticks(), size = 8)
            g1.set_ylabel(g1.get_ylabel(), fontsize=7, labelpad=1.5)  #rotation=70 #NASTAVENÍ LABELU U OSY Y
            
            #g1.text(0, 0, "Ahoj kámo", fontsize= 7, horizontalalignment='right', verticalalignment='top')
            #g1.text(0.5, 0.5, 'matplotlib', horizontalalignment='center', verticalalignment='center')

            pct = pracovni_df_legenda.at[value,'pct_change']
            pct = "{0:.2f}".format(pct)
            g1.legend([],[],title='změna: '+ "\n" + str(pct) +"%", loc = 'center', frameon=False)#, fontsize=0.5)  loc=#upper right #best
            n = df_s_pocetem_hodnot["Pocet_True"].to_numpy()
            n2 = df_s_pocetem_hodnot["Pocet_False"].to_numpy()
            n = np.append(n, n2)
            aa = (n - 0) / (np.max(n) - 0) # tenhle řádek přepočítává hodnoty na interval mezi 0 a 1 
            #aa = (n - np.min(n)) / (np.max(n) - np.min(n))
            #aa = (n - 0) / (4030 - 0)

            counts_array = np.array_split(aa, 2)

            pocet1 = counts_array[0]
            pocet2 = counts_array[1]

            bar1_width = pocet1[count2]
            bar2_width = pocet2[count2]
                
            widthbars = [bar1_width, bar2_width] #udává šířku sloupců
            for bar, newwidth in zip(g1.patches, widthbars): #forcyklus nastavuje udanou šířku sloupcům
                x = bar.get_x()
                width = bar.get_width()
                centre = x + width/2.
                bar.set_x(centre - newwidth/2.)
                bar.set_width(newwidth)

             

            count += 1 #pro vykreslování do subplotů
            count2 +=1 #pro šířku sloupců

        #plt.tight_layout() 

        sns.despine(left=True) # přizpůsobuje desing grafu - odstraní ohraničení 
        #sns.despine(offset=10, trim=True)
        #fig.supylabel('Průměr hodnot indikátoru', fontsize = 12)
        #plt.subplots_adjust(left=None, bottom=0.076, right=0.276, top=0.966, wspace=None, hspace=None)
        plt.suptitle("Vliv '" + str(faktor) + "' na indikátory / " + str(research_area))
        #plt.figure(figsize=(1,4), dpi=400)
        plt.show()
        
        #plt.savefig('destination_path.png', format='png', dpi=500)


def vizualizace_zmena_hodnot_indikatoru_po_druhem_mereni(data1, data2):
    pracovni_df_pro_faktor = pd.DataFrame(columns = ["prvni_mereni","druhy_mereni"])
    df_rozdily_indikatoru = pd.DataFrame()
    
    indikatory_list = [
        "tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics",
        "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", 
        "score_altmetrics", "capture_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"] #"pole_TC"

    for ind in indikatory_list:
        pracovni_df_pro_faktor["prvni_mereni"] = data1[ind].copy()
        pracovni_df_pro_faktor["druhy_mereni"] = data2[ind].copy()
        # pracovni_df_pro_faktor.dropna(subset = ["prvni_mereni"], inplace=True) #odstraňujě NaN hodnoty
        # pracovni_df_pro_faktor.dropna(subset = ["druhy_mereni"], inplace=True) #odstraňujě NaN hodnoty


        pracovni_df_pro_faktor["prvni_mereni"] = pracovni_df_pro_faktor["prvni_mereni"].astype('float')
        pracovni_df_pro_faktor["druhy_mereni"] = pracovni_df_pro_faktor["druhy_mereni"].astype('float')


 #       pracovni_df_pro_faktor["rozdil_" + str(ind)] = pracovni_df_pro_faktor["druhy_mereni"] - pracovni_df_pro_faktor["prvni_mereni"]
        df_rozdily_indikatoru["rozdil_" + str(ind)] = pracovni_df_pro_faktor["druhy_mereni"] - pracovni_df_pro_faktor["prvni_mereni"]



    #df_rozdily_indikatoru.dropna(subset = ["rozdil_usage_plumx"], inplace=True)
    # print(pracovni_df_pro_faktor)
    #print(df_rozdily_indikatoru.head(20))
    # df_rozdily_indikatoru = df_rozdily_indikatoru.T
    #df_rozdily_indikatoru['poradi'] = df_rozdily_indikatoru.index
    for col in df_rozdily_indikatoru:
        df_rozdily_indikatoru[col] = df_rozdily_indikatoru[col].sort_values(ignore_index=True)#, ascending=False)
#    print(df_rozdily_indikatoru)
    df_melted = df_rozdily_indikatoru.melt(var_name='indikator')
    #df_melted = df_melted[df_melted.value != 0]
    df_melted.dropna(subset = ["value"], inplace=True)

    
    #df_melted["value"] = df_melted["value"].astype('int')
    #df_melted = df_melted.drop_duplicates(subset=['value'], keep='first')

    gr = df_melted.sort_values('value').groupby('indikator')
    df_melted['order_within_group'] = gr.cumcount()
    df_melted.sort_values(['indikator', 'order_within_group'], inplace=True)

    print(df_melted.head(40))



    # Create a grid : initialize it
    g = sns.FacetGrid(df_melted, col='indikator', col_wrap=5, sharex=False, sharey=False)

    # Add the line over the area with the plot function
    g = g.map(plt.plot, 'order_within_group', 'value')

    # Fill the area with fill_between
    g = g.map(plt.fill_between, 'order_within_group', 'value', alpha=0.2) #.set_titles("{col_name} country")

    # Control the title of each facet
    #g = g.set_titles("{col_name}")

    # Add a title for the whole plot
    plt.subplots_adjust(top=0.92)
    g = g.fig.suptitle('Rozdíl mezi prvním a druhým měřením')

    # Show the graph
    plt.show()




def pocty_poklesu_a_narustu(source_df, new_df, sledovany_indikator):
    """Funkce vypočítá pro sledovaný indikátor, v rámci kolika záznamů indikátor poklesl nebo narostl v druhém měření oproti prvnímu měření.
    Funkce se používá hlavně jako součástí další funkce - nespouští se manuálně. 
    """

    prepared_source_df = source_df[["doi", sledovany_indikator]]
    prepared_new_df = new_df[["doi", sledovany_indikator]]
    
    #merged_df = prepared_source_df.merge(prepared_new_df, indicator=True, how='outer')
    merged_df = prepared_source_df.merge(prepared_new_df,on='doi')
    merged_df.columns = ['doi', 'source_df', 'new_df']
    merged_df.dropna(subset = ["source_df"], inplace=True)
    merged_df.dropna(subset = ["new_df"], inplace=True)
    
    merged_df['zmena'] = np.where(merged_df['source_df'] == merged_df['new_df'], "stejne", np.where(merged_df['source_df'] >  merged_df['new_df'], "pokles", "narust"))  #vytvoří třetí sloupec s tím jestli byl zaznamenaný pokles nebo nárůst

    #print(merged_df)

    narust = merged_df.loc[merged_df["zmena"] == 'narust', 'zmena'].count()
    pokles = merged_df.loc[merged_df["zmena"] == 'pokles', 'zmena'].count()
    stejne = merged_df.loc[merged_df["zmena"] == 'stejne', 'zmena'].count()
    celkem = narust + pokles + stejne


    return narust, pokles, celkem
    



    # changed_rows_dataframe = changed_rows_df.drop('_merge', axis=1)
    # print(changed_rows_dataframe)

def priprav_df_pro_prirustku_a_ubytku(data1, data2):
    """"
    Funkce připravuje dataframe pro vizualizaci "klastrovaného stacked barplotu".
    Na vstup si bere originální dataframe a nově naměřený dataframe. Výstupem pak je připravený dataframe pro další funkci s názvem "plot_clustered_stacked"
    Tato funkce si volá "pocty_poklesu_a_narustu" k výpočtům poklesů a nárůstů. 
    Funkce se volá manuálně pro přípravů datafrajmů, a tyto připravené dataframy se poté musejí ručně vložit do funkce "plot_clustered_stacked"
    """
    df_pocty_zmen = pd.DataFrame(columns = ["Ind","celkem","narust","pokles"])

    indikatory = ["tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", 
            "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", 
            "score_altmetrics", "capture_plumx", "citation_plumx", "mentions_plumx", 
            "socialMedia_plumx", "usage_plumx"]
    
    for indikator in indikatory:
        narust, pokles, celkem = pocty_poklesu_a_narustu(data1, data2, indikator)
        df_pocty_zmen = df_pocty_zmen.append({'Ind' : indikator, 'celkem' : celkem, 'narust' : narust, 'pokles': pokles}, ignore_index = True)
    

    df_pocty_zmen["narust_v_pct"] = (df_pocty_zmen["narust"] / df_pocty_zmen["celkem"])*100
    df_pocty_zmen["pokles_v_pct"] = (df_pocty_zmen["pokles"] / df_pocty_zmen["celkem"])*100
    
    df_pocty_zmen.drop(["narust", "pokles", "celkem"], axis=1, inplace=True)
    df_pocty_zmen.set_index("Ind", inplace=True)
    print(df_pocty_zmen)

    # df_pocty_zmen.plot(kind='bar', stacked=True, color=['red', 'skyblue'])

    # plt.show()

    return df_pocty_zmen




def plot_clustered_stacked(dfall, labels=None, title="multiple stacked bar plot",  H="/", **kwargs):
    """Given a list of dataframes, with identical columns and index, create a clustered stacked bar plot. 
    labels is a list of the names of the dataframe, used for the legend
    title is a string for the title of the plot
    H is the hatch used for identification of the different dataframe
    
    Převzato a upraveno: https://stackoverflow.com/questions/22787209/how-to-have-clusters-of-stacked-bars-with-python-pandas
    """

    n_df = len(dfall)
    n_col = len(dfall[0].columns) 
    n_ind = len(dfall[0].index)
    axe = plt.subplot(111)

    for df in dfall : # for each data frame
        axe = df.plot(kind="bar",
                      linewidth=0,
                      stacked=True,
                      ax=axe,
                      legend=False,
                      grid=False,
                      **kwargs)  # make bar plots

    h,l = axe.get_legend_handles_labels() # get the handles we want to modify
    for i in range(0, n_df * n_col, n_col): # len(h) = n_col * n_df
        for j, pa in enumerate(h[i:i+n_col]):
            for rect in pa.patches: # for each index
                rect.set_x(rect.get_x() + 1 / float(n_df + 1) * i / float(n_col))
                rect.set_hatch(H * int(i / n_col)) #edited part     
                rect.set_width(1 / float(n_df + 1))

    axe.set_xticks((np.arange(0, 2 * n_ind, 2) + 1 / float(n_df + 1)) / 2.)
    axe.set_xticklabels(df.index, rotation = 0)
    axe.set_title(title)

    # Add invisible data to add another legend
    n=[]        
    for i in range(n_df):
        n.append(axe.bar(0, 0, color="gray", hatch=H * i))

    l1 = axe.legend(h[:n_col], l[:n_col], loc=[1.01, 0.5])
    if labels is not None:
        l2 = plt.legend(n, labels, loc=[1.01, 0.1]) 
    axe.add_artist(l1)

    plt.show()
    return axe



        

#porovnej_faktory(df, "mezinarodni_spoluprace", "usage_plumx", "t-test")

#========================================================================================
#faktory = ["typ_dokumentu","pole_LA","pocet_autoru", "interdisciplinarita", "open_access", "pocet_str", "flesch", "pocet_slov_AB", "pocet_slov_TI", "funding", "mezinarodni_spoluprace"]
#indikatory = ["pole_TC","tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", "score_altmetrics", "capture_plumx", "citation_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"]
#faktor = ["open_access", "mezinarodni_spoluprace", "interdisciplinarita", "funding"]
#zkouska_logaritmus(df, "typ_dokumentu", "mendeley_altmetrics")

###r = zjisti_vlivne_faktory(df, "tweetovani_altmetrics", "list_LA", False)

#zjisti_vlivne_faktory(df, "pole_TC", "typ_dokumentu", False)

#cyklus_vlivne_faktory(zjisti_vlivne_faktory, df, False)

#-------------------------------------------------------------

# for f in faktor:
#     porovnej_faktory(df, f, "usage_plumx", "mannwhitneyu")
#porovnej_faktory(df, "open_access", "mendeley_altmetrics", "t-test") 
#porovnej_faktory(df, "open_access", "tweetovani_altmetrics", "t-test")


df_social_sciences = df.loc[df['research_areas'] == 'Social Sciences']
df_technology = df.loc[df['research_areas'] == 'Technology']
df_Physical_sciencese = df.loc[df['research_areas'] == 'Physical Sciences']
df_Life_biomedicine = df.loc[df['research_areas'] == 'Life Sciences & Biomedicine']
df_Arts_Humanities = df.loc[df['research_areas'] == 'Arts & Humanities']

df02_social_sciences = df02.loc[df02['research_areas'] == 'Social Sciences']
df02_technology = df02.loc[df02['research_areas'] == 'Technology']
df02_Physical_sciencese = df02.loc[df02['research_areas'] == 'Physical Sciences']
df02_Life_biomedicine = df02.loc[df02['research_areas'] == 'Life Sciences & Biomedicine']
df02_Arts_Humanities = df02.loc[df02['research_areas'] == 'Arts & Humanities']

#faktory = ["interdisciplinarita", "open_access", "funding", "mezinarodni_spoluprace"]
faktory = ["open_access", "mezinarodni_spoluprace", "funding", "interdisciplinarita"]

#vizualizace_zmena_hodnot_indikatoru_po_druhem_mereni(df_social_sciences, df02_social_sciences)
#vizualizace_zmena_hodnot_indikatoru_po_druhem_mereni(df, df02)
#vizualizace_vliv_faktoru_na_hodnotu_indikatoru(df, "interdisciplinarita", "typ_2" , "Celkem")


#vizualizace_prirustku_a_ubytku(df, df02)


df_social = priprav_df_pro_prirustku_a_ubytku(df_social_sciences, df02_social_sciences)
df_tech = priprav_df_pro_prirustku_a_ubytku(df_technology, df02_technology)
df_physic = priprav_df_pro_prirustku_a_ubytku(df_Physical_sciencese, df02_Physical_sciencese)


# Then, just call :
plot_clustered_stacked([df_social, df_tech, df_physic],["df1", "df2", "df3"])


#get_different_rows(df_Life_biomedicine, df02_Life_biomedicine, "usage_plumx")

#print(df_social_sciences)

#zjisti_podil_dokumentu_v_agregatorech(df02, vizualizace=True)#, minimum_clanku=1) #"research_categories, list_DT") 
#zjisti_podil_dokumentu_v_agregatorech(df_technology, groupby="kategorie_WC", vizualizace=True, minimum_clanku=3)

#disciplinary_and_time_differences(data=df, indikator="pole_TC", groupby="kategorie_WC", median_or_mean="mean", minimum_clanku=1)

# indikator = "usage_plumx"
# faktor = "open_access"
#indikatory = ["pole_TC","tweetovani_altmetrics", "fb_altmetrics", "blogy_altmetrics", "zpravy_altmetrics", "reddit_altmetrics", "video_altmetrics", "mendeley_altmetrics", "score_altmetrics", "capture_plumx", "citation_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"]
#indikatory = ["score_altmetrics", "capture_plumx", "mentions_plumx", "socialMedia_plumx", "usage_plumx"]

#zjisti_korelaci(df_Life_biomedicine, "pole_TC", "usage_plumx",  typ_korelace="pearson", vizualizace=False, group_by="funding", zjisti_p_value=False)#, minimum_clanku = 80)#, top_hodnoty=5)

# zjisti_korelaci(df_social_sciences, "pole_TC", indikator,  typ_korelace="pearson", vizualizace=False, group_by=faktor, zjisti_p_value=True)#, minimum_clanku = 80, top_hodnoty=5)
# zjisti_korelaci(df_technology, "pole_TC", indikator,  typ_korelace="pearson", vizualizace=False, group_by=faktor, zjisti_p_value=True)#, minimum_clanku = 80, top_hodnoty=5)
# zjisti_korelaci(df_Physical_sciencese, "pole_TC", indikator,  typ_korelace="pearson", vizualizace=False, group_by=faktor, zjisti_p_value=True)#, minimum_clanku = 80, top_hodnoty=5)
# zjisti_korelaci(df_Life_biomedicine, "pole_TC", indikator,  typ_korelace="pearson", vizualizace=False, group_by=faktor, zjisti_p_value=True)#, minimum_clanku = 80, top_hodnoty=5)


#faktory = ["typ_dokumentu","pole_LA", "interdisciplinarita", "open_access", "funding", "mezinarodni_spoluprace", "kategorie_WC"]



#zjisti_korelaci(df, "pole_TC", "usage_plumx",  typ_korelace="pearson", vizualizace=False, minimum_clanku=1, group_by=faktor)

