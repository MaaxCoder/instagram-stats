import json
import pandas as pd
import streamlit as st
from datetime import datetime
import os

dirs = []
for file in sorted(os.listdir(".")):
    d = os.path.join(".", file)
    if os.path.isdir(d):
        dirs.append(d)

st.set_page_config(
    page_title="Instagram stats",
    page_icon="Instagram_icon.png")

st.image("Instagram_icon.png", width=100)
st.title("Instagram streamlit statisitcs")
st.divider()
st.header("**:orange[Choisir le dossier]**")
month_actual = datetime.today().strftime('%Y-%m')
option = st.selectbox("Choisissez un dossier", dirs, len(dirs)-1)
st.divider()
st.header("Abonnés et abonnements")
st.subheader("Statistiques")
dosser_actuel = option

# Lire le fichier json (en objet phython)
def lire_fichier_json(nom_fichier):
    with open(f"{dosser_actuel}/{nom_fichier}", 'r') as fichier:
        contenu = json.load(fichier)
    return contenu

# Dans une boucle pour chaque follower : transofrmer le timestamp en Mois/Année
# Transformer tout ca en dataframe

def to_dataframe(object):
    noms = []
    times = []
    for f in object:
        nom = f["string_list_data"][0]["value"]
        ts = f["string_list_data"][0]["timestamp"]
        noms.append(nom)
        times.append(ts)
    df = pd.DataFrame({
        "timestamp" : times,
        "followers": noms
    })
    return df

def to_dataframe_1(object):
    noms = []
    times = []
    for f in object["relationships_following"]:
        nom = f["string_list_data"][0]["value"]
        ts = f["string_list_data"][0]["timestamp"]
        noms.append(nom)
        times.append(ts)
    df = pd.DataFrame({
        "timestamp" : times,
        "followers": noms
    })
    return df

# Faire un objet qui compte le nombrede mois/année

