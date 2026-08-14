#!/usr/bin/env node
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const shim = fs.readFileSync('dockhand/rootfs/usr/share/dockhand-ha/ingress-shim.js', 'utf8');

class FakeLocation {
  constructor() {
    this.origin = 'https://ha.example.test';
    this.pathname = '/api/hassio_ingress/token/settings';
    this.search = '?tab=auth';
    this.replaced = null;
    this.assigned = null;
  }
  replace(url) {
    this.replaced = url;
  }
  assign(url) {
    this.assigned = url;
  }
}

function contextFor(fetchImpl) {
  const location = new FakeLocation();
  class FakeMutationObserver {
    observe() {}
  }
  const window = {
    location,
    URL,
    fetch: fetchImpl,
    MutationObserver: FakeMutationObserver
  };
  const document = {
    documentElement: {},
    querySelector(selector) {
      if (selector === 'base[href]') {
        return { getAttribute: () => '/api/hassio_ingress/token/' };
      }
      return null;
    },
    querySelectorAll() {
      return [];
    },
    addEventListener(_event, callback) {
      callback();
    }
  };
  const history = {
    pushState() {},
    replaceState() {}
  };
  return {
    window,
    document,
    history,
    Location: FakeLocation,
    XMLHttpRequest: function XMLHttpRequest() {},
    MutationObserver: FakeMutationObserver,
    EventSource: undefined,
    URL,
    console,
    setTimeout,
    clearTimeout
  };
}

contextFor.prototype = undefined;

async function tick() {
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
}

async function testAuthEnableRedirects() {
  const calls = [];
  const response = {
    ok: true,
    clone() {
      return { json: async () => ({ authEnabled: true }) };
    }
  };
  const ctx = contextFor(async (input, init) => {
    calls.push({ input, init });
    return response;
  });
  ctx.XMLHttpRequest.prototype = { open() {} };
  vm.createContext(ctx);
  vm.runInContext(shim, ctx);

  const result = await ctx.window.fetch('/api/auth/settings', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ authEnabled: true })
  });
  await tick();

  assert.equal(result, response);
  assert.equal(calls[0].input, '/api/hassio_ingress/token/api/auth/settings');
  assert.equal(
    ctx.window.location.replaced,
    '/api/hassio_ingress/token/login?redirect=%2Fsettings%3Ftab%3Dauth'
  );
}

async function testNoRedirectWhenAuthDisabled() {
  const response = {
    ok: true,
    clone() {
      return { json: async () => ({ authEnabled: false }) };
    }
  };
  const ctx = contextFor(async () => response);
  ctx.XMLHttpRequest.prototype = { open() {} };
  vm.createContext(ctx);
  vm.runInContext(shim, ctx);

  await ctx.window.fetch('/api/auth/settings', {
    method: 'PUT',
    body: JSON.stringify({ authEnabled: false })
  });
  await tick();

  assert.equal(ctx.window.location.replaced, null);
}

async function testNoRedirectOnFailedResponse() {
  const response = {
    ok: false,
    clone() {
      return { json: async () => ({ authEnabled: true }) };
    }
  };
  const ctx = contextFor(async () => response);
  ctx.XMLHttpRequest.prototype = { open() {} };
  vm.createContext(ctx);
  vm.runInContext(shim, ctx);

  await ctx.window.fetch('/api/auth/settings', {
    method: 'PUT',
    body: JSON.stringify({ authEnabled: true })
  });
  await tick();

  assert.equal(ctx.window.location.replaced, null);
}

async function testNormalFetchStillGetsIngressPrefix() {
  const calls = [];
  const response = { ok: true };
  const ctx = contextFor(async (input, init) => {
    calls.push({ input, init });
    return response;
  });
  ctx.XMLHttpRequest.prototype = { open() {} };
  vm.createContext(ctx);
  vm.runInContext(shim, ctx);

  await ctx.window.fetch('/api/containers', { method: 'GET' });

  assert.equal(calls[0].input, '/api/hassio_ingress/token/api/containers');
  assert.equal(ctx.window.location.replaced, null);
}

(async () => {
  await testAuthEnableRedirects();
  await testNoRedirectWhenAuthDisabled();
  await testNoRedirectOnFailedResponse();
  await testNormalFetchStillGetsIngressPrefix();
  console.log('ingress_shim_tests=ok');
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
