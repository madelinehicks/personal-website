$(document).ready(function() {
	
	_.each($('a.tab-link'), function(e) {
		$(e).click(function(a) {
			a.preventDefault();
			$(this).tab('show');
		});
	});
	
	window.fbAsyncInit = function() {
		FB.init({
			appId      : '361149077274357',
			status     : true, 
			cookie     : true,
			xfbml      : true,
			oauth      : true,
		});
		FB.getLoginStatus(function(response) {
			console.log(response);
			if (response.status == "connected") {
				FB.api("/me", function (r) {
				    var b = $('#login-button');
					b.children()[0].innerText = "Logged in as " + r.name;
					b.addClass('friend');
					$.post('log/', r);
				});
			}
		});
		
        $('#login-button').click(function() { 
            FB.login(function(response) {
                if (response.authResponse) {
                    FB.api('/me', function(r) {
                        document.getElementById('login-button').children[0].innerText =
                            "Logged in as " + r.name;
                    });
                } else {
                  console.log('User cancelled login or did not fully authorize.');
                }
            }, {scope: 'email'})
        });
    }
});

jQuery(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
