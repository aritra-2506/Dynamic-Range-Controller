/*
 * Updated to use the function-based method described in http://www.phpied.com/social-button-bffs/
 * Better handling of scripts without supplied ids.
 *
 * N.B. Be sure to include Google Analytics's _gaq and Facebook's fbAsyncInit prior to this function.
 */

(function(d, u) {
    var s = d.scripts[0],
        i = u.length, g;
    while (i--) {
        g = d.createElement('script');
        g.src = '//' + u[i] + '.js';
        s.parentNode.insertBefore(g, s);
    }
}(document, [
    // Google Analytics
    'google-analytics.com/ga',
    // Google+ button
    'apis.google.com/js/plusone',
    // Facebook SDK
    'connect.facebook.net/en_US/all',
    // Twitter SDK
    'platform.twitter.com/widgets'
]));