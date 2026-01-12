/**
 *
 *  VISUALIZE COUNTRY PIE CHART
 *
 **/

function visualize_country_pie(data) {

    document.getElementById('visualization').innerHTML = '<h1>'+ data["country_title"] +'</h1>' +
        '<h3>Dataset count by category</h3>'+
        '<div class="canvas-holder"><canvas id="categoriesPieChart"></canvas></div>' +
        '<h3>Dataset count by catalogue</h3>'+
        '<div class="canvas-holder"><canvas id="cataloguesPieChart"></canvas></div>';

    var categoriesPieChart_div = document.getElementById('categoriesPieChart').getContext('2d');
    var cataloguesPieChart_div = document.getElementById('cataloguesPieChart').getContext('2d');

    /**
     color palette from:
     http://colorbrewer2.org/#type=qualitative&scheme=Paired&n=13
     **/
    //var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb'];
    var colors = ['#69de86','#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#bc80bd','#ccebc5','#ffed6f', '#7284fb', '#d9d9d9'];


    /*
    PIE CHART FOR CATEGORIES COUNT
     */

    var categoriesConfig = {
        type: 'pie',
        data: {
            datasets: [{
                data: data['count_categories']['count'],
                backgroundColor: colors
            }],
            labels: data['count_categories']['categories']
        },
        options: {
            plugins: {
                        datalabels: false
                    },
            responsive: true,
            legend: {
                position: 'left',
                labels: {
                    padding: 20
                }
            }
        }
    };

    var categoriesPieChart = new Chart(categoriesPieChart_div, categoriesConfig);


    /*
    PIE CHART FOR CATALOGUES COUNT
     */

    colors = colors.slice(0, data['count_catalogues']['count'].length);

    var cataloguesConfig = {
        type: 'pie',
        data: {
            datasets: [{
                data: data['count_catalogues']['count'],
                backgroundColor: colors
            }],
            labels: data['count_catalogues']['catalogues']['desc']
        },
        options: {
            plugins: {
                        datalabels: false
                    },
            responsive: true,
            legend: {
                position: 'left',
                labels: {
                    padding: 20
                }
            }
        }
    };

    var cataloguesPieChart = new Chart(cataloguesPieChart_div, cataloguesConfig);
}