def groupby_month(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df_grouped = df_grouped = df.groupby(pd.Grouper(key='timestamp', freq='ME')).agg({'followers': lambda x: x.tolist()})
    df_grouped.index = df_grouped.index.strftime('%Y-%m')
    df_grouped["followers_count"] = df_grouped['followers'].apply(lambda x: len(x))
    return df_grouped

def groupby_month_1(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df_grouped = df_grouped = df.groupby(pd.Grouper(key='timestamp', freq='ME')).agg({'followers': lambda x: x.tolist()})
    df_grouped.index = df_grouped.index.strftime('%Y-%m')
    df_grouped["followers_count"] = df_grouped['followers'].apply(lambda x: len(x))
    df_grouped["followers_count"] = -df_grouped["followers_count"]
    return df_grouped

# Mettre ça dans streamlit

#def to_st(df_grouped):
    # st.bar_chart(data=df_grouped, y="followers_count")
    st.dataframe(data=df_grouped["followers"], width=2000)

# Fusion

def fusion(df_1, df_2):
    merge = df_1.merge(df_2, left_index=True, right_index=True, how='outer')
    merge.rename(columns={"followers_count_x": "Abonnés", "followers_count_y": "Abonnements"}, inplace=True)
    merge_columns = merge[['Abonnés', 'Abonnements']]
    st.bar_chart(merge_columns)
    st.subheader("Chercher")
    col1, col2 = st.columns(2)
    option = col1.selectbox("Choisissez un type:", ["Abonnés", "Abonnements"])
    if (option=="Abonnés"):
        option2 = col2.selectbox("Choisissez une date :",reversed(df_1[~df_1.followers.isin([[]])].index.tolist()))
        st.multiselect("La liste correpondante :",df_1.loc[[option2]].followers.values[0],df_1.loc[[option2]].followers.values[0], disabled=True)
    if (option=="Abonnements"):
        option2 = col2.selectbox("Choisissez une date :",reversed(df_2[~df_2.followers.isin([[]])].index.tolist()))
        st.multiselect("La liste correpondante :",df_2.loc[[option2]].followers.values[0],df_2.loc[[option2]].followers.values[0], disabled=True)

# State globale
def state_globale(df, df_1, df_grouped, df_grouped_1):
    col1, col2 = st.columns(2)
    if month_actual == df_grouped.iloc[-1].name:
        col1.metric("Abonnés", df.shape[0], f"{int(df_grouped.iloc[-1].followers_count)} last month")
    else:
        col1.metric("Abonnés", df.shape[0], f"0 last month")
    if month_actual == df_grouped_1.iloc[-1].name:
        col2.metric("Abonnements", df_1.shape[0], f"{~int(df_grouped_1.iloc[-1].followers_count)} last month")
    else:
        col2.metric("Abonnements", df_1.shape[0], f"0 last month")

# tableau des putes

def insta_type_follower(df_follower, df_following):
    communs = df_follower.followers[df_follower.followers.isin(df_following.followers)].reset_index(drop=True)
    pigeons = df_follower.followers[~df_follower.followers.isin(df_following.followers)].reset_index(drop=True)
    star = df_following.followers[~df_following.followers.isin(df_follower.followers)].reset_index(drop=True)
    
    col1, col2, col3 = st.columns(3)

    df_star = df_1[df_1.followers.isin(star)]
    df_star_grouped = df_star.groupby(pd.Grouper(key='timestamp', freq='ME')).agg({'followers': lambda x: x.tolist()})
    df_star_grouped.index = df_star_grouped.index.strftime('%Y-%m')
    df_star_grouped["followers_count"] = df_star_grouped['followers'].apply(lambda x: len(x))
    if month_actual == df_star_grouped.iloc[-1].name:
        col3.metric("Star", star.size, int(df_star_grouped.iloc[-1].followers_count))
    else:
        col3.metric("Star", star.size, 0)

    df_pigeons = df[df.followers.isin(pigeons)]
    df_pigeons_grouped = df_pigeons.groupby(pd.Grouper(key='timestamp', freq='ME')).agg({'followers': lambda x: x.tolist()})
    df_pigeons_grouped.index = df_pigeons_grouped.index.strftime('%Y-%m')
    df_pigeons_grouped["followers_count"] = df_pigeons_grouped['followers'].apply(lambda x: len(x))
    if month_actual == df_pigeons_grouped.iloc[-1].name:
        col1.metric("Pigeons", pigeons.size, int(df_pigeons_grouped.iloc[-1].followers_count))
    else:
        col1.metric("Pigeons", pigeons.size, 0)

    df_communs = df[df.followers.isin(communs)]
    df_communs_grouped = df_communs.groupby(pd.Grouper(key='timestamp', freq='ME')).agg({'followers': lambda x: x.tolist()})
    df_communs_grouped.index = df_communs_grouped.index.strftime('%Y-%m')
    df_communs_grouped["followers_count"] = df_communs_grouped['followers'].apply(lambda x: len(x))
    if month_actual == df_communs_grouped.iloc[-1].name:
        col2.metric("Communs", communs.size, int(df_communs_grouped.iloc[-1].followers_count))
    else:
        col2.metric("Communs", communs.size, 0)

    df_merge_temp = df_star_grouped.merge(df_communs_grouped, left_index=True, right_index=True, how='outer')
    df_merge = df_merge_temp.merge(df_pigeons_grouped, left_index=True, right_index=True, how='outer')
    df_merge.rename(columns={"followers_count_x": "Stars", "followers_count_y": "Communs", "followers_count": "Pigeons"}, inplace=True)
    df_merge_columns = df_merge[["Stars", "Communs", "Pigeons"]]
    
    st.bar_chart(df_merge_columns)
    st.subheader("Recherche")

    st.markdown("**:red[Star]** (personne qui ne te follow pas mais que tu follow)")
    st.markdown(" **:red[Communs]** (follow back)")
    st.markdown("**:red[Pigeons]**(personne que tu ne follow pas mais qui te follow)")
    col4, col5 = st.columns(2)
    
    option = col4.selectbox("Choisissez un type:", ["Pigeons","Communs","Star"],index=2)
    if (option=="Star"):
        option2 = col5.selectbox("Choisissez une date :",["Total"] + df_star_grouped[~df_star_grouped.followers.isin([[]])].index.tolist())
        if option2 != "Total":
            st.multiselect("La liste correpondante :",df_star_grouped.loc[[option2]].followers.values[0],df_star_grouped.loc[[option2]].followers.values[0], disabled=True)
        else:
            liste = []
            for element in df_star_grouped.followers.tolist():
                liste = liste + element
            st.multiselect("La liste correpondante :",liste, liste, disabled=True)
    if (option=="Communs"):
        option2 = col5.selectbox("Choisissez une date :",["Total"] + df_communs_grouped[~df_communs_grouped.followers.isin([[]])].index.tolist())
        if option2 != "Total":
            st.multiselect("La liste correpondante :",df_communs_grouped.loc[[option2]].followers.values[0],df_communs_grouped.loc[[option2]].followers.values[0], disabled=True)
        else:
            liste = []
            for element in df_communs_grouped.followers.tolist():
                liste = liste + element
            st.multiselect("La liste correpondante :",liste, liste, disabled=True)
    if (option=="Pigeons"):
        option2 = col5.selectbox("Choisissez une date :",["Total"] + df_pigeons_grouped[~df_pigeons_grouped.followers.isin([[]])].index.tolist())
        if option2 != "Total":
            st.multiselect("La liste correpondante :",df_pigeons_grouped.loc[[option2]].followers.values[0],df_pigeons_grouped.loc[[option2]].followers.values[0], disabled=True)
        else:
            liste = []
            for element in df_pigeons_grouped.followers.tolist():
                liste = liste + element
            st.multiselect("La liste correpondante :",liste, liste, disabled=True)
    st.divider()


#def show_ads(ads_object):
#    st.header("Tags")
#    interests = []
#    for i in ads_object["inferred_data_ig_interest"]:
#        interest = i["string_map_data"]["Centre dâ\x80\x99intÃ©rÃªt"]["value"]
#        interests.append(interest)
#    if st.button("Afficher tous les tags"):
#        with st.expander("Voir les tags", expanded=True):
#           st.multiselect("Tags :",interests,interests,disabled=True)
#    else:
#        st.multiselect("Les premiers tags :",interests[0:10]+["...", "...", "...", "...", "..."],interests[0:10]+["...", "...", "...", "...", "..."],disabled=True)


# Code fonction

followers_file = lire_fichier_json("followers_1.json")
df = to_dataframe(followers_file)
df_grouped = groupby_month(df)

following_file = lire_fichier_json("following.json")
df_1 = to_dataframe_1(following_file)
df_grouped_1 = groupby_month_1(df_1)

state_globale(df, df_1, df_grouped, df_grouped_1)
df_fusion = fusion(df_grouped, df_grouped_1)
st.divider()
st.header("PCS : Pgieons, communs et star")
st.subheader("Graphique")
insta_type_follower(df, df_1)

#ads_object = lire_fichier_json("ads_interests.json")
#show_ads(ads_object)
