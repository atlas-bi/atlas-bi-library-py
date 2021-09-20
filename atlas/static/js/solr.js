/*

  Search flow

  - when site is accessed a request is made for the search template by including a tag in the header
    <script id="search-template" type="text/x-handlebars-template" src="/search/template"></script>

  - when user searches a json response with search results and permissions will
    be returned

  - handlebars.js is used to put the json data into the template


*/

(function () {
Function.prototype.debounce = function (delay) {
  var outter = this,
    timer;

  return function () {
    var inner = this,
      args = [].slice.apply(arguments);

    clearTimeout(timer);
    timer = setTimeout(function () {
      outter.apply(inner, args);
    }, delay);
  };
};

  var d = document,
      w = window;
      var searchResultsContainer = document.getElementById("search-results");
      // grp = d.getElementsByClassName("sr-grp")[0],
      // m = d.getElementsByClassName("body-mainCtn")[0],
      // hst = d.getElementsByClassName("sr-hst")[0],
      // i = grp.querySelector(".sr-grp input"),
      // cls = d.getElementById("sr-cls"),
      // scls = d.getElementById("nav-search");
  /**
   * scroll to top when clicking search button
   */
   // document.addEventListener('click', function(e){
   //  if(e.target.closest('#nav-search')){
   //    document.documentElement.scrollTop = document.body.scrollTop = 0;
   //  }
   // });


  // load search template
  // ====================
  // var template = Handlebars.compile(
  //   d.getElementById("search-template").innerHTML
  // );

  // formatting functions
  // ====================
  /**
   * @param {string} str String to convert to title case.
   */
  // function toTitleCase(str) {
  //   // if string is already capitalized, return.
  //   if (str[0] === str[0].charAt(0).toUpperCase()) return str;

  //   str = str.toLowerCase().split(/(?:\s|_|text)+/);
  //   for (var i = 0; i < str.length; i++) {
  //     str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
  //   }
  //   return str.join(" ");
  // }

  /**
   * Register handlerbars custom helpers.
   */
  // Handlebars.registerHelper("titleCase", function (aString) {
  //   // fix single line values
  //   aString = aString=='Y' ? 'Yes' : aString;
  //   aString = aString=='N' ? 'No' : aString;
  //   aString = aString=='1' ? 'Yes' : aString;
  //   aString = aString=='0' ? 'No' : aString;
  //   if (typeof aString == "string"){
  //         return toTitleCase(aString);
  //   }
  //   return toTitleCase(aString[0]);

  // });

  // Handlebars.registerHelper("addition", function (a,b) {
  //   return a + b;
  // });



  // Handlebars.registerHelper("get_page", function (b) {
  //   if(b !== 0){
  //     return Math.ceil(b/10);
  //   }
  //   else {
  //     return 1;
  //   }
  // });


  // Handlebars.registerHelper("get_pages", function (results, start) {
  //   // current page
  //   page = start !== 0 ? Math.ceil(start/10) : 1;

  //   pages = results > 10 ? Math.ceil(results / 10) : 1;

  //   page_list = [];
  //   for(var x=1;x<=pages;x++){
  //     if (
  //         x <= Math.max(page + 2, 5) &&
  //         (x >= Math.max(page - 2, 0) || pages - x < 5)
  //       ) {
  //       page_list.push(x);
  //     }

  //   }

  //   return page_list;
  //   // get three pages on each side, or up to 6 if we are at start/end of results.
  // });


  // Handlebars.registerHelper("filter_type", function (my_filters, my_facet, my_filter, options) {
  //   return my_filters[my_facet] && my_filters[my_facet].indexOf(my_filter) != -1 ? "checked" : "";
  // });

  // Handlebars.registerHelper("filter_open_collapse", function (my_index, my_facets, my_facet, my_filter, my_filters, options) {
  //   /**
  //    * idealy we do not want to show a bunch of search filters with 0... or
  //    * a million valid search filters. Only show the first 5, or first couple
  //    * that are not 0.
  //    * however, not any group that has a filter, or on type
  //    *
  //    * if 0index is < 5
  //    * if my_index == 5 and 0index >=5
  //    */
  //   // never collapse the type box
  //   if(my_facet == 'type'){
  //     return options.inverse(this);
  //   }
  //   // get index of any checked boxes
  //   var checked_index = my_filters[my_facet] ? Object.keys(my_facets).indexOf(my_filters[my_facet][0]) : -1;

  //   var zero_index = Object.entries(my_facets).map(function(o){return o[1];}).findIndex(function(o){return o===0;});

  //   zero_index = zero_index === -1 ? my_index + 1 : zero_index;
  //   // add one to the checked index, so that we hide the next element.
  //   zero_index = Math.max(checked_index+1, zero_index);
  //   if (my_index == 5 && zero_index >= 5 || zero_index <5 && my_index == zero_index){
  //     return options.fn(this);
  //   }
  //   return options.inverse(this);
  // });

  // Handlebars.registerHelper("filter_close_collapse", function (my_index, my_facets,my_facet, my_filter, my_filters, options) {
  //   // never collapse the type box
  //   if(my_facet == 'type'){
  //     return options.inverse(this);
  //   }
  //   var zero_index = Object.entries(my_facets).map(function(o){return o[1];}).findIndex(function(o){return o===0;});
  //   if (my_index == Object.entries(my_facets).length-1 && (my_index >= 5 || (zero_index <= 5 && zero_index != -1))){
  //     return options.fn(this);
  //   }
  //   return options.inverse(this);
  // });

  // Handlebars.registerHelper('if_cond', function (v1, operator, v2, options) {
  //   switch (operator) {
  //       case '==':
  //           return (v1 == v2) ? options.fn(this) : options.inverse(this);
  //       case '===':
  //           return (v1 === v2) ? options.fn(this) : options.inverse(this);
  //       case '!=':
  //           return (v1 != v2) ? options.fn(this) : options.inverse(this);
  //       case '!==':
  //           return (v1 !== v2) ? options.fn(this) : options.inverse(this);
  //       case '<':
  //           return (v1 < v2) ? options.fn(this) : options.inverse(this);
  //       case '<=':
  //           return (v1 <= v2) ? options.fn(this) : options.inverse(this);
  //       case '>':
  //           return (v1 > v2) ? options.fn(this) : options.inverse(this);
  //       case '>=':
  //           return (v1 >= v2) ? options.fn(this) : options.inverse(this);
  //       case '&&':
  //           return (v1 && v2) ? options.fn(this) : options.inverse(this);
  //       case '||':
  //           return (v1 || v2) ? options.fn(this) : options.inverse(this);
  //       default:
  //           return options.inverse(this);
  //   }
  // });

  // Handlebars.registerHelper('if_in', function (v1, v2, options) {
  //   return JSON.parse(v2).indexOf(v1[0]) != -1 ? options.fn(this) : options.inverse(this);
  // });

  // Handlebars.registerHelper("filter_name_lower", function(str) {
  //   return str.toLowerCase();
  // });

  // Handlebars.registerHelper("filter_exists", function(my_facets, my_facet, my_filters) {
  //   // if sum is 0 (no matches in group), then the filter will be hidden.
  //   // but we should still show the filter if any options are checked regardless.

  //   if(my_filters.hasOwnProperty(my_facet) || my_facet == 'type'){
  //     return true;
  //   }

  //   return  Object.entries(my_facets).map(function(o) { return o[1]; }).length > 0 ? Object.entries(my_facets).map(function(o) { return o[1]; }).reduce(function(a, b){return a+b;}) > 0 : true;
  // });


  /**
   * Build search results from json result.
   *
   * @param {JSON} my_json Json to convert to search results html.
   */
  function build_results(my_json) {

    // d.querySelector(".body-mainCtn").style.visibility = "visible";
    // d.querySelector(".body-mainCtn").style.removeProperty("overflow");

    // // render markdown
    // // ---------------
    // var my_div = d.createElement("div");
    // my_div.innerHTML = template(my_json);
    // var md = w.markdownit();
    // var my_md = my_div.getElementsByClassName("markdown");
    // for (var x = 0; x < my_md.length; x++) {
    //   my_md[x].innerHTML = md.render(my_md[x].innerText.trim());
    // }

    // // finish progress
    // d.dispatchEvent(new CustomEvent("progress-finish"));

    // m.innerHTML = my_div.innerHTML;
    console.log(my_json)

    var formattedResults = my_json["docs"].map(function(result){
      console.log(result)
      // Create elements
      var link = document.createElement("a");
      var media = document.createElement("div");
      var img = document.createElement("div");
      var content = document.createElement("div");
      var title = document.createElement("strong");
      var excerpt = document.createElement("p");
      var tags = document.createElement("span");
      var type = document.createElement("span");

      media.classList.add("media")

      img.classList.add("media-left")
      content.classList.add("media-content")

      link.href = result.id;
      link.classList.add(
        "panel-block",
        "p-3",
        "is-block"
      );

      excerpt.classList.add("search-snippet");
      desc = result.hasOwnProperty("description") ? result.description[0] : ""
      console.log(typeof desc)
      excerpt.innerHTML = desc.substr(0,160) + "…";

      title.classList.add("is-flex", "is-justify-content-space-between");
      title.innerText = result.name;

      type.innerText = result.type;
      type.classList.add(
        "tag",
        "is-info",
        "is-light",
        "ml-3"

      );

      if(result.certification){

        // this is dupped in the django tag. should fix sometime
        var cert_class = {
          "Analytics Certified": "is-success",
          "Analytics Reviewed": "is-info",
          "Epic Released": "is-warning",
          "Legacy": "is-warning",
          "High Risk": "is-danger",
        }

        var cert = document.createElement("span");
        cert.innerText = result.certification;
        cert.classList.add(
          "tag",
          cert_class[result.certification[0]],
              "is-light"

        );
        tags.appendChild(cert)
      }

      // Put all the elements together
      img.innerHTML = `
                <figure class="image is-64x64"><img data-src="` + result.id + `/image?size=64x64"
                         src="/static/img/loader.gif"
                         alt="report image"/>
                </figure>`


      tags.appendChild(type)
      title.appendChild(tags);
      content.appendChild(title)
      content.appendChild(excerpt)
      media.appendChild(img);

      media.appendChild(content);


      link.appendChild(media);

      return link;
   });

  formattedResults.map(function(el){
    searchResultsContainer.insertAdjacentElement("beforeend", el)
  });

  document.dispatchEvent(new CustomEvent("lazy"))
  }
  var hAjx = null;
  d
    .getElementById('search')
    .addEventListener("input",  search.debounce(250));
  d.getElementById('search-form').addEventListener("submit", (e) => e.preventDefault());

  // hide search suggestions/history on scroll
  // d.addEventListener(
  //   "scroll",
  //   function () {
  //     i.blur();
  //     hst.style.display = "none";
  //   },
  //   {
  //     passive: true,
  //   }
  // );

  /**
   * changing pages
   */
   // d.addEventListener('click',function(e){
   //  if(e.target.closest('.page-link')) {
   //    search(e.target.closest('.page-link').value);
   //  }
   // });
 /**
  * When a search filter is applied.
  */
  // d.addEventListener(
  //   "click",
  //   function (e) {
  //     // fairly broad target so we can catch click all over the label.
  //     if(e.target.closest('.search-filter')) {
  //       // prevent duplicate events from all the children
  //       e.stopImmediatePropagation();
  //       var input = e.target.closest('.search-filter').querySelector('input');
  //       // if this is an "type", we only can search one "type" at a time.
  //       // so we will uncheck the other types, and also reset all checkboxes.
  //       if (input.parentElement.hasAttribute("group") && input.parentElement.getAttribute("group") === "type"){
  //         var types = d.querySelectorAll('.search-filter input:checked');
  //         for(var i=0; i < types.length;i++){
  //           if(types[i] != input){
  //             types[i].checked = false;
  //           }
  //         }
  //       }
  //       // if they did not click on the input then we need to manually toggle it.
  //       if(!e.target.matches('.search-filter input')){
  //         input.checked = !input.checked;
  //       }
  //       console.log('filter clicked');
  //       setTimeout(function(){
  //         search(1);
  //       },0);
  //     }

  //   }, true
  // );

  /**
   *
   */
  // function remove_side_nav() {
  //   // remove nav links
  //     if (d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")) {
  //       var navLinks = Array.prototype.slice.call(
  //         d.querySelectorAll(".sideNav .nav-link:not(#nav-search)")
  //       );
  //       for (var x = 0; x < navLinks.length; x++) {
  //         navLinks[x].parentElement.removeChild(navLinks[x]);
  //       }
  //     }
  // }
  /**
   *
   */
  function search(page){
    var t0 = performance.now();


  searchResultsContainer.textContent = "";


    // remove_side_nav();

    // start progress
    // d.dispatchEvent(
    //   new CustomEvent("progress-start", {
    //     cancelable: true,
    //     detail: {
    //       value: 90,
    //     },
    //   })
    // );

    // vars
    var search_url = "/search/";

    // build search url
    // get any checked filters and add to search query.
    // 1. get type
    // var type = d.querySelector('.search-filter[group="type"][group-value] input:checked') ? d.querySelector('.search-filter[group="type"][group-value] input:checked').parentElement.getAttribute('group-value') : 'query';

    var search_text = d.getElementById('search').value;

    // search_url += type + "/" + search_text;
    search_url += "query/" + search_text

    // 2. get filters
    // var filters = d.querySelectorAll('.search-filter[group]:not([group="type"])[group-value] input:checked');


    // for (var x = 0; x<filters.length; x++){
    //     var el = filters[x].parentElement;
    //   if(x===0) {
    //     search_url += "?";
    //   } else {
    //     search_url += "&";
    //   }
    //   search_url += el.getAttribute('group') + "=" + el.getAttribute('group-value');
    // }

    // if(page != 'undefined' && page > 1){
    //   search_url += (search_url.indexOf("?") != -1) ? "&" : "?";
    //   search_url += "start=" + (page * 10);
    // }

    // w.oldPopState = d.location.pathname;

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
