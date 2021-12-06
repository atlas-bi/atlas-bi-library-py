

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
    .addEventListener("input",  instant_search.debounce(250));
  d.getElementById('search-form').addEventListener("submit", (e) => e.preventDefault());


  function instant_search(page){
    var t0 = performance.now();


  searchResultsContainer.textContent = "";

   var search_url = "/search/instant_search/";

     var search_text = d.getElementById('search').value;

    // search_url += type + "/" + search_text;
    search_url += "query/" + search_text;

    // mirror search url to advanced filters box
    d.getElementById('search').closest('form').querySelector('.control a.button').setAttribute('href', "/search/query/" + search_text);

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
