# Importing the libraries
import streamlit as st
import pandas as pd
import numpy as np
from scipy.spatial.distance import hamming
import itertools #for paginator
import os
import base64
import random

st.set_page_config(layout="wide")

#for button background colour
m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(54, 180, 73);
    color: white;
}

[class^="css-qrbaxs effi0qh3"]{
    font-weight: bold;
    font-size: 120%;
}

#for side bar background color
.sidebar .sidebar-content {
    background-image: linear-gradient(##FFFDE6,##FFFDE6);
    color: white;
}

</style>""", unsafe_allow_html=True)


# a dictionary that converts Chinese main cat to Eng main cat
translate_main_cat = {
'飲料':'Beverages',
'零食':'Junk Food',
'急凍食品': 'Frozen',
'麵食':'Noodles',
'米/食油':'Rice/Oil',
'個人護理':'personal care',
'保健產品':'Health',
'護膚產品':'Skin Care'
}

# a dictionary that converts Eng main cat to CHinese main cat
inv_translate_main_cat = {v: k for k, v in translate_main_cat.items()}

#a dictionary that translates Eng sub cat to Chinese sub cat
sub_cat_to_chinese = {'Dairy':'奶製品', 'Water':'純水', 'No Sugar Tea':'無糖茶','Wellness Drink':'健康飲料',
                      'Sweeten Tea':'甜茶','Coffee':'咖啡','Juice':'果汁','Soft Drink':'汽水','Energy Drink':'能量飲品',
                      'Tea Bag':'茶包','Plant Milk':'植物奶','Soy Milk':'豆奶','Drink Mixes':'沖調飲品','Milk Tea':'奶茶',
                      'Sparkling Water':'有汽礦泉水','Yogurt Drink':'乳酪飲品','Snack':'零食', 'Dumplings':'餃子', 
                      'Poultry':'家禽','Soy-based':'豆類製品', 'Beef':'牛', 'Seafood':'海鮮', 'Dim Sum':'點心', 
                      'Curing Food':'醃製品', 'Pork':'豬','Meat Ball':'肉丸', 'Egg':'蛋', 'Steak':'牛排', 'Pork Chop':'豬排',
                      'Kimchi':'泡菜', 'Chicken Wings':'雞翼', 'Soup':'湯', 'Lamb':'羊', 'Ready-To-Cook Dishes':'加熱即食',
       'Vegetables':'蔬菜', 'Noodles':'麵食', 'Dessert':'甜品', 'Beverage':'飲料', 'Men':'男士保健', 'Powder':'奶粉/蛋白粉/營養補充粉',
       'Women':'女士保健', 'Tiredness':'對抗疲勞', 'Immunity':'提升免疫力', 'Slimming':'瘦身', 'Eye':'護眼', 'Respiratory':'呼吸系統',
       'Wellness':'養生', 'Digestive':'幫助消化', 'Liver':'護肝', 'Cardiovascular':'護心', 'Bone':'骨',
       'Brain':'醒腦', 'Beauty':'美容', 'Health Accessories':'防疫用品', 'Hair':'護髮', 'Mask':'口罩', 'Toner':'化妝水',
       'Face Cleanser':'面部清理', 'Make Up Remover':'卸妝用品', 'Lip':'唇膏', 'Face Cream':'面霜', 'Essence':'美容精華液',
       'Beauty Accessories':'美容用品', 'Acne':'暗瘡護理', 'Natural':'天然產品', 'Deep Cleaning':'深層護理', 'Sweets':'糖果/糖水',
       'Cookies':'餅乾', 'Popcorn':'爆谷', 'Cake':'蛋糕', 'nut/beans':'豆/堅果', 'Crackers':'脆片食物', 'Chocolate':'朱古力',
       'Chips':'薯片', 'Seaweed':'紫菜/海苔', 'snack bar/breakfast':'零食條/早餐', 'jerky':'肉乾', 'Others':'其它',
       'Sausage':'香腸', 'Dried Fruit':'水果乾', 'EggRoll':'蛋卷', 'Udon noodles':'烏冬',
       'Instant noodles':'即食麵', 'Rice/Cellophane noodles':'米粉/米線/冬粉', 'Ramen':"拉麵",
       'Pasta/Macaroni':'意粉/通粉', 'Cup noodles':'杯麵', 'Bean thread':'粉絲', 'Potato noodles':'薯仔麵',
       'Yimian':'伊麵', 'Instant rice/congee':'即食飯/粥', 'Konjac':'蒟蒻', 'personal hygiene':'個人衛生',
       'oral':'口腔護理', 'sanitary':'生理用品', 'facial care':'面部護理', 'sexual health':'兩性生活', 'others':"其它",
       'beauty':'美容', 'body':'盥洗用品', 'hair':'護髮', 'Rice':'米', 'Oil':'油'}





def paginator(label, items, items_per_page=40):
    """Lets the user paginate a set of items.
    Parameters
    ----------
    label : str
        The label to display over the pagination widget.
    items : Iterator[Any]
        The items to display in the paginator.
    items_per_page: int
        The number of items to display per page.
    on_sidebar: bool
        Whether to display the paginator widget on the sidebar.
        
    Returns
    -------
    Iterator[Tuple[int, Any]]
        An iterator over *only the items on that page*, including
        the item's index.

    """
    

        

    # Display a pagination selectbox in the specified location.
    items = list(items)
    n_pages = len(items)
    n_pages = (len(items) - 1) // items_per_page + 1
    page_format_func = lambda i: "第 %s 頁" % (i+1)
    # the 'right_column' is defned at line 362
    page_number = right_column.selectbox(label, range(n_pages), format_func=page_format_func)

    # Iterate over the items in the page to let the user display them.
    min_index = page_number * items_per_page
    max_index = min_index + items_per_page


    #display page number on the sidebar
    # the 'next_right_column' is defned at line 356
    next_right_column.write('共{}頁'.format(n_pages))
    st.subheader('商品編號 - 產品名稱')   

    return itertools.islice(enumerate(items), min_index, max_index)

#For image url
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

@st.cache(allow_output_mutation=True)
def get_img_with_href(local_img_path, target_url):
    img_format = os.path.splitext(local_img_path)[-1].replace('.', '')
    bin_str = get_base64_of_bin_file(local_img_path)
    html_code = f'''
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}" />
        </a>'''
    return html_code

@st.cache
def get_data():
    #import data
    df_item_ALL = pd.read_csv('RecommendationSystem/df_item_ALL.csv')

    # after trying to solve the 1d vector problem using the for loop,
    # it is found that there are duplicated product ID
    # therefore for products with duplicated rows, the df returns 2 rows
    # solution? drop the duplicated rows
    df_item_ALL.drop_duplicates(subset=['ProductID'],inplace=True)

    df_review_ALL_original = pd.read_csv('RecommendationSystem/df_review_ALL.csv')
    # clean the user name
    # commented, because that was done in the notebook
    # df_review_ALL_original['Username']= df_review_ALL_original['Username'].apply(lambda x:str(x).split('>')[-1])
    return df_item_ALL, df_review_ALL_original

df_item_ALL, df_review_ALL_original = get_data()


# lets write a function to compute k nearest neighbours of active user
# To Find the k nearest neighbours of active user first find the distance of active user to all other users
def nearestneighbours(df,product,K):
    # create a user df that contains all users except active user
    allProducts = pd.DataFrame(df.index)
    allProducts = allProducts[allProducts.ProductID!=product]
    # Add a column to this df which contains distance of active user to each user
    allProducts["distance"] =allProducts["ProductID"].apply(lambda x: hamming(df.loc[product],df.loc[x]))
    KnearestProducts = allProducts.sort_values(["distance"],ascending=True)["ProductID"][:K]
    return KnearestProducts


def df_creater(productid_input):
    main_cat=list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Main_Cat'])[0]
    temp_df=df_item_ALL[df_item_ALL['Main_Cat']==main_cat]
    temp_df_id=temp_df['ProductID']
    temp_df_user=pd.merge(temp_df_id,
                 df_review_ALL_original[['ProductID', 'Username', 'Rating']],
                 on='ProductID', 
                 how='left')
    #create pivot tables for finding the nearest neighbours
    temp_user_item_matrix=pd.pivot_table(temp_df_user, values='Rating',
                                    index=['ProductID'], columns=['Username'])
    return temp_user_item_matrix

# lets write a function to compute k nearest neighbours of active user
# To Find the k nearest neighbours of active user first find the distance of active user to all other users
def nearestneighbours_brand_cat(df,product,K):
    # create a user df that contains all users except active user
    allProducts = pd.DataFrame(df.index)
    allProducts = allProducts[allProducts.ProductID!=product]
    # Add a column to this df which contains distance of active user to each user
    allProducts["distance"] =allProducts["ProductID"].apply(lambda x: hamming(df.loc[product],df.loc[x]))
    KnearestProducts = allProducts.sort_values(["distance"],ascending=True)["ProductID"][:K]
    return KnearestProducts

def df_creatercat(productid_input):
    main_cat=list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Main_Cat'])[0]
    # create a new dataframe with productID as index column. For retrieveing the info of the recommended products.
    df_item_ALL_id_as_index = df_item_ALL.set_index('ProductID')
    #keep only ProductID, brand, main_cat, and sub_cat for recommendation
    # main_cat will be dropped later 
    df_item_brand_cat = df_item_ALL[['ProductID','Main_Cat','Brand','Sub_Cat']]
    #extract the data according to their main cat
    #for brand and sub_cat
    temp_df_brand_cat = df_item_brand_cat[df_item_ALL['Main_Cat']==main_cat][['ProductID','Brand','Sub_Cat']]
    #one-hot the brand and sub_cat
    temp_df_brand_cat = pd.concat([temp_df_brand_cat['ProductID'],pd.get_dummies(temp_df_brand_cat.Brand),pd.get_dummies(temp_df_brand_cat.Sub_Cat)],axis=1)
    #set ProductID as index column
    temp_df_brand_cat.set_index('ProductID',inplace=True)
    return temp_df_brand_cat

# Before input front page function

def df_create(x):
    if x == 'Personal Care':
        x='personal care'
    df = df_item_ALL[df_item_ALL['Main_Cat']==x]
    df['Image']=df['Image'].apply(lambda x: x if 'http' in str(x) else 'https'+str(x) )
    df.reset_index(drop=True,inplace=True)
    return df



def create_paginator(def_tab):
    product_df = df_create(translate_main_cat[def_tab])
    image_iterator = paginator('頁面', product_df['Image'])
    indices_on_page, images_on_page = map(list, zip(*image_iterator))
    captions = [str(product_df['ProductID'].iloc[i]) + '-' +str(product_df['Name'][i]) for i in indices_on_page]
    st.image(images_on_page, width=180, caption=captions)
    



#sidebar


st.sidebar.image('RecommendationSystem/hktvmall logo.png')
st.sidebar.title("商品推薦系統")
st.sidebar.write('請輸入商品編號，系統會找出相似商品')
productid_input=st.sidebar.text_input('', key = 'product_id_text', placeholder='在此輸入商品編號').upper()
#add spaces
st.sidebar.caption('')
st.sidebar.caption('')
st.sidebar.caption('')
st.sidebar.caption('')

#for clearing the productID in the text_input box
def clear_text():
    st.session_state['product_id_text'] = ''
    

   
#if a productID is entered
if productid_input: 

     #if no such productID
    if (productid_input not in list(df_item_ALL['ProductID'])):
        #create the back to main page button
        if st.sidebar.button('回到商品列表', on_click=clear_text, key = 'not_found_button'):
            st.experimental_rerun() 

        st.header('未有搜尋到 "{}" 相關的商品…'.format(productid_input)) 
        st.subheader('建議﹕ ')
        st.write('- 請確認所輸入的編號中沒有錯別字，或嘗試使用不同的搜尋編號')
        #st.write('- 請在以下目錄查找其他商品')
        st.write('\n')
        st.subheader('隨機產品推薦:')
        random_product=random.choices(list(df_item_ALL['ProductID']),k=4)
        cols=st.columns(4)
        for i in range(4):
            with cols[i]:
                st.image(list(df_item_ALL[df_item_ALL['ProductID']==random_product[i]]['Image'])[0])
                st.caption(list(df_item_ALL[df_item_ALL['ProductID']==random_product[i]]['Name'])[0])  
                st.caption(f'商品編號: {random_product[i]}')

    else: #user has entered a valid productID

        #create the back to main page button
        if st.sidebar.button('回到商品列表', on_click=clear_text, key = 'product_page_button'):
            st.experimental_rerun() 

        st.write(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Shop'])[0]) 
        st.title('{} - {}'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Brand'])[0],list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Name'])[0]))  
        
        
        st.write('商品類別: {} - {}'.format(inv_translate_main_cat[list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Main_Cat'])[0]],sub_cat_to_chinese[list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Sub_Cat'])[0]]))  
            
        cols=st.columns(3)
        with cols[0]:
        
            st.image(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Image'])[0])
            st.write(f'商品編號: {productid_input}') 
    
        with cols[1]:
            price_str='$ {}'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Price'])[0])
            st.markdown(f'<h1 style="color:#ff0d00;font-size:40px;">{price_str}</h1>', unsafe_allow_html=True)
            st.write('已售出  {}+'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Sales_Number'])[0]))  
            
            st.write('產地  {}'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['MadeIn'])[0]))  
            st.write('包裝規格  {}'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Package'])[0]))  
            st.write('商品簡介  {}'.format(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Description'])[0]))  
            
            #button that brings you to the HKTVMall product page
            url = list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['url'])[0]
            gif_html = get_img_with_href('RecommendationSystem/buy.png', url)
            st.markdown(gif_html, unsafe_allow_html=True)

            st.subheader('客戶評論 ({})  客戶評分 {} / 5 '.format(int(list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Review_total'])[0]),list(df_item_ALL[df_item_ALL['ProductID']==productid_input]['Review_avg'])[0]))  
        
        # recommendation part

        st.write('\n')
        st.header('購買此商品的顧客還選購了:')
        predicted_product=list(nearestneighbours(df_creater(productid_input),productid_input,4))
        cols=st.columns(4)
        for i in range(4):
            with cols[i]:
                st.image(list(df_item_ALL[df_item_ALL['ProductID']==predicted_product[i]]['Image'])[0])
                st.caption(str(predicted_product[i]) + '-' + str(list(df_item_ALL[df_item_ALL['ProductID']==predicted_product[i]]['Name'])[0]))  
                
    
        st.write('\n')
        st.header('您可能會對以下商品感興趣:')
        predicted_product=list(nearestneighbours_brand_cat(df_creatercat(productid_input),productid_input,4))
        cols=st.columns(4)
        for i in range(4):
            with cols[i]:
                st.image(list(df_item_ALL[df_item_ALL['ProductID']==predicted_product[i]]['Image'])[0])
                st.caption(str(predicted_product[i]) + '-' + str(list(df_item_ALL[df_item_ALL['ProductID']==predicted_product[i]]['Name'])[0]))
                

else: #inothing in the input text bar
    left_column, right_column = st.columns(2) #for tab and page selector
    tab = left_column.selectbox('請選擇商品類別 ',('飲料', '零食', '急凍食品','麵食', '米/食油',
        '個人護理', '保健產品', '護膚產品'))

    #for page number
    next_left_column, next_right_column = st.columns(2)
    
    create_paginator(tab)

     
