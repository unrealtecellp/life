window.onload = function() {

    console.log(map);

    alert('hi');
    for (var ele of map) { 
        if (ele[1] == 'multimedia'){
        var inpt = '<div class="col-md-3 nopadding"><div class="form-group">'+
                    '<label for="'+ele[0]+'">'+ele[0]+'</label>'+
                    '<input type="file" class="form-control" id='+ele[0]+'">'+
                    '</div></div>'
        }        
        else if (ele[1] == 'text'){
        var inpt = '<div class="col-md-3 nopadding"><div class="form-group">'+
                    '<label for="'+ele[0]+'">'+ele[0]+'</label>'+
                    '<input type="text" class="form-control" id='+ele[0]+'">'+
                    '</div></div>'          
        }
        else if (ele[1] == 'textarea'){
        var inpt = '<div class="col-md-3 nopadding"><div class="form-group">'+
                    '<label for="'+ele[0]+'">'+ele[0]+'</label>'+
                    '<textarea class="form-control" id='+ele[0]+'"></textarea>'+
                    '</div></div>'          
        };
        $('.new').append(inpt);
        
    };
};    
  