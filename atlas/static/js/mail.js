(function () {
  const d = document;
  let sendMes = null;

  d.addEventListener(
    'submit',
    function (event) {
      if (event.target.closest('form.share')) {
        event.preventDefault();

        const form = event.target.closest('form.share');

        // To
        const to = [];
        const recp = form.querySelectorAll('.share-to input[type="hidden"]');

        if (recp !== null && recp.length > 0) {
          for (let x = 0; x < recp.length; x++) {
            const g = recp[x].classList.contains('group') ? 'g' : '';
            to.push({
              userId: recp[x].value,
              type: g,
            });
          }
        } else {
          const label = form
            .querySelector('.share-to')
            .parentElement.querySelector('label');
          if (label) {
            label.insertAdjacentHTML(
              'afterend',
              '<p class="help is-danger">Recipients are required.</p>',
            );
          }

          return false;
        }

        // Message
        const message = form.querySelector(
          'textarea[name="share-message"]',
        ).value;

        const data = {
          recipient: JSON.stringify(to),
          subject: form.querySelector('input.share-subject').value,
          message,
          text: message,
          share: 1,
          shareName: form.querySelector('input.share-name').value,
          shareUrl: form.querySelector('input.share-url').value,
        };

        sendMes = new XMLHttpRequest();
        sendMes.open('post', form.getAttribute('action'), true);
        sendMes.setRequestHeader(
          'Content-Type',
          'application/x-www-form-urlencoded; charset=UTF-8',
        );
        sendMes.setRequestHeader('X-CSRFToken', csrftoken);
        sendMes.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        sendMes.send(JSON.stringify(data));
        sendMes.addEventListener('load', function () {
          document.dispatchEvent(
            new CustomEvent('notification', {
              cancelable: true,
              detail: {
                value: sendMes.responseText,
              },
            }),
          );
        });

        // Close modal if its open
        d.dispatchEvent(new CustomEvent('modal-close'));
      }
    },
    false,
  );
})();
