grecaptcha.ready(function() {
  grecaptcha.execute('6LfkYW0eAAAAAExou1PUJwUC6XT7nv1ecjk_x-hl', {action: "/register/"}).then(function(token) {
    document.getElementById('g-recaptcha-response').value = token;
  });
});