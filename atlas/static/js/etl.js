// https://stackoverflow.com/a/10834843/10265880
/**
 *
 */
function isNormalInteger(string_) {
  return /^\+?(0|[1-9]\d*)$/.test(string_);
}

/**
 *
 */
function isJson(string_) {
  try {
    return JSON.parse(string_);
  } catch {
    return false;
  }
}

/**
 *
 */
function getAjax(element) {
  const q = new XMLHttpRequest();
  q.open('get', element.getAttribute('data-ajax'), true);
  q.setRequestHeader(
    'Content-Type',
    'application/x-www-form-urlencoded; charset=UTF-8',
  );
  q.setRequestHeader('X-CSRFToken', csrftoken);
  q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
  q.send();

  q.addEventListener('readystatechange', function () {
    if (q.readyState === 4 && q.status === 200) {
      const data = isJson(q.responseText);

      if (!data) {
        element.innerHTML = q.responseText;
      } else {
        element.innerHTML = data.message;

        // Set color or text based on status
        if (data.hasOwnProperty('status')) {
          element.setAttribute('data-color', data.status);
        } else {
          element.removeAttribute('data-color');
        }
      }

      if (
        element.hasAttribute('data-toggle') &&
        document.querySelector(
          '.field input#' + element.getAttribute('data-toggle'),
        )
      ) {
        const checkbox = document.querySelector(
          '.field input#' + element.getAttribute('data-toggle'),
        );
        if (data.active === true) {
          checkbox.setAttribute('checked', 'checked');
        } else {
          checkbox.removeAttribute('checked');
        }
      }

      // Enable periodic update
      if (
        element.hasAttribute('data-freq') &&
        isNormalInteger(element.getAttribute('data-freq'))
      ) {
        setTimeout(
          getAjax.bind(this, element),
          element.getAttribute('data-freq') * 1000,
        );
      }
    }
  });
}

/**
 * Function for loading all ajax content on page.
 * can be called for force refresh of all, otherwise
 * it will run when page loads.
 */
function loadAjax() {
  const ajax = document.querySelectorAll('*[data-ajax]');

  Array.prototype.forEach.call(ajax, function (event) {
    getAjax(event);
  });
}

loadAjax();

document.addEventListener('something_changed', function () {
  loadAjax();
});

document.addEventListener('click', function (event) {
  if (event.target.matches('input.switch[data-url')) {
    const STATUS = { true: 'enable', false: 'disable' };

    const q = new XMLHttpRequest();
    q.open(
      'get',
      event.target.getAttribute('data-url') + STATUS[event.target.checked],
      true,
    );
    q.setRequestHeader('X-CSRFToken', csrftoken);
    q.setRequestHeader(
      'Content-Type',
      'application/x-www-form-urlencoded; charset=UTF-8',
    );
    q.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    q.send();

    document.dispatchEvent(new CustomEvent('something_changed'));
  }
});
