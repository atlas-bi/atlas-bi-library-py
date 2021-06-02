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
   * @param str
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

  // handlerbars custom helpers
  // ==========================
  Handlebars.registerHelper("filter_name", function (aString) {
    return toTitleCase(aString);
  });

  /**
   * @param my_json
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
      var t0 = performance.now();

      // remove nav links
      if (d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")) {
        var navLinks = Array.prototype.slice.call(
          d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")
        );
        for (var x = 0; x < navLinks.length; x++) {
          navLinks[x].parentElement.removeChild(navLinks[x]);
        }
      }

      // start progress
      d.dispatchEvent(
        new CustomEvent("progress-start", {
          cancelable: true,
          detail: {
            value: 90,
          },
        })
      );

      w.oldPopState = d.location.pathname;
      history.pushState(
        {
          state: "ajax",
          search: this.value,
        },
        d.title,
        w.location.origin + "/search/" + encodeURI(this.value)
      );


      if (hAjx !== null) {
        hAjx.abort();
      }
      hAjx = new XMLHttpRequest();
      hAjx.open("get", "/search/search/" + this.value, true);
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
})();
