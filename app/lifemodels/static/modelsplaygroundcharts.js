// import * as echarts from 'echarts';
function createAnalysisChart(inputFileName, selectedModel, data) {
    var chartDom = document.getElementById('main');
    var myChart = echarts.init(chartDom);
    var option;

    option = {
    title: {
        text: inputFileName,
        subtext: selectedModel,
        left: 'center'
    },
    tooltip: {
        trigger: 'item'
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
        name: selectedModel.split('_')[0],
        type: 'pie',
        stillShowZeroSum: false,
        radius: '50%',
        data: data,
        emphasis: {
            itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        }
        }
    ]
    };

    option && myChart.setOption(option);
}

function createDownloadFileBtn() {
    let ele = '';
    ele += '<div class="col-md-2">';
    ele += '<button type="button" id="idDataAnalysisDownload" class="btn btn-warning" onclick="downloadPrediction(this)">'+
            '<i class="glyphicon glyphicon-download-alt"></i></button>';
    ele += '</div>';
    $('#dataAnalysisChartsControl').append(ele);
}

function applySelect2(eleId,
    options,
    placeholder,
    allowClear,
    selectedOption) {
    // console.log(eleId,
        // options,
        // placeholder,
        // allowClear,
        // selectedOption);
    $('#'+eleId).select2({
        // tags: true,
        placeholder: placeholder,
        data: options,
        allowClear: allowClear
    });
    $('#'+eleId).val(selectedOption); // Select the option with a value of '1'
    $('#'+eleId).trigger('change'); // Notify any JS components that the value changed
}

function createModelSelect2(inputFileName, selectedOptionInfo, selectedModel) {
    let ele = '';
    // console.log(selectedOptionInfo);
    let modelList = [];
    for (let [modelName, modelInfo] of Object.entries(selectedOptionInfo)) {
        if (modelName === 'Text') continue;
        // console.log(modelName, modelInfo);
        modelList.push(modelName);
        
    }
    let dataAnalysis = selectedOptionInfo[selectedModel]['dataAnalysis'];
    ele += '<div class="col-md-5">';
    ele += '<label for="idChartModels">Model: </label>';
    ele += '<select id="idChartModels" name="chartModels" style="width: 100%;"></select>';
    ele += '</div>';
    $('#dataAnalysisChartsControl').append(ele);
    applySelect2('idChartModels', modelList, 'Select Models', false, [selectedModel]);
    createAnalysisChart(inputFileName, selectedModel, dataAnalysis);
    dataAnalysisChartsControlEvents();
}

function createInputFileSelect2(selectedFile, selectedModel) {
    // console.log(selectedFile)
    let data_info = JSON.parse(localStorage.getItem('modelsPlaygroundDataInfo'));
    let inputFileList = Object.keys(data_info);
    let ele = '';
    ele += '<div class="col-md-5">';
    ele += '<label for="idChartInputFiles">Input: </label>';
    ele += '<select id="idChartInputFiles" name="chartInputFiles" style="width: 100%;"></select>';
    ele += '</div>';
    $('#dataAnalysisChartsControl').html(ele);
    applySelect2('idChartInputFiles', inputFileList,  'Select Input Data', false, [selectedFile]);
    let selectedFileInfo = data_info[selectedFile];
    createModelSelect2(selectedFile, selectedFileInfo, selectedModel);

}

function createChart(data_info) {
    // console.log(data_info);
    // console.log(Object.keys(data_info));
    localStorage.setItem("modelsPlaygroundDataInfo", JSON.stringify(data_info));
    let selectedFile = Object.keys(data_info)[0];
    let selectedFileInfo = data_info[selectedFile];
    let selectedModel = Object.keys(selectedFileInfo).filter(function (letter) {
        return letter !== 'Text';
    });
    createInputFileSelect2(selectedFile, selectedModel[0]);
    // createDownloadFileBtn();
}

function dataAnalysisChartsControlEvents() {
    let chartInputFileEle = document.getElementById('idChartInputFiles');
    let chartModelEle = document.getElementById('idChartModels');

    chartInputFileEle.onchange = function() {
        let chartInputFileEleValue = chartInputFileEle.value;
        let chartModelEleValue = chartModelEle.value;
        console.log(chartInputFileEleValue, chartModelEleValue)
        createInputFileSelect2(chartInputFileEleValue, chartModelEleValue);
     }
     chartModelEle.onchange = function() {
        let chartInputFileEleValue = chartInputFileEle.value;
        let chartModelEleValue = chartModelEle.value;
        console.log(chartInputFileEleValue, chartModelEleValue)
        createInputFileSelect2(chartInputFileEleValue, chartModelEleValue);
     }

}