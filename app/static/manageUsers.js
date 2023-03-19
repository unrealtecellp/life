function activeform(buttonType) {
    var x = document.getElementById("userdisplay");

    if (x.style.display === "none") {
        x.style.display = "block";
    } else if (buttonType == 'closebutton') {
        x.style.display = "none";
    }
}

// $(document).ready(function () {
// $('#userdetailsmodal').on('show.bs.modal', function () {
$('.userview').click(function () {
    // $('#userdetailsmodal').show.bs.modal
    // document.getElementById("userdisplay").style.display = "block";
    var username_id = $(this).attr("id");
    var username = username_id.split("++")[1]
    console.log('Username', username)

    // $.getJSON("{{url_for('getoneuserdetails')}}", {
    $.getJSON("/getoneuserdetails", {
        username: String(username)
    }, function (data) {
        console.log("Received data", data.userdetails)
        console.log("End Received data")
        uname = data.userdetails.username
        cur_id = "display++username"
        // document.getElementById(cur_id).value = uname
        document.getElementById(cur_id).innerHTML = uname

        uprofile = data.userdetails.userProfile
        for (var key in uprofile) {
            cur_id = "display++" + key
            console.log("Current ID", cur_id)
            cur_value = uprofile[key]
            console.log("Value", cur_value)
            // document.getElementById(cur_id).value = cur_value
            document.getElementById(cur_id).innerHTML = cur_value
        }
    });
});

$('.useractions').click(function () {
    window.location.href = window.location.href.replace("manageusers", "updateuserstatus")
    var username_id = $(this).attr("id");
    var username = username_id.split("++")[1]
    var action = username_id.split("++")[0]
    var status = document.getElementById("iduserRole++" + username).value
    console.log(username)

    $.getJSON("/updateuserstatus", {
        username: String(username),
        action: String(action),
        status: String(status)
    }, function (data) {
        console.log(data);
        console.log('Reloaded');
        location.reload();

    });
});

$('.addnewuser').click(function () {
    window.location.href = window.location.href.replace("manageusers", "register")
    // window.location.href = window.location.href.replace("updateuserstatus", "register")
    // = "{{ url_for('register') }}"
});

$('#closebutton').click(function () {
    buttonType = $(this).attr("id")
    activeform(buttonType)
    // activeform()
    // $('#formdisplay').find('input, select').attr('disabled', false);
    // $('#editbutton').attr('hidden', true)
})
// })