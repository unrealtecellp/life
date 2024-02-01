// import * as echarts from 'echarts';

function createChart(data_info) {
    var chartDom = document.getElementById('main');
    var myChart = echarts.init(chartDom);
    var option;

    option = {
    title: {
        text: data_info['selectedModel'],
        // subtext: 'Fake Data',
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
        name: 'Harm Potential Level',
        type: 'pie',
        radius: '50%',
        data: data_info['data'],
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