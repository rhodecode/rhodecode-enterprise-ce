"""
rcextensions module.

"""


import os
import imp
import string
import functools

here = os.path.dirname(os.path.abspath(__file__))
registered_extensions = dict()

class DotDict(dict):

    def __contains__(self, k):
        try:
            return dict.__contains__(self, k) or hasattr(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        try:
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toDict(self):
        return unserialize(self)

    def __repr__(self):
        keys = list(self.iterkeys())
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)

    @staticmethod
    def fromDict(d):
        return serialize(d)


def serialize(x):
    if isinstance(x, dict):
        return DotDict((k, serialize(v)) for k, v in x.iteritems())
    elif isinstance(x, (list, tuple)):
        return type(x)(serialize(v) for v in x)
    else:
        return x


def unserialize(x):
    if isinstance(x, dict):
        return dict((k, unserialize(v)) for k, v in x.iteritems())
    elif isinstance(x, (list, tuple)):
        return type(x)(unserialize(v) for v in x)
    else:
        return x


def load_extension(filename, async=False):
    """
    use to load extensions inside rcextension folder.
    for example::

        callback = load_extension('email.py', async=False)
        if callback:
            callback('foobar')

    put file named email.py inside rcextensions folder to load it. Changing
    async=True will make the call of the plugin async, it's useful for
    blocking calls like sending an email or notification with APIs.
    """
    mod = ''.join(filename.split('.')[:-1])
    loaded = imp.load_source(mod, os.path.join(here, filename))

    callback = getattr(loaded, 'run', None)
    if not callback:
        raise Exception('Plugin missing `run` method')
    if async:
        # modify callback so it's actually an async call
        def _async_callback(*args, **kwargs):
            import threading
            thr = threading.Thread(target=callback, args=args, kwargs=kwargs)
            thr.start()
            if kwargs.get('_async_block'):
                del kwargs['_async_block']
                thr.join()

        return _async_callback
    return callback


def _verify_kwargs(expected_parameters, kwargs):
    """
    Verify that exactly `expected_parameters` are passed in as `kwargs`.
    """
    expected_parameters = set(expected_parameters)
    kwargs_keys = set(kwargs.keys())
    if kwargs_keys != expected_parameters:
        missing_kwargs = expected_parameters - kwargs_keys
        unexpected_kwargs = kwargs_keys - expected_parameters
        raise AssertionError(
            "Missing parameters: %r, unexpected parameters: %s" %
            (missing_kwargs, unexpected_kwargs))


def verify_kwargs(required_args):
    """
    decorator to verify extension calls arguments.

    :param required_args:
    """
    def wrap(func):
        def wrapper(*args, **kwargs):
            _verify_kwargs(required_args, kwargs)
            return func(*args, **kwargs)
        return wrapper
    return wrap


