// get progress report button
$(document).ready(function() {
    // console.log('qwaaszxzx');
    $("#progressreport").click(function() {
        $.getJSON('/progressreport', {
        }, function(data) {
            progressreport = data.progressreport
            // console.log('qwaaszxzx');
            if (progressreport !== '') {
                console.log(progressreport);
                progressreporttable = '';
                count = 0;
                progressreporttable += '<div class="row"><div class="col-xs-12">';
                // progressreporttable += '<p id="totalrecords">Total Records:&nbsp;'+count+'</p>';
                progressreporttable += '<table class="table table-hover table-responsive text-center" id="myTable">'+
                                        '<thead><tr>'+
                                        // '<th onclick="sortTable(0)">Id</th>'+
                                        // '<th><input type="checkbox" id="headcheckbox" onchange="checkAllLexeme(this)" name="chk[]" checked/>&nbsp;</th>'+
                                        '<th class="text-center" onclick="sortTable(0)">Speaker Name</th>'+
                                        '<th class="text-center" onclick="sortTable(1)">Assigned To</th>'+
                                        '<th class="text-center" onclick="sortTable(2)">Total Files</th>'+
                                        '<th class="text-center" onclick="sortTable(3)">Completed Files</th>'+
                                        '<th class="text-center" onclick="sortTable(4)">Remaining Files</th>'+
                                        // '<th>View</th>'+
                                        // '<th>Edit</th>'+
                                        // '<th>Delete</th>'+
                                        '</tr></thead>';

                progressreporttable += '<tbody id="myTableBody">';
                totalSum = 0;
                completedSum = 0;
                remainingSum = 0;
                for (let [username, usersharedetails] of Object.entries(progressreport)) {
                    for (let [speakername, commentstats] of Object.entries(usersharedetails)) {
                        console.log(speakername, username, commentstats)
                        
                        total = commentstats[0]
                        totalSum += total
                        completed = commentstats[1]
                        completedSum += completed
                        remaining = commentstats[2]
                        remainingSum += remaining
                        percentcomplete = completed/total*100;
                        console.log(percentcomplete);
                        if (percentcomplete <= 10) {
                            completioncolor = 'danger';
                        }
                        else if (percentcomplete > 10 && percentcomplete < 100) {
                            completioncolor = 'warning';
                        }
                        else if (percentcomplete == 100) {
                            completioncolor = 'success';
                        }
                        progressreporttable += '<tr class="'+completioncolor+'">';
                        // progressreporttable += '<td><input type="checkbox" id="lexemecheckbox" onchange="checkLexeme(this)" name="name1" checked/></td>'
                        progressreporttable += '<td id="">'+speakername+'</td>'+
                                            '<td id="">'+username+'</td>'+
                                            '<td id="">'+total+'</td>'+
                                            '<td id="">'+completed+'</td>'+
                                            '<td id="">'+remaining+'</td>';
                    // progressreporttable += '<td><button type="button" class="btn btn-primary lexemeview">View</button></td>'+
                    //                         '<td><button type="button" class="btn btn-warning lexemeedit">Edit</button></td>'+
                    //                         '<td><button type="button" class="btn btn-danger lexemedelete">Delete</button></td>';
                    progressreporttable += '</tr>';
                    }
                }
                progressreporttable += '</tbody></table>';
                progressreporttable += '<strong>Total Sum: '+totalSum+'</strong><br>'+
                                        '<strong>Completed Sum: '+completedSum+'</strong><br>'+
                                        '<strong>Remaining Sum: '+remainingSum+'</strong><br>';
                progressreporttable += '</div></div>';

            }
            $('.progressreport').html(progressreporttable);
        });
    });  
});
