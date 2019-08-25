from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework_mongoengine import viewsets
from rest_framework.response import Response
from apps.tool.models import Model, Predict
from apps.tool.serializers import ModelSerializer, PredictSerializer
from apps.tool.services import AI

class PredictViewSet(viewsets.ModelViewSet):
    serializer_class = PredictSerializer
    http_method_names = ['post']

    @csrf_exempt
    def create(self, request):
        data = JSONParser().parse(request)
        serializer = PredictSerializer(data=data)
        
         = AI()

        if serializer.is_valid():
            predictions = ai.predict(data)
            results = self.manipulatePredictions(predictions)
            serializer.save()
            return JsonResponse({'predictions': results}, status=201)
        return JsonResponse(serializer.errors, status=400)

    def manipulatePredictions(self, predictions):
        preds = []
        for pred in predictions:
            if pred.get('error') is False:
                accuracy = pred.get("inputFile").get("model").get("accuracy")
                accuracy = "학습 데이터(Training data)<br>"+self.dictToStr(accuracy['training'])+"<br>테스트 데이터(Test data)<br>"+self.dictToStr(accuracy['test'])
                preds.append({
                    "inputFileName": pred.get("inputFile").get("name"),
                    "inputFileId": pred.get("inputFile").get("id"),
                    "inputFilePath": pred.get("inputFile").get("path"),
                    "inputFileFormat": pred.get("inputFile").get("format"),
                    "refinedFileName": pred.get("refinedFile").get("name"),
                    "refinedFilePath": pred.get("refinedFile").get("path"),
                    "refinedFileFormat": pred.get("refinedFile").get("format"),
                    "modelName": pred.get("inputFile").get("model").get("name"),
                    "modelGroup": pred.get("inputFile").get("model").get("group"),
                    "modelAccuracy":  accuracy,
                    "predictedValue": pred.get("predictedValue"),
                    "chart": pred.get("chart"),
                    "error": pred.get("error")
                })
            elif pred.get('error') is 'ERR001':
                accuracy = pred.get("inputFile").get("model").get("accuracy")
                accuracy = "학습 데이터(Training data)<br>"+self.dictToStr(accuracy['training'])+"<br>테스트 데이터(Test data)<br>"+self.dictToStr(accuracy['test'])
                preds.append({
                    "inputFileName": pred.get("inputFile").get("name"),
                    "inputFileId": pred.get("inputFile").get("id"),
                    "inputFilePath": pred.get("inputFile").get("path"),
                    "inputFileFormat": pred.get("inputFile").get("format"),
                    "refinedFileName": pred.get("refinedFile").get("name"),
                    "refinedFilePath": pred.get("refinedFile").get("path"),
                    "refinedFileFormat": pred.get("refinedFile").get("format"),
                    "modelName": pred.get("inputFile").get("model").get("name"),
                    "modelGroup": pred.get("inputFile").get("model").get("group"),
                    "modelAccuracy":  accuracy,
                    "chart": pred.get("chart"),
                    "error": pred.get("error")
                })
            elif pred.get('error') is 'ERR002':
                preds.append({
                    "inputFileName": pred.get("inputFile").get("name"),
                    "inputFileId": pred.get("inputFile").get("id"),
                    "inputFilePath": pred.get("inputFile").get("path"),
                    "inputFileFormat": pred.get("inputFile").get("format"),
                    "chart": pred.get("chart"),
                    "error": pred.get("error")
                })

        return preds

    def dictToStr(self, dic):
        string = ''
        for idx, prop in enumerate(dic):
            string += prop+'='+str(dic[prop])
            if idx != len(dic.keys())-1:
                string += ', '

        return string

class ModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    serializer_class = ModelSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return Model.objects.all()
    

    @csrf_exempt
    def list(self, request):
        queryset = Model.objects.all()
        serializer = ModelSerializer(queryset, many=True)
        data = serializer.data

        for rec in data:            
            rec['accuracy'] = "학습 데이터(Training data)<br>"+self.dictToStr(rec['accuracy']['training'], ",")+"<br>테스트 데이터(Test data)<br>"+self.dictToStr(rec['accuracy']['test'], ",")
            rec['hyperparameters'] = self.dictToStr(rec['hyperparameters'], "<br>")

        return Response(data)

    def dictToStr(self, dic, sep):
        string = ''
        for idx, prop in enumerate(dic):
            string += prop+'='+str(dic[prop])
            if idx != len(dic.keys())-1:
                string += sep+' '

        return string
