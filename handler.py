import os
import pickle

import pandas                   as pd

from flask                      import Flask, request, Response
from custom_packs.v_insurance   import V_insurance

# loading model
model = pickle.load( open( 'resources/model_xgb.pkl', 'rb') )

# initialize API
app = Flask( __name__ )

@app.route( '/vinsurance/predict', methods=['POST'] )
def V_insurance_predict():
    test_json = request.get_json()
   
    if test_json: # there is data
        if isinstance( test_json, dict ): # unique example
            test_raw = pd.DataFrame( test_json, index=[0] )
            
        else: # multiple example
            test_raw = pd.DataFrame( test_json, columns=test_json[0].keys() )
            
        # Instantiate Rossmann class
        pipeline = V_insurance()
        
        # data wrangling
        df = pipeline.apply_01(test_raw)
        df = pipeline.apply_02(df)
        df = pipeline.apply_03(df)
        df = pipeline.apply_04(df)

        # prediction
        df_response = pipeline.get_prediction( model, test_raw, df )

        return df_response
          
    else:
        return Response( '{}', status=200, mimetype='application/json' )

if __name__ == '__main__':
    port = os.environ.get( 'PORT', 5000 )
    app.run( host='0.0.0.0', port=port )