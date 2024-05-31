
import streamlit as st
import pandas as pd
import pydeck as pdk

custom_css = """
<style>
    @media screen and (max-width: 768px) {
        * {
        }
        .stButton button {
            width: 100%;
            margin-top: 10px;
        }
        .st-form .stButton button {
            width: 100%;
            margin-top: 10px;
        }
        .stMultiSelect *{
            padding: 0.1rem;
            font-size: 1.5rem;
        }
        .stMultiSelect [data-baseweb=select] span{
            padding: 0.1rem;
            font-size: 1.2rem;
        }
    }
</style>
"""

# カスタムCSSをStreamlitアプリに適用
st.markdown(custom_css, unsafe_allow_html=True)
class Hexagon:    # 地図の設定
    @staticmethod
    def drawing(dataframe):
        df = pd.DataFrame(dataframe)
        view = pdk.ViewState(
            longitude=139.6917,
            latitude=35.6895,
            zoom=4,
            pitch=60,
        )

        # レイヤーの設定
        layer = pdk.Layer(
            "HexagonLayer",
            data=df,
            get_position="[longitude, latitude]",
            radius=9000, # ヘクサゴンの半径
            elevation_scale=100, # 高さのスケール
           
            elevation_range=[0, df['合計'].max()/100],
            auto_highlight=True,
            extruded=True,
            pickable=True,
            coverage=0.9, # ヘクサゴンの重なり具合
            get_elevation_weight='合計', # カラムの値を高さの重み　
            elevation_aggregation='SUM',
        )

        # レイアウトの設定
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view,
            tooltip={
                "html": "{elevationValue}",
                "style": {"backgroundColor": "steelblue", "color": "white"}}
        )
        # Streamlitに表示
        st.pydeck_chart(r)

    @staticmethod
    def forms(dataframe):
        with st.form(key='forms'):
            def func(option):
                return option.replace('男','').replace('女','')
            df= pd.DataFrame(dataframe)

            
            left, right = st.columns([1, 1])
            
            with left :
                male_list = st.multiselect(
                    '男性',
                    [e for e in list(df.columns)[4:] if '男' in e ],
                    format_func= func, 
                    default= None
                )
                    
            with right:
                female_list = st.multiselect(
                    '女性',
                    [e for e in list(df.columns)[26:] if '女' in e ],
                    format_func= func, 
                    default= [e for e in list(df.columns)[30:32] if '女' in e] #default= [e for e in list(df.columns)[30:32] if '女' in e]
                )
            submit_btn = st.form_submit_button('更新')
        
        # 任意のカラムを抽出
        df_subset = df[male_list + female_list]

        # 新しいデータフレームを作成し、値を合計
        modified_df = pd.DataFrame()
        modified_df['市区町村'] = df['市区町村']
        modified_df['latitude'] = df['latitude']
        modified_df['longitude'] = df['longitude']
        modified_df['合計'] = df_subset.sum(axis=1)
        return submit_btn, modified_df

    # データの読み込み
    @st.cache
    def load_data():
        df = pd.read_csv('./data/d5.csv') #, nrows= 10
        return df
    
    def main():
        

        st.title('年齢別の人口分布の可視化')
        df= Hexagon.load_data()
        # レイアウト
        submit_btn, modified_df = Hexagon.forms(df)
        if submit_btn:
            Hexagon.drawing(modified_df)
        else:            
            Hexagon.drawing(modified_df)
       
        with st.expander("参照データ"):
            dic = {
            "統計名":"国勢調査 令和２年国勢調査 人口等基本集計　（主な内容：男女・年齢・配偶関係，世帯の構成，住居の状態，母子・父子世帯，国籍など）",
            "表番号":"2-7-1", 	
            "表題":"男女，年齢（5歳階級），国籍総数か日本人別人口－全国，都道府県，市区町村（2000年（平成12年）市区町村含む）",
            "URL":'https://www.e-stat.go.jp'
            }
            df = pd.DataFrame(dic, index=[""]).T
            st.table(df)
        
if __name__ == '__main__':
    Hexagon.main()