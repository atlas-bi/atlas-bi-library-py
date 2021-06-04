/*

  Search flow

  - when site is accessed a request is made for the search template by including a tag in the header
    <script id="search-template" type="text/x-handlebars-template" src="/search/template"></script>

  - when user searches a json response with search results and permissions will
    be returned

  - handlebars.js is used to put the json data into the template


*/

(function () {

  var d = document,
      w = window,
      grp = d.getElementsByClassName("sr-grp")[0],
      m = d.getElementsByClassName("body-mainCtn")[0],
      hst = d.getElementsByClassName("sr-hst")[0],
      i = grp.querySelector(".sr-grp input"),
      cls = d.getElementById("sr-cls"),
      scls = d.getElementById("nav-search");


  // load search template
  // ====================
  var template = Handlebars.compile(
    d.getElementById("search-template").innerHTML
  );

  // formatting functions
  // ====================
  /**
   * @param {string} str String to convert to title case.
   */
  function toTitleCase(str) {
    // if string is already capitalized, return.
    if (str[0] === str[0].charAt(0).toUpperCase()) return str;

    str = str.toLowerCase().split(/(?:\s|_|text)+/);
    for (var i = 0; i < str.length; i++) {
      str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
    }
    return str.join(" ");
  }

  /**
   * Register handlerbars custom helpers.
   */
  Handlebars.registerHelper("filter_name", function (aString) {
    return toTitleCase(aString);
  });

  Handlebars.registerHelper("filter_name_lower", function(str) {
    return str.toLowerCase();
  });
  Handlebars.registerHelper("filter_exists", function(context) {
    return  Object.entries(context).map(function(o) { return o[1]; }).reduce(function(a, b){return a+b;}) > 0;
  });
  /**
   * Build search results from json result.
   *
   * @param {JSON} my_json Json to convert to search results html.
   */
  function build_results(my_json) {

    d.querySelector(".body-mainCtn").style.visibility = "visible";
    d.querySelector(".body-mainCtn").style.removeProperty("overflow");

    // render markdown
    // ---------------
    var my_div = d.createElement("div");
    my_div.innerHTML = template(my_json);
    var md = w.markdownit();
    var my_md = my_div.getElementsByClassName("markdown");
    for (var x = 0; x < my_md.length; x++) {
      my_md[x].innerHTML = md.render(my_md[x].innerText.trim());
    }

    // finish progress
    d.dispatchEvent(new CustomEvent("progress-finish"));

    m.innerHTML = my_div.innerHTML;
  }
  var hAjx = null;
  d
    .querySelector(".sr-grp input")
    .addEventListener("input", function () {
      search();
    });

  // hide search suggestions/history on scroll
  d.addEventListener(
    "scroll",
    function () {
      i.blur();
      hst.style.display = "none";
    },
    {
      passive: true,
    }
  );

 /**
  * When a search filter is applied.
  */
  d.addEventListener(
    "click",
    function (e) {
      // fairly broad target so we can catch click all over the label.
      if(e.target.closest('.search-filter')) {
        // prevent duplicate events from all the children
        e.stopImmediatePropagation();
        var input = e.target.closest('.search-filter').querySelector('input');
        // if this is an "type", we only can search one "type" at a time.
        // so we will uncheck the other types, and also reset all checkboxes.
        if (input.parentElement.hasAttribute("group") && input.parentElement.getAttribute("group") === "type"){
          var types = d.querySelectorAll('.search-filter input:checked');
          console.log(types)
          for(var i=0; i < types.length;i++){
            console.log(types[i] != input)
            if(types[i] != input){
              types[i].checked = false;
            }
          }
        }
        // if they did not click on the input then we need to manually toggle it.
        if(!e.target.matches('.search-filter input')){
          input.checked = !input.checked;
        }
        console.log('filter clicked');
        setTimeout(function(){
          search();
        },0)
      }

    }, true
  );

  /**
   *
   */
  function remove_side_nav() {
    // remove nav links
      if (d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")) {
        var navLinks = Array.prototype.slice.call(
          d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")
        );
        for (var x = 0; x < navLinks.length; x++) {
          navLinks[x].parentElement.removeChild(navLinks[x]);
        }
      }
  }
  /**
   *
   */
  function search(){
    var t0 = performance.now();

    remove_side_nav();

    // start progress
    d.dispatchEvent(
      new CustomEvent("progress-start", {
        cancelable: true,
        detail: {
          value: 90,
        },
      })
    );

    // vars
    var search_url = "/search/";

    // build search url
    // get any checked filters and add to search query.
    // 1. get type
    var type = d.querySelector('.search-filter[group="type"][group-value] input:checked') ? d.querySelector('.search-filter[group="type"][group-value] input:checked').parentElement.getAttribute('group-value') : 'query';
    console.log(type)
    d.querySelectorAll('.search-filter input:checked');


    var search_text = d.querySelector(".sr-grp input").value;

    search_url += type + "/" + search_text

    w.oldPopState = d.location.pathname;
    // history.pushState(
    //   {
    //     state: "ajax",
    //     search: search_url,
    //   },
    //   d.title,
    //   w.location.origin + "/search/" + encodeURI(this.value)
    // );


    if (hAjx !== null) {
      hAjx.abort();
    }
    hAjx = new XMLHttpRequest();
    hAjx.open("post", search_url, true);
    hAjx.setRequestHeader("X-CSRFToken", csrftoken);
    hAjx.send();

    hAjx.onreadystatechange = function (e) {
      if (this.readyState === 4 && this.status === 200) {
        build_results(JSON.parse(this.responseText));

        console.log(
          "search took " + (performance.now() - t0) + " milliseconds."
        );
      }
    };
  }
})();
