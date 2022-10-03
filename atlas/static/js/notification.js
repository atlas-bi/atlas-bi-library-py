(function () {
  function addNotification(message, type) {
    const d = document;
    const notificationWrapper = d.querySelectorAll(
      '.fixed-notification-wrapper',
    )[0];

    const notification = document.createElement('div');
    notification.classList.add('notification', 'py-2');
    if (type === 'error') {
      notification.classList.add('is-danger');
    } else if (type === 'warning') {
      notification.classList.add('is-warning');
    } else {
      notification.classList.add('is-info');
    }

    const button = document.createElement('button');
    button.classList.add('delete');

    notification.append(button);
    notification.insertAdjacentHTML('beforeend', DOMPurify.sanitize(message));
    notificationWrapper.prepend(notification);

    setTimeout(function () {
      notification.remove();
    }, 4000);

    button.addEventListener('mouseup', () => {
      notification.remove();
    });
  }

  document.addEventListener(
    'notification',
    function (event) {
      if (
        typeof event.detail !== 'undefined' &&
        Boolean(event.detail) &&
        Boolean(event.detail.value)
      ) {
        addNotification(event.detail.value, event.detail.type);
      }
    },
    false,
  );
})();
