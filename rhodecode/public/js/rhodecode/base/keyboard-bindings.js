// Global keyboard bindings

function setRCMouseBindings(repoName, repoLandingRev) {
    // general help "?"
    Mousetrap.bind(['?'], function(e) {
        $('#help_kb').modal({});
    });

    // / open the quick filter
    Mousetrap.bind(['/'], function(e) {
        $('#repo_switcher').select2('open');

        // return false to prevent default browser behavior
        // and stop event from bubbling
        return false;
    });

    // ctrl/command+b, show the the main bar
    Mousetrap.bind(['command+b', 'ctrl+b'], function(e) {
        var $headerInner = $('#header-inner'),
            $content = $('#content');
        if ($headerInner.hasClass('hover') && $content.hasClass('hover')) {
            $headerInner.removeClass('hover');
            $content.removeClass('hover');
        } else {
            $headerInner.addClass('hover');
            $content.addClass('hover');
        }
        return false;
    });

    // general nav g + action
    Mousetrap.bind(['g h'], function(e) {
        window.location = pyroutes.url('home');
    });
    Mousetrap.bind(['g g'], function(e) {
        window.location = pyroutes.url('gists', {'private': 1});
    });
    Mousetrap.bind(['g G'], function(e) {
        window.location = pyroutes.url('gists', {'public': 1});
    });
    Mousetrap.bind(['n g'], function(e) {
        window.location = pyroutes.url('new_gist');
    });
    Mousetrap.bind(['n r'], function(e) {
        window.location = pyroutes.url('new_repo');
    });

    if (repoName !== '' && repoLandingRev !== '') {
        // nav in repo context
        Mousetrap.bind(['g s'], function(e) {
            window.location = pyroutes.url(
                'summary_home', {'repo_name': repoName});
        });
        Mousetrap.bind(['g c'], function(e) {
            window.location = pyroutes.url(
                'changelog_home', {'repo_name': repoName});
        });
        Mousetrap.bind(['g F'], function(e) {
            window.location = pyroutes.url(
                'files_home',
                {
                    'repo_name': repoName,
                    'revision': repoLandingRev,
                    'f_path': '',
                    'search': '1'
                });
        });
        Mousetrap.bind(['g f'], function(e) {
            window.location = pyroutes.url(
                'files_home',
                {
                    'repo_name': repoName,
                    'revision': repoLandingRev,
                    'f_path': ''
                });
        });
        Mousetrap.bind(['g o'], function(e) {
            window.location = pyroutes.url(
                'edit_repo', {'repo_name': repoName});
        });
        Mousetrap.bind(['g O'], function(e) {
            window.location = pyroutes.url(
                'edit_repo_perms', {'repo_name': repoName});
        });
    }
}

setRCMouseBindings(templateContext.repo_name, templateContext.repo_landing_commit);
