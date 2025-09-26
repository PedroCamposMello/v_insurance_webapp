import pickle
import inflection
import pandas as pd
import numpy as np

class V_insurance( object ):
    def __init__( self ):
        self.home_path='' 
        self.enc_fe__policy_sales_channel   = pickle.load( open( self.home_path + 'resources/enc_fe__policy_sales_channel.pkl', 'rb') )
        self.enc_oe__age_profile            = pickle.load( open( self.home_path + 'resources/enc_oe__age_profile.pkl', 'rb') )
        self.enc_oe__vehicle_age            = pickle.load( open( self.home_path + 'resources/enc_oe__vehicle_age.pkl', 'rb') )
        self.enc_te__region_code            = pickle.load( open( self.home_path + 'resources/enc_te__region_code.pkl', 'rb') )
        self.scl_mms__age                   = pickle.load( open( self.home_path + 'resources/scl_mms__age.pkl', 'rb') )
        self.scl_mms__vintage               = pickle.load( open( self.home_path + 'resources/scl_mms__vintage.pkl', 'rb') )
        self.scl_rs__annual_premium         = pickle.load( open( self.home_path + 'resources/scl_rs__annual_premium.pkl', 'rb') )


    def apply_01( self, df ):
        df_01 = df.copy()

        # Renomear colunas
        cols_old = ['id', 'Gender', 'Age', 'Driving_License', 'Region_Code',
                    'Previously_Insured', 'Vehicle_Age', 'Vehicle_Damage', 'Annual_Premium',
                    'Policy_Sales_Channel', 'Vintage']

        snakecase = lambda x: inflection.underscore( x )

        cols_new = list( map( snakecase, cols_old ) )

        df_01.columns = cols_new

        return df_01
    

    def apply_02 (self, df):
        df_02 = df.copy()

        # Criando variáveis derivadas

        # age_profile
        conditions = [
                    (df_02['age'].between(20, 34)),
                    (df_02['age'].between(35, 49)),
                    (df_02['age'].between(50, 64)),
                    (df_02['age'] >= 65)
                    ]

        categorias = ['young', 'adult', 'middle-aged', 'elder']
        df_02['age_profile'] = np.select(conditions, categorias, default='out of range')

        # income_proxy
        conditions = [
                    (df_02['annual_premium'] <= 6000),
                    (df_02['annual_premium'].between(6001, 150000)),
                    (df_02['annual_premium'] > 150000)
                    ]

        categorias = ['0', '1', '2']
        df_02['income_proxy'] = np.select(conditions, categorias, default='out of range')
        df_02['income_proxy'] = df_02['income_proxy'].astype(int)

        return df_02


    def apply_03(self, df):
        df_03 = df.copy()

        # Normalização - Não há dados


        # Rescaling

        # annual_premium
        df_03['annual_premium'] = self.scl_rs__annual_premium.transform( df_03[['annual_premium']].values )

        # age
        df_03['age'] = self.scl_mms__age.transform( df_03[['age']].values )

        # vintage
        df_03['vintage'] = self.scl_mms__vintage.transform( df_03[['vintage']].values )


        # Encoding

        # id - Já está no formato de Label Encoding

        # gender - Label Encoding
        df_03['gender'] =df_03['gender'].apply(lambda x: 1 if x=='Male' else 0)

        # driving_license - Já está no formato de Label Encoding

        # region_code - Target Encoding
        df_03['region_code'] =df_03['region_code'].map(self.enc_te__region_code)

        # previously_insured - Já está no formato de Label Encoding

        # vehicle_age - Ordinal Encoding
        df_03['vehicle_age'] = df_03['vehicle_age'].map(self.enc_oe__vehicle_age)

        # vehicle_damage - Label Encoding
        df_03['vehicle_damage'] =df_03['vehicle_damage'].apply(lambda x: 1 if x=='Yes' else 0)

        # policy_sales_channel - Frenquency Encoding
        df_03['policy_sales_channel'] =df_03['policy_sales_channel'].map(self.enc_fe__policy_sales_channel)

        # age_profile - Ordinal Encoding
        df_03['age_profile'] = df_03['age_profile'].map(self.enc_oe__age_profile)

        # income_proxy - Já está no formato de Ordinal Encoding


        # Transformação de natureza - não há casos


        # Descartando colunas antigas - não necessário

        return df_03
    

    def apply_04 (self, df):
        df_04 = df.copy()

        # Selecionando colunas relevantes:

        cols_selected = ['id', # Colocada para manter a identificação dos registros, mas não será usada nos modelos
                        'annual_premium',
                        'region_code',
                        'age',
                        'vehicle_damage',
                        'policy_sales_channel',
                        'previously_insured',
                        'vehicle_age']

        df_04 = df_04[ cols_selected ]

        return df_04


    def get_prediction( self, model, original_data, df_prod ):
        # Gerando scores de interesse (sem a coluna de id)
        score = model.predict_proba(df_prod.drop(['id'], axis=1))

        # Anexando scores ao dataframe
        df_prod['score'] = score[:, 1]
        
        # Anexando scores ao dataframe original
        # Procurando scores em df_prod e aplicando em df_00 com base no id
        score_map = df_prod.set_index('id')['score']
        original_data['score'] = original_data['id'].map(score_map)

        # Preenchendo scores faltantes com zeros
        original_data['score'] = original_data['score'].fillna(0)

        return original_data.to_json( orient='records', date_format='iso' )