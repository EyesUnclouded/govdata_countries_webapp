/**
 *
 *  VISUALIZE CATEGORIES DISTRIBUTION BAR CHART
 *
 **/

function visualize_categories_chart(countries_data, categories, cluster = 0, average_distribution) {

    document.getElementById('visualization').innerHTML = '<h1>Thematic categories</h1>';

    /**
     color palette from:
     http://colorbrewer2.org/#type=qualitative&scheme=Paired&n=13
     **/
    //var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb'];
    var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb', '#d9d9d9'];

    var categoriesBarChart_obj = {};
    var categoriesConfig_obj = {};
    var if_average_distribution = false;

    /**
    first show average distribution of cluster if more than 1 countries in cluster
     **/
    if (parseInt(cluster) > 0) {
        document.getElementById('visualization').innerHTML += '<h2> Cluster ' + cluster + '</h2>';
        console.log(countries_data);
        console.log(countries_data.length);
        if (Object.keys(countries_data).length > 1) {
            if_average_distribution = true;
            document.getElementById('visualization').innerHTML += '<div style="width:50%"><canvas id="average_distributionBarChart"></canvas></div><br>';

            var average_distributionConfig = {
                type: 'bar',
                data: {
                    datasets: [{
                        data: average_distribution,
                        backgroundColor: colors
                    }],
                    labels: categories
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
                        text: 'Average Distribution of Cluster'
                    },
                    scales: {
                        xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Categories'
                            }
                        }],
                        yAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Percentage of dataset count'
                            }
                        }]
                    }
                }
            };
        }
    }

    document.getElementById('visualization').innerHTML +='<hr class="dotted"><h4 class="text-center">Countries</h4>';

    //create bar chart for each country
    for (var country_id in countries_data) {
        var categoriesConfig = {
            type: 'bar',
            data: {
                datasets: [{
                    data: countries_data[country_id]['data'],
                    backgroundColor: colors
                }],
                labels: categories
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
                    text: countries_data[country_id]['country_title']
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Categories'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        ticks: {
                          suggestedMax: 100,
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Data % in Category (' + countries_data[country_id]['count_total'] + ' in total)'
                        }
                    }]
                }
            }
        };

        document.getElementById('visualization').innerHTML += '<div style="float:left; width:49.7%"><canvas id="categoriesBarChart' + country_id + '"></canvas></div>';

        categoriesBarChart_obj[country_id] = 'categoriesBarChart' + country_id;
        categoriesConfig_obj[country_id] = categoriesConfig;
    }
    var first = true;
    $.each(categoriesConfig_obj, function( key ) {
      if (first && if_average_distribution){
          var ctx = document.getElementById('average_distributionBarChart').getContext('2d');
          var myNewChart = new Chart(ctx, average_distributionConfig);
          first = false;
      }

      var ctx = document.getElementById('categoriesBarChart'+ key).getContext('2d');
      var myNewChart = new Chart(ctx, categoriesConfig_obj[key]);
    });
}