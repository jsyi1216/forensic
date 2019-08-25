import sys, os, csv, json
import numpy as np
import pandas as pd
import apps.mongo.services as mongo
import re
from django.conf import settings
from shutil import copyfile
from bson.objectid import ObjectId
from keras.models import model_from_json
from matplotlib import pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Constants
ARCHITECTUREPATH = "static/resources/learning models/architecture_"
WEIGHTPATH = "static/resources/learning models/weights_"
INPUTPATH = "static/resources/dataset/input/"
REFINEDPATH = "static/resources/dataset/refined/"
CHARTPATH = "static/resources/chart/"
CLIENT_STORAGEURL = settings.__getattr__('CLIENT_STORAGEURL')

class AI():
    def __init__(self):
        self.jsonEncoder = JSONEncoder()
        self.preprocessor = Preprocessor()
        self.validatorFactory = ValidatorFactory()

    def predict(self, data):
        records = data.get("inputs")
        preprocessings = data.get("preprocessings")
        results = []
        
        # Database setting
        db = mongo.Mongo().getDatabase('tools')

        # Predict
        for record in records:
            # Get model information
            modelId = record.get('model').get('id')
            modelObj = db.model.find_one({"_id": ObjectId(modelId)})
            record['model'] = json.loads(self.jsonEncoder.encode(modelObj))

            if modelObj.get('klass') == 'GC':
                result = self.predictGC(record, preprocessings)
                results.append(result)
            elif modelObj.get('klass') == 'MS':
                pass
            elif modelObj.get('klass') == 'Formulation':
                results = results+self.predictFormulation(record, preprocessings)

        return results

    def loadModel(self, modelId):
        # Load the architecture of model
        json_file = open(ARCHITECTUREPATH+modelId+".json","r")
        model_json = json_file.read()
        json_file.close()
        model = model_from_json(model_json)
        
        # Load the weights
        model.load_weights(WEIGHTPATH+modelId+".h5")

        return model

    def createGCChart(self, dataframe, fileName, path):
        START = 0
        END = 60
        INTERVAL = 0.1

        abundance = np.delete(dataframe.values[0], [0])
        data = pd.DataFrame({'time': np.arange(START,END,INTERVAL), 'abundance': abundance})

        # plot
        plt.figure(figsize=(15, 6))
        plt.ylabel('Abundance')
        plt.xlabel('Retention time(min)')
        plt.ticklabel_format(style='plain')
        plt.plot('time', 'abundance', data=data, color='black', linewidth=0.5)

        plt.savefig(path+fileName+".png")

    def predictGC(self, record, preprocessings):
        modelId = record.get('model').get('_id')
        name = record.get('name')
        guid = record.get('guid')
        ext = record.get('format')
        path = CLIENT_STORAGEURL+record.get('path')
        refinedName = name+"_refined"

        # Copy the file to the input folder
        if not os.path.exists(INPUTPATH+guid+"."+ext):
            open(INPUTPATH+guid+"."+ext, 'w').close()

        copyfile(path+"/"+guid+"."+ext, INPUTPATH+guid+"."+ext)

        # Validation
        dfForValid = pd.read_csv(INPUTPATH+guid+"."+ext, sep=',', header=0, engine='python', encoding='euc-kr')
        validator = self.validatorFactory.create_validator('GC')
        if validator.isValid(dfForValid, record.get('model')) is False:
            result = {
                "inputFile": record,
                "chart": "",
                "error": "ERR002"
            }

            return result

        # Transform GC data to Dataset
        self.preprocessor.gc2dataset(guid, name, ext, path, INPUTPATH, 0, 60, 0.1)

        # Load input data
        dataframe = pd.read_csv(INPUTPATH+guid+"."+ext, sep=',', header=0, engine='python', encoding='euc-kr')

        # Create a chart
        self.createGCChart(dataframe, name, CHARTPATH)

        # load the moadl
        model = self.loadModel(modelId)

        # Preprocessing
        dataframe = self.preprocessor.preprocess(preprocessings, dataframe)

        # Save refined dataframe
        dataframe.to_csv(REFINEDPATH+refinedName+"."+ext, mode = 'w', index=False, encoding='euc-kr')

        # Manipulate data
        del dataframe["IDX"]
        x_data = dataframe.values
        x_data = x_data[:, :, np.newaxis][:, :, np.newaxis]

        # Predict
        try:
            pred = int(model.predict_classes(x_data)[0])
            err = False
        except:
            pred = ''
            err = 'ERR001'

        result = {
            "inputFile": record,
            "refinedFile": {
                "name": refinedName,
                "path": REFINEDPATH,
                "format": ext
            },
            "predictedValue": pred,
            "chart": CHARTPATH+name+".png",
            "error": err
        }

        return result

    def predictFormulation(self, record, preprocessings):        
        modelId = record.get('model').get('_id')
        name = record.get('name')
        guid = record.get('guid')
        ext = record.get('format')
        path = CLIENT_STORAGEURL+record.get('path')
        results = []

        # Copy the file to the input folder
        if not os.path.exists(INPUTPATH+guid+"."+ext):
            open(INPUTPATH+guid+"."+ext, 'w').close()

        copyfile(path+"/"+guid+"."+ext, INPUTPATH+guid+"."+ext)

        # Load input data
        dataframe = pd.read_csv(INPUTPATH+guid+"."+ext, sep=',', header=0, keep_default_na=False, engine='python', encoding='euc-kr')

        # Validation
        validator = self.validatorFactory.create_validator('Formulation')
        if validator.isValid(dataframe, record.get('model')) is False:
            result = {
                "inputFile": record,
                "chart": "",
                "error": "ERR002"
            }
            results.append(result)

            return results

        # load the moadl
        model = self.loadModel(modelId)

        # Preprocessing
        dataframe = self.preprocessor.preprocess(preprocessings, dataframe)
        # Check duplicate indexes
        idxs = list(dataframe.iloc[:,0].values)
        dups = set([x for x in idxs if idxs.count(x) > 1])

        for i in range(len(dups)):
            n = dups.pop()
            temps = dataframe.loc[dataframe['IDX']==n]['IDX']
            indexes = temps.index
            cnt=0

            for i, t in enumerate(temps):
                cnt+=1
                t=t+'_'+str(cnt)
                dataframe.loc[indexes[i],'IDX'] = t

        for i, r in enumerate(dataframe['IDX']):
            df = dataframe.iloc[i:i+1]
            # Save refined dataframe
            if len(df["IDX"].values) > 0:
                refinedName = name+"_"+df["IDX"].values[0]+"_refined"
                refinedFile = REFINEDPATH+refinedName+"."+ext
                df.to_csv(refinedFile, mode = 'w', index=False, encoding='euc-kr')

                refinedObj = {
                    "name": refinedName,
                    "path": REFINEDPATH,
                    "format": ext
                }
            else:
                refinedObj = {
                    "name": '',
                    "path": '',
                    "format": ''
                }

            # Manipulate data
            del df["IDX"]

            # Predict
            if df.empty is not True:
                try:
                    pred = int(model.predict(df)[0][0])
                    err = False
                except:
                    pred = ''
                    err = 'ERR001'

                result = {
                    "inputFile": record,
                    "refinedFile": refinedObj,
                    "predictedValue": pred,
                    "chart": "",
                    "error": err
                }
                results.append(result)

        return results

