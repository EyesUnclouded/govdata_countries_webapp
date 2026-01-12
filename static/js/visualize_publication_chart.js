/**
 *
 *  VISUALIZE PUBLICATION TIMELINE LINE CHART
 *
 **/

function visualize_publication_chart(countries_publication, start_month, countries_data, cluster, average_distribution) {

    document.getElementById('visualization').innerHTML = '<h1>Open Data Timeliness</h1>';

    var timeliness_factors = ['Avg days between release', 'Weekly avg', 'Bulk outliers'];
    var if_countries_timeliness = false;

    if (parseInt(cluster) > 0) {
        document.getElementById('visualization').innerHTML += '<h2> Cluster ' + cluster + '</h2><br>';
        document.getElementById('visualization').innerHTML +='<h2>Timeliness factors</h2>';
        if (Object.keys(countries_data).length > 1) {
            document.getElementById('visualization').innerHTML +='<h4>Average factors</h4>';

            document.getElementById('visualization').innerHTML +='<table class="table table-dark w-50"><thead> <tr> <th>Average days<br>between release</th> <th>Weekly average</th> <th>Bulk outliers</th> </tr></thead><tbody> <tr> <td>'+ average_distribution[0] +'</td> <td>'+ average_distribution[1] +'</td> <td>'+ average_distribution[2] +'</td> </tr></tbody> </table>';

        }


        document.getElementById('visualization').innerHTML +='<hr class="dotted"><h4 class="text-center">Countries</h4>';

        var bubble_datasets = [];

        var if_countries_timeliness = true;

        for (var country_id in countries_data){
            bubble_datasets.push({label: countries_data[country_id]['country_title'], data: [{x: countries_data[country_id]['data'][0], y: countries_data[country_id]['data'][1], r: countries_data[country_id]['data'][2] + 4}], backgroundColor:"#007bff", hoverBackgroundColor: "#fff", radius: 8});
        }
        document.getElementById('visualization').innerHTML += '<div><canvas id="countries_timelinessDiv"></canvas></div><br>';

        var countries_timelinessConfig = {
            type: 'bubble',
            data: {
                datasets: bubble_datasets
            },
            options: {
                tooltips: {
                    callbacks: {
                        label: function(t, d) {
                            var r_value = parseInt(d.datasets[t.datasetIndex].data[t.index].r) - 4;
                            return d.datasets[t.datasetIndex].label +
                                ': (Avg 0 Days: ' + t.xLabel + ', Weekly Avg: ' + t.yLabel + ', Bulk: ' + r_value + ')';
                        }
                    }
                },
                legend: {
                    display: false
                 },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Average days between release'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Weekly average'
                        }
                    }]
                },
                plugins: {
                    datalabels: {
                        anchor: 'center',
                        align: 'right',
                        color: function (context) {
                            return context.dataset.backgroundColor;
                        },
                        font: {
                            weight: 'bold'
                        },
                        formatter: function (value, context) {
                            return context.dataset.label;
                        },
                        offset: 10,
                        padding: 0
                    }
                }
            }
        };
    }

    document.getElementById('visualization').innerHTML += '<hr class="dotted"><h4 class="text-center">Monthly dataset releases</h4>';

    /**
     *
     * Monthly dataset publications
     */
    var month_list = [];
    var month_str = '';

    var start_month_year = start_month.split("-");
    var end_year = parseInt(start_month_year[0]) + 5;

    for (var year = parseInt(start_month_year[0]); year <= end_year; year++){
        for (var month = 1; month <= 12; month++){
            if (year === parseInt(start_month_year[0]) && month < parseInt(start_month_year[1])){
                continue;
            }

            if (month < 10) month_str = '0' + month.toString();
            else month_str = month.toString();

            month_list.push(year.toString() + '-' + month_str);

            if ((year === end_year) && (month === parseInt(start_month_year[1]))) break;
        }
    }

    //var countries_chart_obj = {};
    var publicationLineChart_obj = {};
    var publicationConfig_obj = {};
    // var countries_pub_max = 0;
    //create line chart for each country
    for (var country_id in countries_publication){
        var country_pub_months = [];

        //check for each month if the country has publications there if not put 0 for this month
        for (var i = 0; i<month_list.length; i++){
            if (month_list[i] in countries_publication[country_id]['pub_month']){
                //var normalized_pub_count = 100 * (countries_publication[country_id]['pub_month'][month_list[i]] / countries_publication[country_id]['pub_total'])
                //country_pub_months.push(normalized_pub_count);
                country_pub_months.push(countries_publication[country_id]['pub_month'][month_list[i]]);

                //if (normalized_pub_count > countries_pub_max) countries_pub_max = normalized_pub_count;
            }
            else {
                country_pub_months.push(null);
            }

        }

        if (country_id === 'cz') {
            console.log(country_pub_months);
        }
        var line_country_obj = {label: countries_publication[country_id]['country_title'], fill: false, data: country_pub_months, backgroundColor: '#fff', borderColor: '#007bff'};

        var publicationConfig = {
        type: 'line',
        data: {
            labels: month_list,
            datasets: [line_country_obj]
        },
        options: {
            plugins: {
                datalabels: false
            },
            legend: {
                display: false
             },
            responsive: true,
            title: {
                display: true,
                text: countries_publication[country_id]['country_title']
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Year-Month'
                    }
                }],
                yAxes: [{
                    display: true,
                    //ticks: {
                    //  suggestedMax: 100,
                    //},
                    scaleLabel: {
                        display: true,
                        labelString: 'Publications (' + countries_publication[country_id]['pub_total'].toString() + ' in total)'
                    }
                }]
            },
            onAnimationProgress: function() { drawDatasetPointsLabels() },
            onAnimationComplete: function() { drawDatasetPointsLabels() }
        }};


        document.getElementById('visualization').innerHTML += '<div style="float:left; width:49.7%"><canvas id="publicationLineChart'+ country_id +'"></canvas></div>';

        //publicationLineChart_obj[country_id] = document.getElementById('publicationLineChart'+ country_id).getContext('2d');
        publicationLineChart_obj[country_id] = 'publicationLineChart'+ country_id;
        publicationConfig_obj[country_id] = publicationConfig;
        //countries_chart_obj[country_id] = new Chart(publicationLineChart_obj[country_id], publicationConfig);

    }

    var first = true;
    $.each(publicationConfig_obj, function( key ) {
      if (if_countries_timeliness && first){
          var ctx = document.getElementById('countries_timelinessDiv').getContext('2d');
          var myNewChart = new Chart(ctx, countries_timelinessConfig);
          first = false;
      }

      var ctx = document.getElementById('publicationLineChart'+ key).getContext('2d');
      var myNewChart = new Chart(ctx, publicationConfig_obj[key]);
    });

}