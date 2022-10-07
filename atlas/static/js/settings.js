(function () {
  let q;
  document.addEventListener('click', function (event) {
    if (event.target.matches('button.report-tags-etl-reset')) {
      q = new XMLHttpRequest();
      q.open('get', '/settings/etl/default', true);
      q.setRequestHeader('Content-Type', 'text/html;charset=UTF-8`');
      q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      q.setRequestHeader('X-CSRFToken', csrftoken);
      q.send();

      q.addEventListener('readystatechange', function () {
        if (this.readyState === 4 && this.status === 200) {
          document.querySelector('.report-tags-etl textarea').value =
            q.responseText;
        }
      });
    } else if (
      event.target.matches('.settings-search-visiblity[type="checkbox"]') &&
      event.target.tagName === 'INPUT'
    ) {
      const p = event.target.parentElement;
      const i = event.target;

      if (i.hasAttribute('checked')) {
        i.removeAttribute('checked');
      } else {
        i.setAttribute('checked', 'checked');
      }

      q = new XMLHttpRequest();
      q.open(
        'post',
        '/settings/search/visiblity/' +
          p.getAttribute('typeId') +
          '/' +
          (p.hasAttribute('groupId') ? p.getAttribute('groupId') : '1'),
        true,
      );
      q.setRequestHeader('Content-Type', 'text/html;charset=UTF-8`');
      q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      q.setRequestHeader('X-CSRFToken', csrftoken);
      q.send();

      q.addEventListener('readystatechange', function () {
        if (this.readyState === 4 && this.status === 200) {
          document.dispatchEvent(
            new CustomEvent('notification', {
              cancelable: true,
              detail: {
                value: 'Changes saved.',
                type: 'success',
              },
            }),
          );
        }
      });
    } else if (event.target.matches('a.settings-search-name')) {
      event.preventDefault();
      const input = event.target
        .closest('.field')
        .querySelector('input[groupId]');
      if (input === undefined) return !1;
      q = new XMLHttpRequest();
      q.open(
        'get',
        '/settings/search/report_type_name/' +
          input.getAttribute('groupId') +
          '?name=' +
          input.value,
        true,
      );
      q.setRequestHeader('Content-Type', 'text/html;charset=UTF-8`');
      q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      q.setRequestHeader('X-CSRFToken', csrftoken);
      q.send();

      q.addEventListener('readystatechange', function () {
        if (this.readyState === 4 && this.status === 200) {
          document.dispatchEvent(
            new CustomEvent('notification', {
              cancelable: true,
              detail: {
                value: 'Changes saved.',
                type: 'success',
              },
            }),
          );
        }
      });
    }
  });
})();
