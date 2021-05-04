(function () {
  var d = document;
  d.addEventListener("click", function (e) {
    var t = e.target,
      v = d.getElementsByTagName("video")[0],
      w = d.getElementsByClassName("video")[0];

    function post(url) {
      var q = new XMLHttpRequest();
      q.open("post", url, true);
      q.setRequestHeader("Content-Type", "text/html;charset=UTF-8`");
      q.setRequestHeader("X-Requested-With", "XMLHttpRequest");
      q.setRequestHeader("X-CSRFToken", csrftoken);
      q.send();
    }

    function on() {
      var s = w.getElementsByTagName("source")[0];

      if (s.hasAttribute("data-src")) {
        s.setAttribute("src", s.getAttribute("data-src"));
        s.removeAttribute("data-src");
        v.appendChild(s);
      }

      v.play();
      post("/user/preference/video/1");
    }

    function off() {
      w.classList.remove("video-large");
      w.classList.add("video-closed");
      v.pause();
      post("/user/preference/video/0");
    }

    if (t.closest(".video-open")) {
      w.classList.remove("video-closed");
      w.classList.add("video-large");
      on();
    } else if (t.closest(".video-min")) {
      w.classList.remove("video-large");
      w.classList.remove("video-closed");
      on();
    } else if (t.closest(".video-close")) {
      off();
    } else if (t.closest(".video")) {
      w.classList.remove("video-closed");
      on();
    } else {
      if (w) {
        w.classList.remove("video-large");
      }
    }
  });
})();