def register(name=None):
    def wrap(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # register load_extensions in kwargs, so we can chain plugins
            kwargs['_load_extension'] = load_extension
            # append this path for us to use added plugins or modules
            import sys
            _cur_path = os.path.dirname(os.path.abspath(__file__))
            if _cur_path not in sys.path:
                sys.path.append(_cur_path)

            registered_extensions[func.__name__] = func
            return func(*args, **kwargs)
        return wrapper
    return wrap

# =============================================================================
#  END OF UTILITY FUNCTIONS HERE
# =============================================================================

# Additional mappings that are not present in the pygments lexers
# used for building stats
# format is {'ext':['Names']} eg. {'py':['Python']} note: there can be
# more than one name for extension
# NOTE: that this will override any mappings in LANGUAGES_EXTENSIONS_MAP
# build by pygments
EXTRA_MAPPINGS = {}

# additional lexer definitions for custom files it's overrides pygments lexers,
# and uses defined name of lexer to colorize the files. Format is {'ext':
# 'lexer_name'} List of lexers can be printed running:
#   >> python -c "import pprint;from pygments import lexers;
#           pprint.pprint([(x[0], x[1]) for x in lexers.get_all_lexers()]);"

EXTRA_LEXERS = {}


CONFIG = DotDict(
    slack=DotDict(
        api_key='api-key',
        api_url='slack-incoming-hook-url',
        default_room='#slack-channel',
        default_plugin_config={},
    ),
    redmine=DotDict(
        api_key='api-key',
        default_tracker_url='https://redmine.tracker.url',
        default_project_id=None,
        default_status_resolved_id=3
    ),
)

# slack conf
CONFIG.slack.default_plugin_config = {
    'INCOMING_WEBHOOK_URL': CONFIG.slack.api_url,
    'SLACK_TOKEN': CONFIG.slack.api_key,
    'SLACK_ROOM': CONFIG.slack.default_room,
    'SLACK_FROM': 'RhodeCode',
    'SLACK_FROM_ICON_EMOJI': ':rhodecode:',
}

# redmine smart_pr configuration
def configure_redmine_smart_pr(issues, kwargs):
    kwargs['REDMINE_ISSUES'] = issues
    kwargs['redmine_tracker_url'] = kwargs.pop(
        'redmine_tracker_url', '') or CONFIG.redmine.default_tracker_url
    kwargs['redmine_api_key'] = kwargs.pop(
        'redmine_api_key', '') or CONFIG.redmine.api_key
    kwargs['redmine_project_id'] = kwargs.pop(
        'redmine_project_id', '') or CONFIG.redmine.default_project_id


@register('CREATE_REPO_HOOK')
@verify_kwargs(
    ['_load_extension', 'repo_name', 'repo_type', 'description', 'private',
     'created_on', 'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
     'clone_uri', 'fork_id', 'group_id', 'created_by'])
def _create_repo_hook(*args, **kwargs):
    """
    POST CREATE REPOSITORY HOOK. This function will be executed after
    each repository is created. kwargs available:

    :param repo_name:
    :param repo_type:
    :param description:
    :param private:
    :param created_on:
    :param enable_downloads:
    :param repo_id:
    :param user_id:
    :param enable_statistics:
    :param clone_uri:
    :param fork_id:
    :param group_id:
    :param created_by:
    """
    return 0
CREATE_REPO_HOOK = _create_repo_hook


@register('CREATE_REPO_GROUP_HOOK')
@verify_kwargs(
    ['_load_extension', 'group_name', 'group_parent_id', 'group_description',
     'group_id', 'user_id', 'created_by', 'created_on', 'enable_locking'])
def _create_repo_group_hook(*args, **kwargs):
    """
    POST CREATE REPOSITORY GROUP HOOK, this function will be
    executed after each repository group is created. kwargs available:

    :param group_name:
    :param group_parent_id:
    :param group_description:
    :param group_id:
    :param user_id:
    :param created_by:
    :param created_on:
    :param enable_locking:
    """
    return 0
CREATE_REPO_GROUP_HOOK = _create_repo_group_hook


@register('PRE_CREATE_USER_HOOK')
@verify_kwargs(
    ['_load_extension', 'username', 'password', 'email', 'firstname',
     'lastname', 'active', 'admin', 'created_by'])
def _pre_create_user_hook(*args, **kwargs):
    """
    PRE CREATE USER HOOK, this function will be executed before each
    user is created, it returns a tuple of bool, reason.
    If bool is False the user creation will be stopped and reason
    will be displayed to the user. kwargs available:

    :param username:
    :param password:
    :param email:
    :param firstname:
    :param lastname:
    :param active:
    :param admin:
    :param created_by:
    """

    reason = 'allowed'
    return True, reason
PRE_CREATE_USER_HOOK = _pre_create_user_hook


@register('CREATE_USER_HOOK')
@verify_kwargs(
    ['_load_extension', 'username', 'full_name_or_username', 'full_contact',
     'user_id', 'name', 'firstname', 'short_contact', 'admin', 'lastname',
     'ip_addresses', 'extern_type', 'extern_name', 'email', 'api_key',
     'api_keys', 'last_login', 'full_name', 'active', 'password', 'emails',
     'inherit_default_permissions', 'created_by', 'created_on'])
def _create_user_hook(*args, **kwargs):
    """
    POST CREATE USER HOOK, this function will be executed after each user is created
    kwargs available:

    :param username:
    :param full_name_or_username:
    :param full_contact:
    :param user_id:
    :param name:
    :param firstname:
    :param short_contact:
    :param admin:
    :param lastname:
    :param ip_addresses:
    :param extern_type:
    :param extern_name:
    :param email:
    :param api_key:
    :param api_keys:
    :param last_login:
    :param full_name:
    :param active:
    :param password:
    :param emails:
    :param inherit_default_permissions:
    :param created_by:
    :param created_on:
    """
    return 0
CREATE_USER_HOOK = _create_user_hook


@register('DELETE_REPO_HOOK')
@verify_kwargs(
    ['_load_extension', 'repo_name', 'repo_type', 'description', 'private',
     'created_on', 'enable_downloads', 'repo_id', 'user_id', 'enable_statistics',
     'clone_uri', 'fork_id', 'group_id', 'deleted_by', 'deleted_on'])
def _delete_repo_hook(*args, **kwargs):
    """
    POST DELETE REPOSITORY HOOK, this function will be executed after
    each repository deletion kwargs available:

    :param repo_name:
    :param repo_type:
    :param description:
    :param private:
    :param created_on:
    :param enable_downloads:
    :param repo_id:
    :param user_id:
    :param enable_statistics:
    :param clone_uri:
    :param fork_id:
    :param group_id:
    :param deleted_by:
    :param deleted_on:
    """
    return 0
DELETE_REPO_HOOK = _delete_repo_hook


@register('DELETE_USER_HOOK')
@verify_kwargs(
    ['_load_extension', 'username', 'full_name_or_username', 'full_contact',
     'user_id', 'name', 'firstname', 'short_contact', 'admin', 'lastname',
     'ip_addresses', 'email', 'api_key', 'last_login', 'full_name', 'active',
     'password', 'emails', 'inherit_default_permissions', 'deleted_by'
     ])
def _delete_user_hook(*args, **kwargs):
    """
    POST DELETE USER HOOK, this function will be executed after each
    user is deleted kwargs available:

    :param username:
    :param full_name_or_username:
    :param full_contact:
    :param user_id:
    :param name:
    :param firstname:
    :param short_contact:
    :param admin:
    :param lastname:
    :param ip_addresses:
    :param ldap_dn:
    :param email:
    :param api_key:
    :param last_login:
    :param full_name:
    :param active:
    :param password:
    :param emails:
    :param inherit_default_permissions:
    :param deleted_by:
    """
    return 0
DELETE_USER_HOOK = _delete_user_hook


@register('PRE_PUSH_HOOK')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username',
     'ip', 'action', 'repository', 'repo_store_path'])
