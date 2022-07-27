/*
    Atlas of Information Management business intelligence library and documentation database.
    Copyright (C) 2020  Riverside Healthcare, Kankakee, IL

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

(function () {
  var d = document; // adding favorites

  d.addEventListener(
    'click',
    function (e) {
      if (
        e.target.closest('.favorite:not(.disabled)') ||
        e.target.closest('.favorite-search:not(.disabled)') ||
        e.target.closest('.fav-star:not(.disabled)') ||
        e.target.closest('[fav-type]')
      ) {
        e.preventDefault();
        e.stopPropagation();
        var t = e.target.closest('.favorite-search:not(.disabled)')
            ? e.target.getElementsByTagName('i')[0]
            : e.target,
          x,
          el,
          q,
          data,
          url,
          inFavBox = t.closest('.favs') == null ? false : true,
          hasFavBox =
            document.getElementsByClassName('favs')[0] == null ? false : true,
          actionType = 1,
          favoriteType = t.getAttribute('fav-type'),
          objectId = t.getAttribute('object-id'),
          objectName = t.getAttribute('object-name'),
          l = d.querySelectorAll(
            '[fav-type="' + favoriteType + '"][object-id="' + objectId + '"]',
          );

        for (x = 0; x < l.length; x++) {
          el = l[x];

          if (el.classList.contains('favorite')) {
            el.classList.remove('favorite');
            actionType = 0;
          } else {
            el.classList.add('favorite');
          }
        }

        if (inFavBox) {
          if (d.querySelectorAll('.favs div[folder-id]').length <= 1) {
            el = d.getElementById('favs-none');
            el.style.opacity = 0;
            el.style.removeProperty('display');
            el.style.transition = 'opacity 0.3s ease-in-out';
            var a = el.offsetHeight; // clear css cache

            el.style.opacity = 1;
          }

          for (x = 0; x < l.length; x++) {
            el = l[x].closest('.fav');
            el.parentElement.removeChild(el);
          }
        }

        data = {
          actionType: actionType,
          favoriteType: favoriteType,
          objectId: objectId,
          objectName: objectName,
        };
        url = Object.keys(data)
          .map(function (k) {
            return encodeURIComponent(k) + '=' + encodeURIComponent(data[k]);
          })
          .join('&');
        q = new XMLHttpRequest();
        q.open('post', '/users?handler=EditFavorites&' + url, true);
        q.setRequestHeader(
          'Content-Type',
          'application/x-www-form-urlencoded; charset=UTF-8',
        );
        q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        q.send();

        q.onload = function () {
          if (hasFavBox) {
            d.dispatchEvent(new CustomEvent('reload-favs'));
          }
        };
      }
    },
    false,
  );

  d.addEventListener('click', function (e) {
    if (e.target.closest('.fav-show-all')) {
      showall();
    } else if (e.target.closest('.fav-folder-new')) {
      return false;
    } else if (e.target.closest('.fav-folder')) {
      if (e.target.classList.contains('active')) {
        showall();
      } else {
        showall(e.target.closest('.fav-folder'));
      }
    }
  });

  /**
   *
   */
  function showall(me) {
    var t = me || d.getElementsByClassName('fav-show-all')[0],
      i,
      x,
      el,
      sel,
      si,
      y,
      a,
      folderId = t.getAttribute('folder-id'),
      nr = d.getElementById('favs-none');
    nr.style.display = 'none';
    i = t.parentElement.getElementsByClassName('active');

    for (x = 0; x < i.length; x++) {
      el = i[x];
      el.classList.remove('active');
      si = el.getElementsByTagName('i')[0];
      si.classList.remove('fa-folder-open');
      si.classList.add('fa-folder');
    }

    if (folderId !== null) {
      i = d.querySelectorAll(
        '.favs div[folder-id]:not([folder-id="' + folderId + '"])',
      );

      for (x = 0; x < i.length; x++) {
        el = i[x];
        el.style.display = 'none';
      }

      i = d.querySelectorAll('.favs div[folder-id="' + folderId + '"]');
    } else {
      i = d.querySelectorAll('.favs div[folder-id]');
    }

    for (x = 0; x < i.length; x++) {
      el = i[x];
      el.style.opacity = 0;
      el.style.removeProperty('display');
      el.style.transition = 'opacity 0.1s ease-in-out';
      a = el.offsetHeight; // clear css cache

      el.style.opacity = 1;
    }

    t.classList.add('active');
    i = t.getElementsByTagName('i')[0];
    i.classList.remove('fa-folder');
    i.classList.add('fa-folder-open'); // check if there  0 items showing and give a message

    if (
      (folderId !== null &&
        d.querySelectorAll('.favs div[folder-id="' + folderId + '"]').length ==
          0) ||
      (folderId == null &&
        d.querySelectorAll('.favs div[folder-id]').length == 0)
    ) {
      i = nr.childNodes;

      for (x = 0; x < i.length; x++) {
        el = i[x];
        el.style.removeProperty('display');
      }

      nr.style.opacity = 0;
      nr.style.removeProperty('display');
      nr.style.transition = 'opacity 0.1s ease-in-out';
      a = nr.offsetHeight; // clear css cache

      nr.style.opacity = 1;
      d.querySelector(
        '#DeleteFolderForm input[name="folder_id"]',
      ).value = folderId;
    }
  }

  d.addEventListener(
    'submit',
    function (e) {
      var q, url;

      if (e.target.closest('#CreateFolderForm')) {
        e.preventDefault();
        var name = e.target.getElementsByTagName('input')[0].value;

        q = new XMLHttpRequest();
        q.open('post', e.target.getAttribute('action'), true);
        q.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
        q.setRequestHeader('X-CSRFToken', csrftoken);
        q.send(JSON.stringify({ folder_name: name }));
        q.onload = function () {
          var div = d.createElement('div');
          div.classList.add('fav-folder');
          div.classList.add('drg');

          if ('folder_id' in JSON.parse(q.responseText)) {
            div.setAttribute('folder-id', JSON.parse(q.responseText).folder_id);
            div.innerHTML =
              '<i class="fas fa-folder"></i><span>' +
              name +
              '</span><div class="fav-count">0</div><div class="folder-grip drg-hdl"><i class="fas fa-grip-lines"></i></div>';
            var nf = d
              .getElementById('fav-folders')
              .getElementsByClassName('fav-folder-new')[0];
            nf.parentElement.insertBefore(div, nf);
          } else {
            alert(JSON.parse(q.responseText).error);
          }

          e.target.getElementsByTagName('span')[0].innerHTML = '';
          document.dispatchEvent(
            new CustomEvent('clps-close', {
              cancelable: true,
              detail: {
                el: d.getElementById('fav-folder-new'),
              },
            }),
          );
        };
      } else if (e.target.closest('#DeleteFolderForm')) {
        e.preventDefault();
        var folderId = e.target
          .closest('#DeleteFolderForm')
          .querySelector('[name="folder_id"]').value;

        q = new XMLHttpRequest();
        q.open('post', e.target.getAttribute('action'), true);
        q.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
        q.setRequestHeader('X-CSRFToken', csrftoken);
        q.send(JSON.stringify({ folder_id: folderId }));

        q.onload = function () {
          var m = d
            .getElementById('fav-folders')
            .querySelector("div[folder-id][folder-id='" + folderId + "']");
          m.parentElement.removeChild(m);
          showall();
        };
      }
    },
    false,
  );
  d.addEventListener(
    'dragEnd',
    function (e) {
      if (typeof e.detail !== 'undefined') {
        Reorder(e.detail.el, e.detail.x, e.detail.y);
      }
    },
    false,
  );

  /**
   *
   */
  function Reorder(el, x, y) {
    var e, r, i, l, f;

    if (el.classList.contains('fav-folder')) {
      e = el.parentElement.querySelectorAll(
        '.fav-folder:not(.fav-folder-new):not(.fav-show-all',
      );
      r = Array.from(e).sort(function (a, b) {
        return getOffset(a).top - getOffset(b).top;
      });
      var nf = el.parentElement.getElementsByClassName('fav-folder-new')[0];

      for (i = 0; i < r.length; i++) {
        nf.parentElement.insertBefore(r[i], nf);
      }

      UpdateFolderRank();
    } else if (el.classList.contains('fav')) {
      e = getHoveredFolder(el, x, y);

      if (e && e !== null) {
        f = !e.hasAttribute('folder-id') ? 0 : e.getAttribute('folder-id');
        UpdateFavFolder(el.getAttribute('fav-id'), e.getAttribute('folder-id'));
        el.setAttribute('folder-id', e.getAttribute('folder-id'));
        showall(d.querySelector('.fav-folder.active'));
      } else {
        e = el.parentElement.getElementsByClassName('fav');
        r = Array.from(e).sort(function (a, b) {
          return getOffset(a).top - getOffset(b).top;
        });

        for (i = 0; i < r.length; i++) {
          el.parentElement.appendChild(r[i]);
        }

        UpdateFavRank();
      }
    }

    el.style.transition = 'top 0.3s; left 0.3s;';
    el.style.top = 0;
    el.style.left = 0; // remove hover class from folders

    i = d.querySelectorAll('#fav-folders .fav-folder:not(.fav-folder-new)');

    for (l = 0; l < i.length; l++) {
      i[l].classList.remove('hover');
    }
  }

  d.addEventListener(
    'dragMove',
    function (e) {
      if (typeof e.detail !== 'undefined') {
        var i = d.querySelectorAll(
            '#fav-folders .fav-folder:not(.fav-folder-new)',
          ),
          l,
          el;

        for (l = 0; l < i.length; l++) {
          i[l].classList.remove('hover');
        }

        el = getHoveredFolder(e.detail.el, e.detail.x, e.detail.y);

        if (el && el !== null) {
          el.classList.add('hover');
        }
      }
    },
    false,
  );

  /**
   *
   */
  function getHoveredFolder(el, x, y) {
    if (el.classList.contains('fav')) {
      var i = d.querySelectorAll(
          '#fav-folders .fav-folder:not(.fav-folder-new)',
        ),
        l,
        g,
        o,
        top,
        bottom,
        left,
        right,
        q = window.event;

      for (l = 0; l < i.length; l++) {
        g = i[l];
        o = getOffset(g);
        top = o.top;
        bottom = o.top + g.offsetHeight;
        left = o.left;
        right = o.left + g.offsetWidth;

        if (y > top && y < bottom && x > left && x < right) {
          return g;
        }
      }

      return false;
    }
  }

  /**
   *
   */
  function UpdateFolderRank() {
    var array = [],
      g,
      s = d.querySelectorAll('#fav-folders .fav-folder:not(.drag-source)'),
      q;

    for (g = 0; g < s.length; g++) {
      if (s[g].hasAttribute('folder-id')) {
        var item = {};
        item.folder_id = s[g].getAttribute('folder-id');
        item.folder_rank = g + 1;
        array.push(item);
      }
    }

    q = new XMLHttpRequest();
    q.open('post', '/users/favorites_reorder_folder', true);
    q.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    q.setRequestHeader('X-CSRFToken', csrftoken);
    q.send(JSON.stringify(array));
  }

  /**
   *
   */
  function UpdateFavRank() {
    var array = [],
      g,
      s = d.querySelectorAll('.favs div[folder-id]:not(.drag-source)'),
      q;

    for (g = 0; g < s.length; g++) {
      if (s[g].hasAttribute('folder-id')) {
        var item = {};
        item.favorite_id = s[g].getAttribute('fav-id');
        item.favorite_rank = g + 1;
        array.push(item);
      }
    }

    q = new XMLHttpRequest();
    q.open('post', '/users/favorites_reorder', true);
    q.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    q.setRequestHeader('X-CSRFToken', csrftoken);
    q.send(JSON.stringify(array));
  }

  /**
   *
   */
  function UpdateFavFolder(FavoriteId, FolderId) {
    var item = {},
      q;
    item.favorite_id = FavoriteId;
    item.folder_id = FolderId;
    q = new XMLHttpRequest();
    q.open('post', '/users/favorites_change_folder', true);
    q.setRequestHeader('Content-Type', 'application/json; charset=utf-8');
    q.setRequestHeader('X-CSRFToken', csrftoken);
    q.send(JSON.stringify(item));
    q.onload = function () {
      // update folder counts
      UpdateFavCounts(q.responseText);
    };
  }

  /**
   *
   */
  function UpdateFavCounts(data) {
    // data should be folder_id: count, with one record
    // beign a total count of folder_id=all.
    data = JSON.parse(data);

    for (var x = 0; x < data.length; x++) {
      if (data[x].folder_id == 'all') {
        document.querySelector(
          '.favs-colOne .fav-folder.fav-show-all .fav-count',
        ).innerHTML = data[x].count;
      } else {
        document.querySelector(
          '.favs-colOne .fav-folder[folder-id="' +
            data[x].folder_id +
            '"] .fav-count',
        ).innerHTML = data[x].count;
      }
    }
  }
})();
