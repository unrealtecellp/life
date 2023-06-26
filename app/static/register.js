$("#username").keyup(function(){
    let special_chars = '!@#$%^&*()-=+[{]}\\|;:\'\",<.>/? ';
    // console.log(special_chars);
    let char = document.getElementById('username').value;
    if (char){
        last_char = char[char.length-1];
        // console.log(last_char);
        if (special_chars.indexOf(last_char) > -1) {
            // console.log(last_char);
            alert("Please use only letters, digits and underscore")
            document.getElementById('username').value = char.slice(0, char.length-1)
        }
        for(let i=0; i<=char.length; i++) {
            console.log(char[i]);
            if (special_chars.indexOf(char[i]) > -1) {
                alert("Please use only letters, digits and underscore")
                document.getElementById('username').value = char.slice(0, i)+char.slice(i+1, char.length)
            }
        }
    }
});