def _pre_push_hook(*args, **kwargs):
    """
    Post push hook
    kwargs available:

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pushed
      :param ip: ip of who pushed
      :param action: push
      :param repository: repository name
      :param repo_store_path: full path to where repositories are stored
    """
    return 0
PRE_PUSH_HOOK = _pre_push_hook


@register('PUSH_HOOK')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username',
     'ip', 'action', 'repository', 'repo_store_path', 'pushed_revs'])
def _push_hook(*args, **kwargs):
    """
    POST PUSH HOOK, this function will be executed after each push it's
    executed after the build-in hook that RhodeCode uses for logging pushes
    kwargs available:

    :param server_url: url of instance that triggered this hook
    :param config: path to .ini config used
    :param scm: type of VS 'git' or 'hg'
    :param username: name of user who pushed
    :param ip: ip of who pushed
    :param action: push
    :param repository: repository name
    :param repo_store_path: full path to where repositories are stored
    :param pushed_revs: list of pushed commit ids
    """
    # backward compat
    kwargs['commit_ids'] = kwargs['pushed_revs']

    # fetch extra fields from repository
    call = load_extension('extra_fields.py')
    _extra_fields = {}
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']
            _extra_fields[key] = data['field_value']

    # fetch pushed commits, from commit_ids list
    call = load_extension('extract_commits.py')
    extracted_commits = {}
    if call:
        extracted_commits = call(**kwargs)
        # store the commits for the next call chain
    kwargs['COMMITS'] = extracted_commits

    # slack !
    call = load_extension('slack_push_notify.py')
    if call:
        kwargs.update(CONFIG.slack.default_plugin_config)
        call(**kwargs)

    # fetch redmine issues from given commits
    call = load_extension('extract_redmine_issues.py')
    issues = {}
    if call:
        issues = call(**kwargs)

    # redmine smart commits
    call = load_extension('redmine_smart_commits.py')
    if call:
        kwargs['REDMINE_ISSUES'] = issues

        kwargs['redmine_tracker_url'] = kwargs.pop(
            'redmine_tracker_url', '') or CONFIG.redmine.default_tracker_url
        kwargs['redmine_api_key'] = kwargs.pop(
            'redmine_api_key', '') or CONFIG.redmine.api_key
        kwargs['redmine_status_resolved_id'] = kwargs.pop(
            'redmine_status_resolved_id', '') or CONFIG.redmine.default_status_resolved_id
        kwargs['redmine_project_id'] = kwargs.pop(
            'redmine_project_id', '') or CONFIG.redmine.default_project_id
        call(**kwargs)

    return 0
PUSH_HOOK = _push_hook


