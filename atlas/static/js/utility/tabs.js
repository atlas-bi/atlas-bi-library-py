(function () {
  /*
     div.tabs
       ul
         li.is-active href=tab1
         li href=tab2
     div.tab-cnt
       div.tab-dta#tab1.tab-o
       div.tab-dta#tab2
     */

  var d = document;
  d.addEventListener(
    'click',
    function (e) {
      if (e.target.closest('.tabs')) {
        e.preventDefault();
        o(e.target.closest('li'));
      }
    },
    false,
  );
  d.addEventListener(
    'tab-open',
    function (e) {
      if (typeof e.detail !== 'undefined' && !!e.detail.el) {
        o(e.detail.el);
      }
    },
    false,
  );

  function o(el) {
    var l = [].slice.call(el.parentElement.querySelectorAll('li')),
      c = d.getElementById(el.getAttribute('href').replace('#', '')),
      t = [].slice.call(c.parentElement.children).filter(function (el) {
        return el.classList.contains('tab-dta');
      });

    [].forEach.call(t, function (s) {
      s.classList.remove('is-active');
    });

    [].forEach.call(l, function (s) {
      s.classList.remove('is-active');
    }); // open tab

    c.classList.add('is-active'); // add style to tab

    el.classList.add('is-active');
    d.dispatchEvent(new CustomEvent('tab-opened'));

    // change url hash. use pushstate not window.location.hash to prevent scrolling.
    if (history.pushState) {
      history.pushState(
        null,
        null,
        '#' + el.getAttribute('href').replace('#', ''),
      );
    }
  }

  // onload open tab that is url
  if (document.location.hash !== '' && document.location.hash !== null) {
    document.dispatchEvent(
      new CustomEvent('tab-open', {
        cancelable: true,
        detail: {
          el: document.querySelector(
            '.tab-lnk[href="' +
              document.location.hash.replace('#', '') +
              '"], .tab-lnk[href="' +
              document.location.hash +
              '"]',
          ),
        },
      }),
    );
  }
})();
