
// https://stackoverflow.com/a/10834843/10265880
/**
 *
 */
function isNormalInteger(str) {
    return /^\+?(0|[1-9]\d*)$/.test(str);
}

/**
 *
 */
function isJson(str){
  try{
    return JSON.parse(str);
  } catch(e){
    return false
  }
}

/**
 *
 */
function get_ajax(e){
    var q= new XMLHttpRequest();
    q.open("get", e.getAttribute("data-ajax"), true);
    q.setRequestHeader(
        "Content-Type",
        "application/x-www-form-urlencoded; charset=UTF-8"
    );
    q.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    q.send();

    q.onreadystatechange = function () {
      if(q.readyState == 4 && q.status == 200){
        data = isJson(q.responseText);


      if(!data){
        e.innerHTML = q.responseText;
      } else {

        e.innerHTML = data["message"];

        // set color or text based on status
        console.log(data.hasOwnProperty("status"))
        if(data.hasOwnProperty("status")){
          console.log("adding status")
          e.setAttribute("data-color", data["status"]);
        }
        else{
          e.removeAttribute("data-color");
        }
      }

      if(e.hasAttribute("data-toggle") && document.querySelector('.field input#'+e.getAttribute("data-toggle"))){
        var el =  document.querySelector('.field input#'+e.getAttribute("data-toggle"))
        if(data["status"] === "success"){
       el.setAttribute("checked","checked");
        }
        else {
         el.removeAttribute("checked");
        }
      }

      // enable periodic update
      if(e.hasAttribute("data-freq") && isNormalInteger(e.getAttribute("data-freq"))){
        console.log(e.getAttribute("data-freq"))

        setTimeout(get_ajax.bind(this,e), e.getAttribute("data-freq")*1000);
      }
            }
    };
}

ajax = document.querySelectorAll('*[data-ajax]');

[].forEach.call(ajax, function (e) {
    console.log(e)
    get_ajax(e);

})


// toggle
document.addEventListener("click", function(e){
  if(e.target.matches('input.switch[data-url')){

    STATUS = {"true":"enable","false":"disable"};

    var q= new XMLHttpRequest();
    q.open("get", e.target.getAttribute("data-url") + STATUS[e.target.checked], true);
    q.setRequestHeader(
        "Content-Type",
        "application/x-www-form-urlencoded; charset=UTF-8"
    );
    q.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    q.send();

  }
})
