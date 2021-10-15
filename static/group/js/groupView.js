function follow(element){
    var status = element.innerText;
    var dataID = element.parentNode.parentNode.getAttribute("id");
    //console.log(dataID)
    if(status==="Follow")
    {
        element.innerText = "UnFollow";
        postReq(dataID,"Follow")
    }
    else
    {
        element.innerText = "Follow";
        postReq(dataID,"UnFollow")
    }
}

function postReq(id_in,status_in){
    let data = {
        "id": id_in,
        "password": status_in,
        "fab":12
    }
    fetch("https://5000-lavender-prawn-xtry6htw.ws-us11.gitpod.io/Account/Create", {method:"POST", body:data} )
}