class Preprocessor():
    def preprocess(self, preprocessing, dataframe):
        for p in preprocessing:
            dataframe = self.__getattribute__("preprocess_"+str(p))(dataframe)

        return dataframe

    # Replace N/A, NaN, Null, empty value with 0
    def preprocess_1(self, dataframe):
        # 앞/뒤 공백 문자 제거
        dataframe = dataframe.replace('(^\s+|\s+$)', '', regex=True)
        dataframe = self.replaceArray(dataframe, ['Na','NULL','Null','null','NaN','NA','N/A',''], np.nan)

        dataframe = dataframe.fillna('0')

        return dataframe

    # Remove any records with N/A, NaN, Null, empty value
    def preprocess_2(self, dataframe):
        dataframe = dataframe.replace('(^\s+|\s+$)', '', regex=True)
        dataframe = self.replaceArray(dataframe, ['Na','NULL','Null','null','NaN','NA','N/A',''], np.nan)

        # row제거(0=row제거,1=column제거)
        dataframe = dataframe.dropna(0)

        return dataframe

    # Remove duplicate data
    def preprocess_3(self, dataframe):
        dataframe = dataframe.drop_duplicates(["IDX"], keep="first")

        return dataframe
    
    # Remove blank characters
    def preprocess_4(self, dataframe):
        dataframe = dataframe.replace('(^\s+|\s+$)', '',regex=True)
        
        return dataframe

    def gc2dataset(self, guid, name, ext, path, inputPath, start, end, interval):
        inputFile = open(inputPath+guid+"."+ext, 'w', encoding="euc-kr")

        # set columns
        cols=[]
        cols.append('IDX')
        for col in range(int(end/interval)):
            cols.append('X'+str(col))

        # set records
        rt=[]
        dic={}
        j=0
        rec=[]

        rec.append(name)

        with open(path+"/"+guid+"."+ext, newline='', encoding="euc-kr") as gcFile:
            reader = csv.reader(gcFile)
            for idx, row in enumerate(reader):
                if idx > 2:
                    rt.append(row[0])
                    dic[row[0]]=row[1]

        for i in self.getRange(start, end, interval):
            i = round(i, 2)
            temp=[]
            if j < len(rt) and float(rt[j]) >= i and float(rt[j]) < i+interval:
                for k, c in enumerate(rt):
                    if float(rt[k]) >= i and float(rt[k]) < i+interval:
                        temp.append(float(dic[c]))
                        j=j+1
            if len(temp)>0:
                s=0
                for k in temp:
                    s = s + float(k)
                rec.append(max(temp))
            else:
                rec.append(0)

        # write the dataset file
        writer = csv.writer(inputFile)

        writer.writerow(cols)

        writer.writerow(rec)

        # close files
        gcFile.close()
        inputFile.close()

    def getRange(self, start, end, step):
        while start <= end:
            yield start
            start += step
    
    def replaceArray(self, dataframe, arr, val):
        for i in arr:
            dataframe = dataframe.replace(i,val)
        return dataframe

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class ValidatorFactory():
    def __init__(self):
        pass

    def create_validator(self, vType):
        if vType is 'GC':
            validator = Validator_GC()
        elif vType is 'Formulation':
            validator = Validator_Formulation()
        else:
            validator = None

        return validator

