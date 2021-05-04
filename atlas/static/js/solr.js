/*

  Search flow

  - when site is accessed a request is made for the search template by including a tag in the header
    <script id="search-template" type="text/x-handlebars-template" src="/search/template"></script>

  - when user searches a json response with search results and permissions will
    be returned

  - handlebars.js is used to put the json data into the template


*/

(function () {
  // load search template
  // ====================
  var template = Handlebars.compile(
    document.getElementById("search-template").innerHTML
  );

  // formatting functions
  // ====================
  function toTitleCase(str) {
    // if string is already capitalized, return.
    if (str[0] === str[0].charAt(0).toUpperCase()) return str;

    str = str.toLowerCase().split(/(?:\s|_|text)+/);
    for (var i = 0; i < str.length; i++) {
      str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
    }
    return str.join(" ");
  }

  // handlerbars custom helpers
  // ==========================
  Handlebars.registerHelper("filter_name", function (aString) {
    return toTitleCase(aString);
  });

  function build_results(my_json) {
    var result_div = document.querySelector(".sr-results");

    document.querySelector(".body-mainCtn").style.visibility = "visible";
    document.querySelector(".body-mainCtn").style.removeProperty("overflow");

    // render markdown
    // ---------------
    var my_div = document.createElement("div");
    my_div.innerHTML = template(my_json);
    var md = window.markdownit();
    var my_md = my_div.getElementsByClassName("markdown");
    for (var x = 0; x < my_md.length; x++) {
      my_md[x].innerHTML = md.render(my_md[x].innerText.trim());
    }

    result_div.innerHTML = my_div.innerHTML;
  }
  var hAjx = null;
  document
    .querySelector(".sr-grp input")
    .addEventListener("input", function () {
      var t0 = performance.now();

      if (hAjx !== null) {
        hAjx.abort();
      }
      hAjx = new XMLHttpRequest();
      hAjx.open("get", "/search/search/" + this.value, true);
      hAjx.setRequestHeader("X-CSRFToken", csrftoken);
      hAjx.send();

      hAjx.onreadystatechange = function (e) {
        if (this.readyState == 4 && this.status == 200) {
          build_results(JSON.parse(this.responseText));

          console.log(
            "search took " + (performance.now() - t0) + " milliseconds."
          );
        }
      };
    });
})();
