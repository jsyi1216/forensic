# -*- coding: utf-8 -*-
from django.test import TestCase
import numpy as np
import pandas as pd
import apps.tool.services as services
class Test_1(TestCase):
    
    def test_process1(self):

        print('***********process1 test start(Replace empty value with 0)***********')
        print('IDX5-X9의 값은 empty이므로 0으로 변경')
        sv = services.Preprocessor()

        preprocessings = [1]
        
        dataframe = pd.read_csv("static/test/test.CSV", sep=",", dtype='unicode')
        print('전처리 후 dataset')
        print(dataframe)
        dataframe = sv.preprocess(preprocessings, dataframe)
        print('전처리 후 dataset')
        print(dataframe)
        print('***********process1 test end***********')
        
    def test_process2(self):

        print('***********process2 test start(Remove any record with NULL value)***********')
        print('IDX0,IDX1,IDX5을 제외한 모든 ROW 삭제')

        sv = services.Preprocessor()

        preprocessings = [2]
        
        dataframe = pd.read_csv("static/test/test.CSV", sep=",", dtype='unicode')
        print('전처리 후 dataset')
        print(dataframe)
        dataframe = sv.preprocess(preprocessings, dataframe)
        print('전처리 후 dataset')
        print(dataframe)
        print('***********process2 test end***********')

    def test_process3(self):

        print('***********process3 test start(Remove duplicate data-IDX 기준으로 첫번째 항목을 제외한 다른 row 삭제)***********')
        print('IDX2가 3번째 행과 5번째 행에 존재하기 때문에 3번째 IDX2는 유지하고 5번째 행의 IDX2 row가 삭제')
        sv = services.Preprocessor()

        preprocessings = [3]
        
        dataframe = pd.read_csv("static/test/test.CSV", sep=",", dtype='unicode')
        print('전처리 후 dataset')
        print(dataframe)
        dataframe = sv.preprocess(preprocessings, dataframe)
        print('전처리 후 dataset')
        print(dataframe)
        print('***********process3 test end***********')

    def test_process4(self):

        print('***********process4 test start(Remove null characters)***********')
        print('IDX0~IDX3 앞뒤 공백 제거')
        sv = services.Preprocessor()

        preprocessings = [4]
        
        dataframe = pd.read_csv("static/test/test.CSV", sep=",", dtype='unicode')
        print('전처리 후 dataset')
        print(dataframe)
        dataframe = sv.preprocess(preprocessings, dataframe)
        print('전처리 후 dataset')
        print(dataframe)
        print('***********process4 test end***********')