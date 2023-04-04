(function () {
  document
    .querySelector('#enable_share_notification')
    .addEventListener('change', () => {
      const q = new XMLHttpRequest();
      q.open('get', '/users/settings/toggle?setting=share_notification', true);
      q.setRequestHeader(
        'Content-Type',
        'application/x-www-form-urlencoded; charset=UTF-8',
      );
      q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      q.setRequestHeader('X-CSRFToken', csrftoken);
      q.send();
    });
})();