class Validator_GC():
    def isValid(self, df, model):
        if self.isValid_1(df, model) is False:
            return False
        elif self.isValid_2(df, model) is False:
            return False
        elif self.isValid_3(df) is False:
            return False
        elif self.isValid_4(df) is False:
            return False 
        elif self.isValid_5(df) is False:
            return False        
        else:
            return True

    def isValid_1(self, dataframe, model):
        tPath = model.get('dataset').get('template').get('path')
        template = pd.read_csv(tPath)
        tCols = np.array(template.columns, dtype=object)
        iCols = np.array(dataframe.columns, dtype=object)

        valid = (len(tCols) == len(iCols))

        return valid

    def isValid_2(self, dataframe, model):
        tPath = model.get('dataset').get('template').get('path')
        template = pd.read_csv(tPath)
        validArr = (template.columns == dataframe.columns)
        
        valid = False not in validArr

        return valid

    def isValid_3(self, dataframe):
        time = dataframe.iloc[2:,0]
        abundance = dataframe.iloc[2:,1]

        try:
            time.astype('float64')
            abundance.astype('float64')
            valid = True
        except:
            valid = False
        
        return valid

    def isValid_4(self, dataframe):
        time = dataframe.iloc[2:,0]
        abundance = dataframe.iloc[2:,1]
        isBlank1 = all(not i == np.nan for i in list(dataframe.iloc[2:,2]))
        isBlank2 = all(not i == np.nan for i in list(dataframe.iloc[2:,3]))
        isBlank3 = all(not i == np.nan for i in list(dataframe.iloc[2:,4]))

        if np.nan not in list(time) and np.nan not in list(abundance) and isBlank1 and isBlank2 and isBlank3:
            valid = True
        else:
            valid = False

        return valid

    def isValid_5(self, dataframe):
        time = dataframe.iloc[2:,0].astype('float64')

        if max(time) <= 60:
            valid = True
        else:
            valid = False

        return valid

class Validator_Formulation():
    def isValid(self, dataframe, model):
        if self.isValid_1(dataframe, model) is False:
            return False
        elif self.isValid_2(dataframe, model) is False:
            return False
        elif self.isValid_3(dataframe, model) is False:
            return False
        elif self.isValid_4(dataframe) is False:
            return False
        elif self.isValid_5(dataframe) is False:
            return False
        else:
            return True

    def isValid_1(self, dataframe, model):
        tPath = model.get('dataset').get('template').get('path')
        template = pd.read_csv(tPath)
        tCols = np.array(template.columns, dtype=object)
        iCols = np.array(dataframe.columns, dtype=object)

        valid = (len(tCols) == len(iCols))

        return valid

    def isValid_2(self, dataframe, model):
        tPath = model.get('dataset').get('template').get('path')
        template = pd.read_csv(tPath)
        validArr = (template.columns == dataframe.columns)
        
        valid = False not in validArr

        return valid

    def isValid_3(self, dataframe, model):
        tPath = model.get('dataset').get('template').get('path')
        template = pd.read_csv(tPath)
        tCols = np.array(template.columns, dtype=object)
        iCols = np.array(dataframe.columns, dtype=object)
        
        valid = False not in np.equal(tCols, iCols)

        return valid

    def isValid_4(self, dataframe):
        preprocessor = Preprocessor()
        dataframe = dataframe.replace('(^\s+|\s+$)', '', regex=True)
        dataframe = preprocessor.replaceArray(dataframe, ['Na','NULL','Null','null','NaN','NA','N/A',''], 0)
        del dataframe['IDX']
        try:
            dataframe.astype('float64')
        except:
            valid = False
        else:
            valid = True       

        return valid

    def isValid_5(self, dataframe):
        valid = True

        for row in dataframe['IDX']:
            if not re.match(r'^\w+', row):
                valid = False

        return valid
