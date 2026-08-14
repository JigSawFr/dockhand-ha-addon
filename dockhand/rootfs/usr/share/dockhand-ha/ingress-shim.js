(function () {
  var base = document.querySelector('base[href]');
  if (!base) return;

  var href = base.getAttribute('href') || '';
  var prefix = href.endsWith('/') ? href.slice(0, -1) : href;
  if (!prefix) return;

  var origin = window.location.origin;

  function fix(url) {
    if (typeof url !== 'string') return url;
    if (url[0] === '/' && url.slice(0, 2) !== '//' && !url.startsWith(prefix + '/') && url !== prefix) {
      return prefix + url;
    }
    if (url.startsWith(origin + '/') && !url.startsWith(origin + prefix + '/') && url !== origin + prefix) {
      return origin + prefix + url.slice(origin.length);
    }
    return url;
  }

  function stripPrefix(path) {
    if (typeof path !== 'string') return '/';
    if (path === prefix) return '/';
    if (path.startsWith(prefix + '/')) return path.slice(prefix.length) || '/';
    return path || '/';
  }

  function pathOf(url) {
    try {
      return stripPrefix(new NativeURL(fix(url), origin).pathname);
    } catch (_) {
      return '';
    }
  }

  function requestBodyEnablesAuth(init) {
    if (!init || typeof init.body !== 'string') return false;
    try {
      var body = JSON.parse(init.body);
      return body && body.authEnabled === true;
    } catch (_) {
      return false;
    }
  }

  function maybeRedirectAfterAuthEnabled(response) {
    if (!response || !response.ok || !response.clone) return;
    response.clone().json().then(function (body) {
      if (!body || body.authEnabled !== true || stripPrefix(window.location.pathname) === '/login') return;
      var target = stripPrefix(window.location.pathname + window.location.search);
      window.location.replace(fix('/login?redirect=' + encodeURIComponent(target || '/')));
    }).catch(function () {});
  }

  var NativeURL = window.URL;
  function IngressURL(input, baseUrl) {
    if (typeof input === 'string') input = fix(input);
    if (typeof baseUrl === 'string') baseUrl = fix(baseUrl);
    return new NativeURL(input, baseUrl);
  }
  IngressURL.prototype = NativeURL.prototype;
  try { Object.setPrototypeOf(IngressURL, NativeURL); } catch (_) {}
  window.URL = IngressURL;

  var nativeFetch = window.fetch;
  if (nativeFetch) {
    window.fetch = function (input, init) {
      var shouldRedirectAfterAuth = typeof input === 'string'
        && (init && String(init.method || 'GET').toUpperCase()) === 'PUT'
        && pathOf(input) === '/api/auth/settings'
        && requestBodyEnablesAuth(init);
      if (typeof input === 'string') input = fix(input);
      var request = nativeFetch.call(this, input, init);
      if (shouldRedirectAfterAuth && request && request.then) {
        return request.then(function (response) {
          maybeRedirectAfterAuthEnabled(response);
          return response;
        });
      }
      return request;
    };
  }

  var nativeOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url) {
    if (typeof url === 'string') url = fix(url);
    return nativeOpen.apply(this, [method, url].concat(Array.prototype.slice.call(arguments, 2)));
  };

  var NativeEventSource = window.EventSource;
  if (NativeEventSource) {
    window.EventSource = function (url, config) {
      if (typeof url === 'string') url = fix(url);
      return new NativeEventSource(url, config);
    };
  }

  var pushState = history.pushState;
  history.pushState = function (state, title, url) {
    if (typeof url === 'string') url = fix(url);
    return pushState.call(this, state, title, url);
  };

  var replaceState = history.replaceState;
  history.replaceState = function (state, title, url) {
    if (typeof url === 'string') url = fix(url);
    return replaceState.call(this, state, title, url);
  };

  var locationAssign = Location.prototype.assign;
  if (locationAssign) {
    Location.prototype.assign = function (url) {
      if (typeof url === 'string') url = fix(url);
      return locationAssign.call(this, url);
    };
  }

  var locationReplace = Location.prototype.replace;
  if (locationReplace) {
    Location.prototype.replace = function (url) {
      if (typeof url === 'string') url = fix(url);
      return locationReplace.call(this, url);
    };
  }

  function fixElement(element) {
    if (!element || element.nodeType !== 1) return;
    ['src', 'href', 'action'].forEach(function (attr) {
      var value = element.getAttribute && element.getAttribute(attr);
      if (value && typeof value === 'string') {
        var next = fix(value);
        if (next !== value) element.setAttribute(attr, next);
      }
    });
    if (element.querySelectorAll) {
      element.querySelectorAll('[src],[href],[action]').forEach(fixElement);
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    Object.keys(window).forEach(function (key) {
      if (/^__sveltekit/.test(key) && window[key] && typeof window[key].base === 'string') {
        Object.defineProperty(window[key], 'base', {
          get: function () { return prefix; },
          configurable: true
        });
      }
    });
    document.querySelectorAll('[src],[href],[action]').forEach(fixElement);
  });

  if (window.MutationObserver) {
    new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (mutation.addedNodes) Array.prototype.forEach.call(mutation.addedNodes, fixElement);
        if (mutation.target) fixElement(mutation.target);
      });
    }).observe(document.documentElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['src', 'href', 'action']
    });
  }
})();
