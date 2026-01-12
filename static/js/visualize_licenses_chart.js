/**
 *
 *  VISUALIZE LICENSES CHARTS
 *
 **/

function visualize_licenses_chart(data) {

    var open_licenses = data['open_licenses'];
    var top5_licenses = data['top5_licenses'];

    document.getElementById('visualization').innerHTML = '<h1>'+ data["country_title"] +'</h1>' +
        '<h3>Open Licenses</h3>'+
        '<div class="canvas-holder"><canvas id="open_licensesDiv"></canvas></div>' +
        '<h3>Top 5 most used licenses</h3>'+
        '<div class="canvas-holder"><canvas id="top5_licensesDiv"></canvas></div>';

    var open_licensesDiv = document.getElementById('open_licensesDiv').getContext('2d');
    var top5_licensesDiv = document.getElementById('top5_licensesDiv').getContext('2d');

    /**
     color palette from:
     http://colorbrewer2.org/#type=qualitative&scheme=Paired&n=13
     **/
    //var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb'];
    var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb', '#d9d9d9'];

    var open_licensesConfig = {
        type: 'bar',
        data: {
            datasets: [{
                data: open_licenses['data'],
                backgroundColor: colors
            }],
            labels: open_licenses['licenses']
        },
        options: {
            plugins: {
                        datalabels: false
                    },
            responsive: true,
            legend: {
                display: false
            },
            title: {
                display: true,
                text: data['country_title']
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'License'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Number of Datasets'
                    }
                }]
            }
        }
    };

    var open_licensesBarChart = new Chart(open_licensesDiv, open_licensesConfig);

    var top5_licensesConfig = {
        type: 'bar',
        data: {
            datasets: [{
                data: top5_licenses['data'],
                backgroundColor: colors
            }],
            labels: top5_licenses['licenses']
        },
        options: {
            plugins: {
                        datalabels: false
                    },
            responsive: true,
            legend: {
                display: false
            },
            title: {
                display: true,
                text: data['country_title']
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'License'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Number of Datasets'
                    }
                }]
            }
        }
    };

    var top5_licensesBarChart = new Chart(top5_licensesDiv, top5_licensesConfig);
}