(function () {
  var params = new URLSearchParams(window.location.search);
  var isEmbed = params.has('embed') || window.self !== window.top;
  if (!isEmbed) return;

  document.documentElement.classList.add('is-embed');

  function sendHeight() {
    var height = Math.max(
      document.documentElement.scrollHeight,
      document.body ? document.body.scrollHeight : 0
    );
    window.parent.postMessage({ type: 'mapyo-resize', height: height }, '*');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendHeight);
  } else {
    sendHeight();
  }

  window.addEventListener('load', sendHeight);
  window.addEventListener('resize', sendHeight);

  if (window.ResizeObserver && document.body) {
    new ResizeObserver(sendHeight).observe(document.body);
  }
})();