@register('PRE_PULL_HOOK')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository'])
def _pre_pull_hook(*args, **kwargs):
    """
    Post pull hook
    kwargs available::

      :param server_url: url of instance that triggered this hook
      :param config: path to .ini config used
      :param scm: type of VS 'git' or 'hg'
      :param username: name of user who pulled
      :param ip: ip of who pulled
      :param action: pull
      :param repository: repository name
    """
    return 0
PRE_PULL_HOOK = _pre_pull_hook


@register('PULL_HOOK')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository'])
def _pull_hook(*args, **kwargs):
    """
    POST PULL HOOK, this function will be executed after each push it's
    executed after the build-in hook that RhodeCode uses for logging pulls

    kwargs available:

    :param server_url: url of instance that triggered this hook
    :param config: path to .ini config used
    :param scm: type of VS 'git' or 'hg'
    :param username: name of user who pulled
    :param ip: ip of who pulled
    :param action: pull
    :param repository: repository name
    """
    return 0
PULL_HOOK = _pull_hook


# =============================================================================
#  PULL REQUEST RELATED HOOKS
# =============================================================================
@register('CREATE_PULL_REQUEST')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository', 'pull_request_id', 'url', 'title', 'description',
     'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
     'mergeable', 'source', 'target', 'author', 'reviewers'])
def _create_pull_request_hook(*args, **kwargs):
    """

    """
    # extract extra fields and default reviewers from target
    kwargs['REPOSITORY'] = kwargs['target']['repository']

    call = load_extension('extra_fields.py')
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']

    call = load_extension('default_reviewers.py')
    if call:
        # read default_reviewers key propagated from extra fields
        kwargs['default_reviewers'] = map(string.strip, kwargs.pop(
            'default_reviewers', '').split(','))
        call(**kwargs)

    # extract below from source repo as commits are there
    kwargs['REPOSITORY'] = kwargs['source']['repository']

    # # fetch pushed commits, from commit_ids list
    # call = load_extension('extract_commits.py')
    # extracted_commits = {}
    # if call:
    #     extracted_commits = call(**kwargs)
    #     # store the commits for the next call chain
    # kwargs['COMMITS'] = extracted_commits
    #
    # # fetch issues from given commits
    # call = load_extension('extract_redmine_issues.py')
    # issues = {}
    # if call:
    #     issues = call(**kwargs)
    #
    # # redmine smart pr update
    # call = load_extension('redmine_pr_flow.py')
    # if call:
    #     # updates kwargs on the fly
    #     configure_redmine_smart_pr(issues=issues, kwargs=kwargs)
    #     call(**kwargs)
    #
    # # slack notification on merging PR
    # call = load_extension('slack_message.py')
    # if call:
    #     kwargs.update(CONFIG.slack.default_plugin_config)
    #     kwargs['SLACK_ROOM'] = '#develop'
    #     kwargs['SLACK_MESSAGE'] = 'Pull request <%s|#%s> (%s) was created.' % (
    #         kwargs.get('url'), kwargs.get('pull_request_id'), kwargs.get('title'))
    #
    #     call(**kwargs)

    return 0
CREATE_PULL_REQUEST = _create_pull_request_hook


@register('REVIEW_PULL_REQUEST')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository', 'pull_request_id', 'url', 'title', 'description',
     'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
     'mergeable', 'source', 'target', 'author', 'reviewers'])
def _review_pull_request_hook(*args, **kwargs):
    """

    """
    # extract extra fields and default reviewers from target
    kwargs['REPOSITORY'] = kwargs['target']['repository']

    # fetch extra fields
    call = load_extension('extra_fields.py')
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']

    # extract below from source repo as commits are there
    kwargs['REPOSITORY'] = kwargs['source']['repository']

    # fetch pushed commits, from commit_ids list
    call = load_extension('extract_commits.py')
    extracted_commits = {}
    if call:
        extracted_commits = call(**kwargs)
        # store the commits for the next call chain
    kwargs['COMMITS'] = extracted_commits

    # fetch issues from given commits
    call = load_extension('extract_redmine_issues.py')
    issues = {}
    if call:
        issues = call(**kwargs)

    # redmine smart pr update
    call = load_extension('redmine_pr_flow.py')
    if call:
        # updates kwargs on the fly
        configure_redmine_smart_pr(issues=issues, kwargs=kwargs)
        call(**kwargs)

    return 0
REVIEW_PULL_REQUEST = _review_pull_request_hook


@register('UPDATE_PULL_REQUEST')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository', 'pull_request_id', 'url', 'title', 'description',
     'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
     'mergeable', 'source', 'target', 'author', 'reviewers'])
