//console.log($('#visualization').attr("class"))
//$('#visualization').collapse();
//console.log($('#visualization').attr("class"))

/**
Deering, S. (2011). Get URL parameters using jQuery. Retrieved April 13, 2020 from https://www.sitepoint.com/url-parameters-jquery/
 **/
$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}

function changeURL(method, params = {}) {
    /**
Nolasco, F. (2013). How do we update URL or query strings using javascript/jQuery without reloading the page? Answer by user Fabio Nolasco. Retrieved April 13, 2020 from https://stackoverflow.com/a/19279268
 **/
    if (history.pushState) {
        var url = window.location.protocol + "//" + window.location.host + window.location.pathname + '?method=' + method;

        if ('country_id' in params){
            url += '&country_id=' + params['country_id'];
        }
        if ('cluster' in params){
            url += '&cluster=' + params['cluster'];
        }

        window.history.pushState({path:url},'',url);
    }
}


function changeVisualization () {
    if($("#method_loading").is(":visible"))
        $("#method_loading").hide();
    else
        $("#method_loading").show();


    var x = $('#visualization');

    console.log("toggle" )
    console.log($('#visualization').attr("class"))
    $('#visualization').collapse('toggle');
    console.log($('#visualization').attr("class"))
}

function loading_show(){
    $("#method_loading").show();
    $('#visualization').slideUp(200);
    //$('#visualization').stop().slideUp(200);
}

function loading_hide(){
    $("#method_loading").hide();
    $('#visualization').slideDown(400);
    //$('#visualization').stop().slideDown(400);
}

/**
function testcollapse_toggle(){
    $('#visualization').collapse('toggle');
    console.log($('#visualization').attr("class"))
}
function testcollapse_toggle_false(){
    $('#visualization').collapse({
        toggle: false
    });
    console.log($('#visualization').attr("class"))
}
function testcollapse_hide(){
    $('#visualization').collapse('hide');
    console.log($('#visualization').attr("class"))
}
function testcollapse_show(){
    $('#visualization').collapse('show');
    console.log($('#visualization').attr("class"))
}
 **/