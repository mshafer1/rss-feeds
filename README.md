# RSS Feeds

A GH-Pages repo of mirrored RSS feeds for programatic access.

## Why?

Well, I went to do a project and even though the website I was working from offered an RSS feed 
(for, you know, programmatic querying to determine if I should link to it), the headers on that feed
blocked cross-origin (i.e., cross-domain) access...

So, even though this website has a defined api for getting information, you are not allowed to
load it from within the browser on another website...

The "solution", seemed to be to setup a server that would pull that data (cache it to provide minimal load), 
and serve it up with the necessary headers ([attempt 1](https://github.com/mshafer1/caching-rss-proxy)); however, 
it is simpler and (should be) more secure to do the pulls / caching in a pipeline and let GH-Pages serve the resulting static content.