def _update_pull_request_hook(*args, **kwargs):
    """

    """
    # extract extra fields and default reviewers from target
    kwargs['REPOSITORY'] = kwargs['target']['repository']

    # fetch extra fields
    call = load_extension('extra_fields.py')
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']

    # extract below from source repo as commits are there
    kwargs['REPOSITORY'] = kwargs['source']['repository']

    # fetch pushed commits, from commit_ids list
    call = load_extension('extract_commits.py')
    extracted_commits = {}
    if call:
        extracted_commits = call(**kwargs)
        # store the commits for the next call chain
    kwargs['COMMITS'] = extracted_commits

    # fetch issues from given commits
    call = load_extension('extract_redmine_issues.py')
    issues = {}
    if call:
        issues = call(**kwargs)

    # redmine smart pr updated
    call = load_extension('redmine_pr_flow.py')
    if call:
        # updates kwargs on the fly
        configure_redmine_smart_pr(issues=issues, kwargs=kwargs)
        call(**kwargs)

    return 0
UPDATE_PULL_REQUEST = _update_pull_request_hook


@register('MERGE_PULL_REQUEST')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository', 'pull_request_id', 'url', 'title', 'description',
     'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
     'mergeable', 'source', 'target', 'author', 'reviewers'])
def _merge_pull_request_hook(*args, **kwargs):
    """

    """
    # extract extra fields and default reviewers from target
    kwargs['REPOSITORY'] = kwargs['target']['repository']

    # fetch extra fields
    call = load_extension('extra_fields.py')
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']

    # extract below from source repo as commits are there
    kwargs['REPOSITORY'] = kwargs['source']['repository']

    # fetch pushed commits, from commit_ids list
    call = load_extension('extract_commits.py')
    extracted_commits = {}
    if call:
        extracted_commits = call(**kwargs)
        # store the commits for the next call chain
    kwargs['COMMITS'] = extracted_commits

    # fetch issues from given commits
    call = load_extension('extract_redmine_issues.py')
    issues = {}
    if call:
        issues = call(**kwargs)

    # redmine smart pr update
    call = load_extension('redmine_pr_flow.py')
    if call:
        # updates kwargs on the fly
        configure_redmine_smart_pr(issues=issues, kwargs=kwargs)
        call(**kwargs)

    # slack notification on merging PR
    call = load_extension('slack_message.py')
    if call:
        kwargs.update(CONFIG.slack.default_plugin_config)
        kwargs['SLACK_ROOM'] = '#develop'
        kwargs['SLACK_MESSAGE'] = 'Pull request <%s|#%s> (%s) was merged.' % (
            kwargs.get('url'), kwargs.get('pull_request_id'), kwargs.get('title'))
        call(**kwargs)

    return 0
MERGE_PULL_REQUEST = _merge_pull_request_hook


@register('CLOSE_PULL_REQUEST')
@verify_kwargs(
    ['_load_extension', 'server_url', 'config', 'scm', 'username', 'ip',
     'action', 'repository', 'pull_request_id', 'url', 'title', 'description',
     'status', 'created_on', 'updated_on', 'commit_ids', 'review_status',
     'mergeable', 'source', 'target', 'author', 'reviewers'])
def _close_pull_request_hook(*args, **kwargs):
    """

    """
    # extract extra fields and default reviewers from target
    kwargs['REPOSITORY'] = kwargs['target']['repository']

    # fetch extra fields
    call = load_extension('extra_fields.py')
    if call:
        repo_extra_fields = call(**kwargs)
        # now update if we have extra fields, they have precedence
        # this way users can store any configuration inside the database per
        # repo
        for key, data in repo_extra_fields.items():
            kwargs[key] = data['field_value']

    # extract below from source repo as commits are there
    kwargs['REPOSITORY'] = kwargs['source']['repository']

    # fetch pushed commits, from commit_ids list
    call = load_extension('extract_commits.py')
    extracted_commits = {}
    if call:
        extracted_commits = call(**kwargs)
        # store the commits for the next call chain
    kwargs['COMMITS'] = extracted_commits

    # fetch issues from given commits
    call = load_extension('extract_redmine_issues.py')
    issues = {}
    if call:
        issues = call(**kwargs)

    # redmine smart pr update
    call = load_extension('redmine_pr_flow.py')
    if call:
        # updates kwargs on the fly
        configure_redmine_smart_pr(issues=issues, kwargs=kwargs)
        call(**kwargs)

    return 0
CLOSE_PULL_REQUEST = _close_pull_request_hook
